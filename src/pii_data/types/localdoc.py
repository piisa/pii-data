"""
Some subclasses of SrcDocument that can read/write data from/to a local file.
"""
from pathlib import Path

from typing import Dict, Iterable, Union

from ..doc import dump_raw, dump_yaml
from ..helper.exception import InvArgException, FileException, UnimplementedException
from ..helper.io import load_datafile

from .document import SrcDocument, DocumentChunk, TreeSrcDocument

CHUNK_TYPE = Union[Dict, str]


TYPES = {"SequentialLocalSrcDocument": "sequential",
         "TreeLocalSrcDocument": "tree",
         "TabularLocalSrcDocument": "tabular"}

# --------------------------------------------------------------------------


class LocalSrcDocument(SrcDocument):
    """
    A document that can be loaded/saved to a local file
    """

    def __init__(self, document_header: Dict = None,
                 add_chunk_context: bool = False,
                 chunks: Iterable[CHUNK_TYPE] = None):
        """
          :param document_header: document general information
          :param add_chunk_context: add context information when iterating over
            chunks
          :param chunks: document chunks
        """
        super().__init__(document_header, add_chunk_context)
        self.set_chunks(chunks)
        dtype = TYPES.get(self.__class__.__name__)
        if dtype:
            self.add_metadata(document={"type": dtype})


    def set_id_path(self, path: str, path_prefix: str = None):
        """
        Set the document id from its filename
          :param path: the document full pathname to construct the id from
          :param path_prefix: a prefix to remove from the document pathname
        """
        if path_prefix:
            try:
                path = Path(path).relative_to(Path(path_prefix))
            except Exception as e:
                raise InvArgException("cannot set document id from {}: {}",
                                      path, e) from e
        self.set_id(str(path))


    def dump(self, outname: str, format: str = None, indent: int = 0):
        """
        Dump the document to an output file
        """
        if format is not None:
            format = str(format).lower()
        elif outname.endswith((".yml", ".yaml")):
            format = "yml"
        elif outname.endswith(".txt"):
            format = "txt"
        else:
            raise InvArgException("unspecified format for: {}", outname)

        data = {"header": self._meta, "chunks": list(self.get_chunks())}
        if format in ("yaml", "yml"):
            dump_yaml(data, outname, indent)
        else:
            dump_raw(data, outname, indent)


    def set_chunks(self, chunks: Iterable[Dict]):
        self._chk = chunks if chunks else None


    def get_chunks(self) -> Iterable[DocumentChunk]:
        """
        Get an iterable over document chunks
        """
        return iter(self._chk)


# --------------------------------------------------------------------------


class TreeLocalSrcDocument(LocalSrcDocument, TreeSrcDocument):

    def get_chunks_tree(self) -> Iterable[DocumentChunk]:
        """
        Get an iterable over document chunks
        """
        for chunk in self._chk:
            yield from self._yield_chunk(chunk)


class TabularLocalSrcDocument(LocalSrcDocument):
    pass


class SequentialLocalSrcDocument(LocalSrcDocument):
    pass


# --------------------------------------------------------------------------


def load_file(filename: str,
              add_chunk_context: bool = False) -> LocalSrcDocument:
    """
    Load a document stored in a YAML file
     :param filename: full pathname of the document to load
     :param add_chunk_context: when iterating over document chunks, add
       context data to each chunk
     :return: a LocalSrcDocument subclass
    """
    data = load_datafile(filename)

    # Get document type
    hdr = data.get("header", {})
    dtype = hdr.get("document", {}).get("type")

    # Select the proper object type to create
    if dtype == "tree":
        Obj = TreeLocalSrcDocument
    elif dtype == "tabular":
        Obj = TabularLocalSrcDocument
    else:
        Obj = SequentialLocalSrcDocument

    # Create object
    doc = Obj(add_chunk_context=add_chunk_context, chunks=data.get("chunks"))
    doc.add_metadata(**hdr)
    return doc
