"""
Dump documents to YAML
"""

from collections import defaultdict, namedtuple
from types import MappingProxyType

from yaml import dump
from yaml import SafeDumper
from yaml.representer import SafeRepresenter
#from yaml.nodes import MappingNode

from typing import Iterable, List, Dict

from ..defs import FMT_SRCDOCUMENT, CTX_FIELDS
from ..types import SrcDocument
from ..helper.io import openfile
from .utils import TextNode, ChunkIterWrapper



def text_representer(dumper, data):
    """
    A YAML representer to ensure text nodes are dumped in block literal style
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data),
                                   style="|")


class ChunkWrapperRepresenter:
    """
    A YAML representer for a ChunkWrapper (an iterator of dict-based chunks)
    """

    def __init__(self, context_fields: List[str] = None):
        """
          :param context_fields: explicit set of context fields to add to the
             output. If not passed, all existing context fields will be added
             *except* a set of well-known structure fields.
        """
        self.ctx_pos = context_fields is not None
        self.ctx = set(context_fields if self.ctx_pos else CTX_FIELDS)


    def __call__(self, dumper: SafeDumper, data: Iterable[Dict]):
        """
        Dump the passed ChunkIterWrapper
        """
        chunklist = []
        for chunk in data:

            # Base data
            elem = {"id": chunk["id"]} if "id" in chunk else {}
            payload = chunk.get("data")
            if isinstance(payload, str):
                payload = TextNode(payload)
            if payload:
                elem["data"] = payload

            # Additional chunks (tree documents)
            if "chunks" in chunk:
                elem["chunks"] = ChunkIterWrapper(chunk["chunks"])

            # Context
            ctx = chunk.get("context")
            if ctx:
                if self.ctx_pos:
                    fields = {f: ctx[f] for f in self.ctx if f in ctx}
                else:
                    fields = {f: ctx[f] for f in ctx if f not in self.ctx}
                if fields:
                    elem["context"] = fields

            chunklist.append(elem)

        return dumper.represent_list(chunklist)


def dump_yaml(doc: SrcDocument, outputfile: str,
              context_fields: List[str] = None):
    """
    Dump the data for a PII Source Document into a YAML file.
    """
    mydumper = SafeDumper

    # Add representers for some Python types
    mydumper.add_representer(MappingProxyType, SafeRepresenter.represent_dict)
    mydumper.add_representer(defaultdict, SafeRepresenter.represent_dict)

    # Add representers for some Custom types
    mydumper.add_representer(TextNode, text_representer)
    mydumper.add_representer(ChunkIterWrapper,
                             ChunkWrapperRepresenter(context_fields))

    # Construct a serializable version of the document
    data = {"format": FMT_SRCDOCUMENT,
            "header": doc.metadata,
            "chunks": ChunkIterWrapper(doc.iter_struct())}

    # Write it
    with openfile(outputfile, "wt", encoding="utf-8") as f:
        yaml = dump(data, Dumper=mydumper, sort_keys=False, allow_unicode=True,
                    default_flow_style=False)
        f.write(yaml)
