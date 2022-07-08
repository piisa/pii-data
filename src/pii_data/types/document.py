"""
The SrcDocument object holding document data.

A base abstract class is provided, subclasses need to implement at least the
get_chunks() method, producing an iterable of chunks.
"""


from collections import namedtuple, defaultdict
from types import MappingProxyType
import uuid

from typing import Dict, Iterable, Tuple

from ..helper.exception import UnimplementedException


# The contents of a document chunk:
#  - a chunk id
#  - the text content
#  - a context for the chunk (optional)
DocumentChunk = namedtuple("DocumentChunk", "id data context", defaults=[None])



class SrcDocument:
    """
    An abstract base object to hold the data for a document to be processed.
    Child classes need to provide at least a get_chunks method
    """

    def __init__(self, document_info: Dict = None,
                 add_chunk_context: bool = False):
        """
          :param document_info: document general information
          :param add_chunk_context: add context information when iterating over
           chunks
        """
        self._do_ctx = add_chunk_context
        self._chunk_id = 0
        self._meta = defaultdict(dict)
        self.set_header_document(document_info)


    def __repr__(self) -> str:
        return f"<SrcDocument {self._meta['document']['id']}>"


    @property
    def header(self):
        """
        Return a read-only representation of the full document header
        """
        return MappingProxyType(self._meta)


    @property
    def id(self):
        """
        Return the document id
        """
        return self._meta["document"].get("id")


    def set_id(self, id: str):
        """
        Set the document identifier inside the document metadata
        """
        self._meta["document"]["id"] = id


    def set_header_document(self, document_info: Dict = None):
        """
        Set the data for the document-level info (part of the document
        metadata)
        If not present, a document id is automatically added as a random UUID
        """
        glb = document_info or {}
        if "id" not in glb:
            glb["id"] = str(uuid.uuid4())
        self._meta["document"] = glb


    def add_metadata(self, **kwargs):
        """
        Update the document metadata elements, adding all passed arguments
        (which should be dictionaries)
        """
        for k, v in kwargs.items():
            self._meta[k].update(v)


    def _chunk(self, before: Tuple, current: Tuple, after: Tuple) -> Dict:
        """
        Create a chunk object, with context
        """
        ctx = self._ctx.copy()
        if before:
            ctx["before"] = before[1]
        if after:
            ctx["after"] = after[1]
        data = *current, ctx
        return DocumentChunk(*data)


    def iter_chunks(self, add_context: bool = None) -> Iterable[Dict]:
        """
        Iterator method, with additional options
        Produce an iterable over document chunks, with or without context
        (depending on the object config, or on the passed extra argument).

        Calls the get_chunks() method, to be implemented by subclasses.
        """
        before = current = None
        if add_context is None:
            add_context = self._do_ctx
        if add_context:
            self._ctx = {k: MappingProxyType(v) for k, v in self._meta.items()}

        for data in self.get_chunks():

            # Get chunk_id and payload
            chunk_id = None
            if isinstance(data, dict) and "data" in data:
                chunk_id = data.get("id")
                data = data["data"]
            if chunk_id is None:
                self._chunk_id += 1
                chunk_id = self._chunk_id
            data = (str(chunk_id), data)

            # Render without context
            if not add_context:
                yield DocumentChunk(*data)
                continue

            # Render with context: track the chunks before & after
            if before is None:
                before = data
            elif current is None:
                yield self._chunk(None, before, data)
                current = data
            else:
                yield self._chunk(before, current, data)
                before = current
                current = data

        # Last chunk?
        if add_context:
            if current:
                yield self._chunk(before, current, None)
            elif before:
                yield self._chunk(None, before, None)


    def __iter__(self) -> Iterable[Dict]:
        return self.iter_chunks()


    def get_chunks(self) -> Iterable[DocumentChunk]:
        raise UnimplementedException("abstract class")


# --------------------------------------------------------------------------


class TreeSrcDocument(SrcDocument):
    """
    A tree document, as an abstract class.
    Subclasses need to implement the top_chunks() method, which gives an
    iterable over just the document top-level chunks
    """

    def _yield_chunks(self, chunk: Dict) -> Iterable[DocumentChunk]:
        """
        Return a sequence of chunks from an element in the document tree
        """
        # This chunk
        text = chunk.get("data")
        if text:
            yield text
        # Child chunks
        for subchunk in chunk.get("chunks", []):
            yield from self._yield_chunks(subchunk)


    def get_chunks(self) -> Iterable[str]:
        """
        Return all chunks from the document tree, traversing it deep-first
        Requires a top_chunks() method
        """
        for chunk in self.top_chunks():
            yield from self._yield_chunks(chunk)


    def top_chunks(self) -> Iterable[Dict]:
        raise UnimplementedException("abstract class")



class TabularSrcDocument(SrcDocument):
    pass
