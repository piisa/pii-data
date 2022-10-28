"""
The SrcDocument object holding document data.

A base abstract class is provided, subclasses need to implement at least the
get_chunks() method, producing an iterable of chunks.
"""

from collections import defaultdict
from types import MappingProxyType
import uuid

from typing import Dict, Iterable, Callable, Iterator

from ..helper.exception import UnimplementedException
from .chunker import DocumentChunk, ChunkGenerator, ContextChunkGenerator

TYPE_META = Dict[str, Dict]



class SrcDocument:
    """
    An abstract base object to hold the data for a document to be processed.
    Child classes need to provide at least a get_chunks method
    """

    def __init__(self, metadata: TYPE_META = None, iter_options: Dict = None):
        """
          :param metadata: document general metadata (e.g. "document" &
            "dataset" dictionaries)
          :param iter_options: set iteration options
        """
        self._iter_options = iter_options or {}
        self._chunk_id = 0
        self._meta = defaultdict(dict)
        self.set_id()
        if metadata:
            self.add_metadata(**metadata)


    def __repr__(self) -> str:
        return f"<SrcDocument {self._meta['document']['id']}>"


    @property
    def metadata(self):
        """
        Return a read-only representation of the full document metadata
        """
        return MappingProxyType(self._meta)


    @property
    def id(self):
        """
        Return the document id
        """
        return self._meta["document"].get("id")


    def set_id(self, id: str = None):
        """
        Set the document identifier inside the document metadata
        If an id is nor passed, a random UUID will be used.
        """
        self._meta["document"]["id"] = id or str(uuid.uuid4())


    def add_metadata(self, **metadata):
        """
        Update the document metadata elements, adding all passed arguments
        (which should be dictionaries)
        """
        for k, v in metadata.items():
            self._meta[k].update(v)


    def __iter__(self) -> Iterable[Dict]:
        """
        Standard full iterator
        """
        return self.iter_full()


    def iter_full(self, context: bool = None,
                  chunk_iterator: Callable = None) -> Iterable[Dict]:
        """
        Iterate over the document, producing a sequence of individual
        DocumentChunk objects
         :param context: add additional context information to each chunk (this
           modifies the default option in the object constructor)
         :param chunk_iterator: the function providing base chunks. If not
           passed, the iter_flat() method will be used.
        """

        if chunk_iterator is None:
            chunk_iterator = self.iter_struct

        # Create the chunker object
        do_context = context if context is not None else self._iter_options.get("context", False)
        cls = ContextChunkGenerator if do_context else ChunkGenerator
        chunker = cls(meta=self._meta)

        # Iterate over the document elements and build a chunk for each one
        for elem in chunk_iterator():
            chunk = elem if isinstance(elem, DocumentChunk) else chunker(elem)
            if chunk:
                yield chunk

        # A pending last chunk?
        if do_context:
            chunk = chunker(None)
            if chunk:
                yield chunk


    def iter_struct(self) -> Iterable[Dict]:
        """
        Iterate over the object base iterator, ensuring that (a) we produce
        dictionaries and (b) all chunks have an id
        """
        is_dict = None
        for n, chunk in enumerate(self.iter_base(), start=1):
            if is_dict is None:
                is_dict = hasattr(chunk, "get") and chunk.get("data") is not None
            if not is_dict:
                chunk = {"id": str(n), "data": chunk}
            elif 'id' not in chunk:
                chunk = chunk.copy()
                chunk["id"] = str(n)
            yield chunk


    def iter_base(self) -> Iterator[Dict]:
        """
        The base iteration method to be implemented by subclasses. When executed
        it should return a sequence of chunks. Each chunk can be:
          * a dictionary-like object, containing at least a "data" field, and
            (optionally) an "id" field
          * a chunk payload (any data structure, except the one above)
        """
        raise UnimplementedException("abstract document class: missing iter_base() method")


# --------------------------------------------------------------------------


class SequenceSrcDocument(SrcDocument):
    """
    A sequence document, as an abstract class
    """

    def iter_full(self, context: bool = None, **kwargs) -> Iterable[Dict]:
        return super().iter_full(context=context)



class TreeSrcDocument(SrcDocument):
    """
    A tree document, as an abstract class.
    """

    def _yield_subtree(self, chunk: Dict, num: int, level: int, prefix: str,
                       context: str = None, src: bool = False) -> Iterable[Dict]:
        """
        Return all the chunks stemming from an element in the document
        tree, as a linear sequence
        """
        # Get base fields
        data = chunk.get("data")
        ctx = chunk.get("context") or context

        # Produce *this* chunk (if it contains data)
        if data:
            obj = {"id": chunk.get("id", f"{prefix}{num}"), "data": data}
            if src:
                obj["src"] = chunk
            obj["context"] = ctx.copy() if ctx else {}
            obj["context"]["level"] = level
            yield obj

        # Produce child chunks
        subprefix = f"{prefix}{num}."
        for n, subchunk in enumerate(chunk.get("chunks", []), start=1):
            yield from self._yield_subtree(subchunk, n, level+1, subprefix, ctx)


    def _recurse_tree(self) -> Iterable[Dict]:
        """
        Return all chunks from the document tree in a sequence, traversing it
        deep-first
        """
        for n, chunk in enumerate(self.iter_base(), start=1):
            yield from self._yield_subtree(chunk, n, level=0, prefix="")


    def iter_full(self, context: bool = None) -> Iterable[Dict]:
        """
        Iterate over the document, producing a linear sequence of DocumentChunk
        objects
        """
        return super().iter_full(context=context,
                                 chunk_iterator=self._recurse_tree)



class TableSrcDocument(SrcDocument):
    """
    A table document, as an abstract class.
    """

    def _iter_cells(self) -> Iterable[Dict]:
        """
        Return all cells from the document tree in a sequence, traversing it
        in row-major order
        """
        header = self.metadata
        colnames = header.get("column", {}).get("name")
        for r, row in enumerate(self.iter_base(), start=1):
            rowdata = row.get("data", [])
            rowid = row.get("id", r)
            for c, cell in enumerate(rowdata, start=1):
                data = {
                    "id": f"{rowid}.{c}",
                    "data": cell,
                    "context": {
                        "column": {"number": c},
                        "row": rowid
                    }
                }
                if colnames:
                    data["context"]["column"]["name"] = colnames[c-1]
                yield data


    def iter_full(self, context: bool = None) -> Iterable[Dict]:
        """
        Iterate over the document, producing a sequence of DocumentChunk
        objects
        """
        return super().iter_full(context=context,
                                 chunk_iterator=self._iter_cells)
