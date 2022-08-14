"""
Dump documents to YAML
"""

from collections import defaultdict
from types import MappingProxyType

from yaml import dump
from yaml import SafeDumper
from yaml.representer import SafeRepresenter
#from yaml.nodes import MappingNode

from typing import Iterator, Iterable

from ..utils import TextNode
from ...defs import FMT_SRCDOCUMENT
from ...types import SrcDocument, DocumentChunk
from ...helper.io import openfile

class ChunkIter:
    """
    A small wrapper around a chunk iterator, to be able to map it to a custom
    YAML representer
    """
    __slots__ = ["chk"]

    def __init__(self, chunks: Iterator):
        self.chk = chunks

    def __iter__(self):
        return iter(self.chk)

    def __repr__(self):
        return "<ChunkIter>"


# --------------------------------------------------------------------------


def text_representer(dumper, data):
    """
    A YAML representer to ensure text nodes are dumped in block literal style
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data),
                                   style="|")


def chunk_representer(dumper, chunk):
    """
    A YAML representer for a DocumentChunk object
    """
    payload = chunk.data
    if isinstance(payload, str):
        payload = TextNode(payload)
    elem = {"id": chunk.id, "data": payload}
    if chunk.chunks:
        elem["chunks"] = chunk.chunks
    return dumper.represent_dict(elem)


def chunkiter_representer(dumper: SafeDumper, data: Iterable):
    """
    A YAML representer for the iterable yielding chunks
    """
    chunklist = []
    for chunk in data:
        elem = {"id": chunk["id"]} if "id" in chunk else {}
        payload = chunk.get("data")
        if isinstance(payload, str):
            payload = TextNode(payload)
        if payload:
            elem["data"] = payload
        if "chunks" in chunk:
            elem["chunks"] = ChunkIter(chunk["chunks"])
        chunklist.append(elem)

    return dumper.represent_list(chunklist)


def dump_yaml(doc: SrcDocument, outputfile: str, indent: int = None):
    """
    Dump the data for a PII Source Document into a YAML file.
    """
    mydumper = SafeDumper

    # Add representers for some Python types
    mydumper.add_representer(MappingProxyType, SafeRepresenter.represent_dict)
    mydumper.add_representer(defaultdict, SafeRepresenter.represent_dict)

    # Add representers for some Custom types
    mydumper.add_representer(ChunkIter, chunkiter_representer)
    mydumper.add_representer(DocumentChunk, chunk_representer)
    mydumper.add_representer(TextNode, text_representer)

    # Construct a serializable version of the document
    data = {"format": FMT_SRCDOCUMENT,
            "header": doc.metadata, "chunks": ChunkIter(doc.iter_struct())}

    # Write it
    with openfile(outputfile, "wt", encoding="utf-8") as f:
        yaml = dump(data, Dumper=mydumper, sort_keys=False, allow_unicode=True,
                    default_flow_style=False)
        f.write(yaml)
