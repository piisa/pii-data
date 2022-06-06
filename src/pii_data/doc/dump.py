"""
Dump raw documents
"""

from yaml import dump
from yaml import SafeDumper as Dumper

from typing import Dict, TextIO

from .utils import TextNode


# --------------------------------------------------------------------------


def text_representer(dumper, data):
    """
    A YAML representer to ensure text nodes are dumped in block literal style
    """
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data),
                                   style='|')


def dump_yaml(doc: Dict, outputfile: str, indent: int):
    """
    Dump a source documento as YAML Source Document
    """
    mydumper = Dumper
    mydumper.add_representer(TextNode, text_representer)
    with open(outputfile, 'w', encoding='utf-8') as f:
        yaml = dump(doc, Dumper=mydumper, sort_keys=False, allow_unicode=True,
                    default_flow_style=False)
        f.write(yaml)



# --------------------------------------------------------------------------

def _dump_chunk(chunk: Dict, out: TextIO, level: int, indent: int):
    """
    Dump a document chunk as raw text lines, possibly with leading indent
    """
    for line in chunk['text'].split('\n'):
        print(' ' * (level-1)*indent, line, sep='', file=out)
    for subchunk in chunk.get('chunks', []):
        _dump_chunk(subchunk, out, level+1, indent)


def dump_raw(doc: Dict, outputfile: str, indent: int):
    """
    Convert a YAML PII Source Document to plain text
    """
    with open(outputfile, 'w', encoding='utf-8') as f:
        for chunk in doc.get('chunks', []):
            _dump_chunk(chunk, f, 1, indent)
