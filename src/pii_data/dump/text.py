"""
Dump a document to plain text
"""

from typing import Dict, TextIO

from ..helper.io import openfile
from ..types.doc import SrcDocument


def _dump_chunk(chunk: Dict, out: TextIO, level: int, indent: int):
    """
    Dump a document chunk as raw text lines, possibly with leading indent
    """
    for line in chunk["data"].splitlines():
        print(" " * (level-1)*indent, line, sep="", file=out)
    for subchunk in chunk.get("chunks", []):
        _dump_chunk(subchunk, out, level+1, indent)


def dump_text(doc: SrcDocument, outputfile: str, indent: int = None):
    """
    Dump the data for a PII Source Document into a plain text file, maybe
    with indentation to preserve a tree structure.
    """
    if not indent:
        indent = 0
    with openfile(outputfile, "wt", encoding="utf-8") as f:
        for chunk in doc.iter_struct():
            _dump_chunk(chunk, f, 1, indent)
