"""
Some subclasses of SrcDocument intended to handle SrcDocuments holding local
information
  * read a YAML representation of the document from a local file, through the
    load_file() wrapper function
  * set the data source (as an iterator)
  * dump the document to a local file (YAML, JSON, text)
"""

from pathlib import Path

from typing import Dict, Iterable, Union, List

from ..defs import FMT_SRCDOCUMENT
from ..doc import dump_text, dump_yaml
from ..helper.exception import InvArgException, InvalidDocument
from ..helper.io import load_datafile, base_extension

from .document import SrcDocument, DocumentChunk, \
    TreeSrcDocument, SequenceSrcDocument, TableSrcDocument, TYPE_META


TYPE_CHUNK = Union[Dict, str, List]


# Mapping of classes to document type (as added to metadata)
TYPES = {"SequenceLocalSrcDocument": "sequence",
         "TreeLocalSrcDocument": "tree",
         "TableLocalSrcDocument": "table"}

# --------------------------------------------------------------------------


class BaseLocalSrcDocument(SrcDocument):
    """
    A document that can be saved to a local file. It also offers base methods
    to set its contents.
    """

    def __init__(self, chunks: Iterable[TYPE_CHUNK] = None,
                 iter_options: Dict = None, metadata: TYPE_META = None):
        """
          :param chunks: set the document chunks
          :param iter_options: set iteration options
          :param metadata: document general information
        """
        super().__init__(iter_options=iter_options, metadata=metadata)
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


    def set_chunks(self, chunks: Iterable[Dict]):
        """
        Set the document chunks
          :param chunks: an iterable producing either plain strings, or
            dictionaries (which contain at least a `data` field)
        """
        self._chk = chunks if chunks else None


    def iter_base(self) -> Iterable[DocumentChunk]:
        """
        Get an iterable over the document chunks
        """
        #import json; print("LOCAL CHUNKS", json.dumps(self._chk, indent=2))
        return iter(self._chk)


    def dump(self, outname: str, format: str = None, indent: int = 0):
        """
        Dump the document to an output file
          :param outname: name of the output file
          :param format: format to write the document in. Valid values are
            "yml", "json", "txt". If not present, the format will try to be
            deduced from the file extension
          :param indent:
        """
        dump_file(self, outname, format=format, indent=indent)



# --------------------------------------------------------------------------


class TreeLocalSrcDocument(BaseLocalSrcDocument, TreeSrcDocument):
    pass

class TableLocalSrcDocument(BaseLocalSrcDocument, TableSrcDocument):
    pass

class SequenceLocalSrcDocument(BaseLocalSrcDocument, SequenceSrcDocument):
    pass


# --------------------------------------------------------------------------

def dump_file(doc: SrcDocument, outname: str,
              format: str = None, indent: int = 0):
    """
    Dump a document to an output file
      :param outname: name of the ooutput file
      :param format: format to write the document in. Valid values are
        "yml", "json", "txt". If not present, the format will try to be
        deduced from the file extension
      :param indent:
    """
    ext = base_extension(outname)
    if format is not None:
        format = str(format).lower()
    elif ext in (".yml", ".yaml"):
        format = "yml"
    elif ext == ".txt":
        format = "txt"
    else:
        raise InvArgException("unspecified format for: {}", outname)

    if format in ("yaml", "yml"):
        dump_yaml(doc, outname, indent)
    else:
        dump_text(doc, outname, indent)



def load_file(filename: str, iter_options: Dict = None,
              metadata: TYPE_META = None) -> BaseLocalSrcDocument:
    """
    Load a document stored in a YAML file
     :param filename: full pathname of the document to load
     :param iter_options: iteration options for the document
     :param metadata: metadata to add to the document
     :return: a LocalSrcDocument subclass
    """
    data = load_datafile(filename)

    # Check format
    if "format" not in data:
        raise InvalidDocument("Error: missing format indicator in {}", filename)
    fmt = data.get("format")
    if fmt != FMT_SRCDOCUMENT:
        raise InvalidDocument(f"Error: invalid format {fmt} in {filename}")

    # Fetch the document header & get document type
    hdr = data.get("header", {})
    dtype = hdr.get("document", {}).get("type")

    # Update header with additional metadata, if passed
    if metadata is not None:
        for name, d in metadata.items():
            if name not in hdr:
                hdr[name] = d
            else:
                hdr[name].update(d)

    # Select the proper object type to create
    if dtype == "tree":
        Obj = TreeLocalSrcDocument
    elif dtype == "table":
        Obj = TableLocalSrcDocument
    else:
        Obj = SequenceLocalSrcDocument

    # Create object
    return Obj(chunks=data.get("chunks"), metadata=hdr,
               iter_options=iter_options)



class LocalSrcDocument:
    """
    A dispatcher class that loads a SrcDocument stored in a local YAML file
    """

    def __new__(self, filename: str, iter_options: Dict = None,
                metadata: TYPE_META = None):
        """
        Create the appropriate class for the YAML file
          :param filename: name of the filename to rad
          :param iter_options: iteration options for the object
          :param metadata: metadata to add to the document
        """
        return load_file(filename, iter_options=iter_options, metadata=metadata)
