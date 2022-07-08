"""
Dump raw documents
"""

from yaml import dump
from yaml import SafeDumper as Dumper
from collections import defaultdict

from typing import Dict, TextIO

from .utils import TextNode


# --------------------------------------------------------------------------


def text_representer(dumper, data):
    """
    A YAML representer to ensure text nodes are dumped in block literal style
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data),
                                   style="|")

def defaultdict_representer(dumper, data):
    """
    A YAML representer to ensure text nodes are dumped in block literal style
    """
    return dumper.represent_dict(data)


def dump_yaml(doc: Dict, outputfile: str, indent: int):
    """
    Dump the data for a  PII Source Document into a YAML file.
    """
    mydumper = Dumper
    mydumper.add_representer(TextNode, text_representer)
    mydumper.add_representer(defaultdict, defaultdict_representer)
    with open(outputfile, "w", encoding="utf-8") as f:
        yaml = dump(doc, Dumper=mydumper, sort_keys=False, allow_unicode=True,
                    default_flow_style=False)
        f.write(yaml)



# --------------------------------------------------------------------------

def _dump_chunk(chunk: Dict, out: TextIO, level: int, indent: int):
    """
    Dump a document chunk as raw text lines, possibly with leading indent
    """
    for line in chunk["data"].split("\n"):
        print(" " * (level-1)*indent, line, sep="", file=out)
    for subchunk in chunk.get("chunks", []):
        _dump_chunk(subchunk, out, level+1, indent)


def dump_raw(doc: Dict, outputfile: str, indent: int):
    """
    Dump the data for a  PII Source Document into a plain text file, possibly
    with indentation to preserve the tree structure.
    """
    with open(outputfile, "w", encoding="utf-8") as f:
        for chunk in doc.get("chunks", []):
            _dump_chunk(chunk, f, 1, indent)
