"""
Some subclasses of SrcDocument intended to handle SrcDocuments holding local
information
  * read a YAML representation of the document from a local file, through the
    load_file() wrapper function
  * set the data source (as an iterator)
  * dump the document to a local file (YAML, JSON, text)
"""

from pathlib import Path

from typing import Dict, Iterable, Union, List, Iterator

from ..defs import FMT_SRCDOCUMENT, DOC_TYPES
from ..dump import dump_text, dump_yaml, dump_json
from ..helper.exception import InvArgException, InvalidDocument
from ..helper.io import load_datafile, base_extension

from .document import SrcDocument, DocumentChunk, \
    TreeSrcDocument, SequenceSrcDocument, TableSrcDocument, TYPE_META


TYPE_CHUNK = Union[Dict, str, List]



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
        # Add document chunks
        self.set_chunks(chunks)
        # Find the docuemnt type and add it to the header
        dtype = DOC_TYPES.get(self.__class__.__name__)
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
        self._chk = chunks if chunks else []


    def iter_base(self) -> Iterator[DocumentChunk]:
        """
        Get an iterable over the document chunks
        """
        #import json; print("LOCAL CHUNKS", json.dumps(self._chk, indent=2))
        return iter(self._chk)


    def dump(self, outname: str, format: str = None, indent: int = None,
             context_fields: List[str] = None):
        """
        Dump the document to an output file
          :param outname: name of the output file
          :param format: format to write the document in. Valid values are
            "yml", "json", "txt". If not present, the format will try to be
            deduced from the file extension
          :param indent: for text output and tree documents, indent used to
            indicate hierarchy level
          :param context_fields: for YAML/JSON output, specific set of context
            fields that will be dumped, if present in the iter_struct() results.
            If not passed, all existing context fields will be added *except* a
            set of well-known structure fields.
        """
        dump_file(self, outname, format=format, indent=indent,
                  context_fields=context_fields)



# --------------------------------------------------------------------------


class SequenceLocalSrcDocument(BaseLocalSrcDocument, SequenceSrcDocument):

    def add_chunk(self, chunk: DocumentChunk):
        """
        Add a chunk to the sequence document
        """
        self._chk.append(chunk.as_dict())


class TreeLocalSrcDocument(BaseLocalSrcDocument, TreeSrcDocument):

    def add_chunk(self, chunk: DocumentChunk):
        """
        Add a chunk to the tree document
        """
        cur_lev = getattr(self, "_cur_lev", 0)
        new_lev = chunk.context.get("level", 0) if chunk.context else 0

        if new_lev > cur_lev + 1:
            raise InvArgException("level gap in document tree for chunk: {}",
                                  chunk.id)
        chunk = chunk.as_dict()
        if new_lev == 0:
            self._chk.append(chunk)
            self._stack = [chunk]
            return

        pos = self._stack[new_lev-1]
        self._cur_lev = new_lev
        self._stack = self._stack[:new_lev] + [chunk]
        if "chunks" not in pos:
            pos["chunks"] = [chunk]
        else:
            pos["chunks"].append(chunk)


class TableLocalSrcDocument(BaseLocalSrcDocument, TableSrcDocument):

    def add_chunk(self, chunk: DocumentChunk):
        """
        Add a chunk to the table document
        """
        cur_row = getattr(self, "_cur_row", None)
        new_row = chunk.context.get("row")

        if new_row == cur_row:
            row_chunk = self._chk[-1]
        else:
            row_chunk = {"id": new_row, "data": []}
            self._chk.append(row_chunk)

        row_chunk["data"].append(chunk.data)
        self._cur_row = new_row


class LocalSrcDocument:
    """
    A dispatcher class that loads a SrcDocument stored in a local YAML file
    """

    def __new__(self, document_type: str, **kwargs):
        """
        Create a local document of a specific type
        """
        if document_type == "sequence":
            return SequenceLocalSrcDocument(**kwargs)
        elif document_type == "tree":
            return TreeLocalSrcDocument(**kwargs)
        elif document_type == "table":
            return TableLocalSrcDocument(**kwargs)
        else:
            InvArgException("unknown document type: {}", document_type)


# --------------------------------------------------------------------------

def dump_file(doc: SrcDocument, outname: str,
              format: str = None, indent: int = None,
              context_fields: List[str] = None):
    """
    Dump a document to an output file
      :param outname: name of the output file
      :param format: format to write the document in. Valid values are
        "yml", "txt". If not present, the format will try to be
        deduced from the file extension
      :param indent: for text output and tree documents, indent used to
         indicate hierarchy level
      :param context_fields: for YAML/JSON output, specific set of context
         fields that will be dumped, if present in the iter_struct() results.
         If not passed, all existing context fields will be added *except* a
         set of well-known structure fields.
    """
    ext = base_extension(outname)
    if format is not None:
        format = str(format).lower()
    elif ext in (".yml", ".yaml"):
        format = "yml"
    elif ext in (".txt", ".text"):
        format = "txt"
    elif ext == ".json":
        format = "json"
    else:
        raise InvArgException("unspecified format for: {}", outname)

    if format in ("yaml", "yml"):
        dump_yaml(doc, outname, context_fields=context_fields)
    elif format == "json":
        dump_json(doc, outname, indent=indent, context_fields=context_fields)
    elif format in ("txt", "text"):
        dump_text(doc, outname, indent=indent)
    else:
        raise InvArgException("unsupported output format: {}", format)


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
    elif dtype == "sequence" or type is None:
        Obj = SequenceLocalSrcDocument
    else:
        raise InvalidDocument(f"Unknown document type '{dtype}' in {filename}")

    # Create object
    return Obj(chunks=data.get("chunks"), metadata=hdr,
               iter_options=iter_options)


class LocalSrcDocumentFile:
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
