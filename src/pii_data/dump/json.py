"""
Dump documents to JSON
"""

from types import MappingProxyType

import json

from typing import List, Set, Union

from .utils import ChunkIterWrapper
from ..defs import FMT_SRCDOCUMENT
from ..types.doc import SrcDocument
from ..types.doc.defs import CTX_FIELDS
from ..helper.io import openfile


def serialize_chunk(chunk, ctx_fields: Set[str], ctx_pos: bool):
    """
    Serialize a document chunk, also with subchunks
    """
    # Main fields
    out = {"id": chunk["id"], "data": chunk["data"]}
    # Context
    ctx = chunk.get("context")
    if ctx:
        if ctx_pos:
            fields = {f: ctx[f] for f in ctx_fields if f in ctx}
        else:
            fields = {f: ctx[f] for f in ctx if f not in ctx_fields}
        if fields:
            out["context"] = fields
    # Subchunks
    if "chunks" in chunk:
        out["chunks"] = [serialize_chunk(c, ctx_fields, ctx_pos)
                         for c in chunk["chunks"]]
    return out



class CustomJSONEncoder(json.JSONEncoder):
    '''
    A custom JSON encoder that can serialize additional objects:
      - datetime objects (into ISO 8601 strings)
      - sets (as sorted lists)
      - iterators (as lists)
      - binary data as Base64 strings (or optionally skipped)
      - any object having a to_json() method

    Any other non-serializable object is converted to its string representation
    '''

    def __init__(self, *args, context_fields: List[str] = None, **kwargs):
        """
          :param context_fields: explicit set of context fields to add to the
             output. If not passed, all existing context fields will be added
             *except* a set of well-known structure fields.
        """
        super().__init__(*args, **kwargs)
        self.ctx_pos = context_fields is not None
        self.ctx = set(context_fields if self.ctx_pos else CTX_FIELDS)

    def default(self, obj):
        '''
        Serialize some special types
        '''
        if isinstance(obj, MappingProxyType):
            return dict(obj.items())
        elif isinstance(obj, ChunkIterWrapper):
            return [serialize_chunk(c, self.ctx, self.ctx_pos) for c in obj]
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def dump_json(doc: SrcDocument, outputfile: str,
              context_fields: List[str] = None,
              indent: Union[int, bool] = None, **kwargs):
    """
    Dump the data for a PII Source Document into a JSON file.
     :param doc: document to dump
     :param outputfile: output destination
     :param context_fields: ignored, for compatibility with YAML output
     :param indent: JSON indent level. If not given (or `None`) a default
        will automatically be assigned; to indicate `None` use `False`
     :param kwargs: additional arguments for the JSON dumper
    """

    # Construct a serializable version of the document
    data = {"format": FMT_SRCDOCUMENT,
            "header": doc.metadata,
            "chunks": ChunkIterWrapper(doc.iter_struct())}

    # Prepare JSON encoder parameters
    indent = None if indent is False else 2 if indent is None else indent
    dump_args = {"ensure_ascii": False, "indent": indent, **kwargs}

    # Write it. Ensure we only close it if we opened it
    f = openfile(outputfile, "wt", encoding="utf-8")
    try:
        json.dump(data, f, cls=CustomJSONEncoder, **dump_args)
    finally:
        if f != outputfile:
            f.close()
