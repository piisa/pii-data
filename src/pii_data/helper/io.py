"""
Code to open & read local files
"""


import sys
from pathlib import Path
import gzip
import bz2
import lzma
import json
import io
from yaml import load as yaml_load, SafeLoader as YamlLoader

from typing import Dict, TextIO

from .exception import InvArgException


CHARSET_ENCODING = "utf-8"


def base_extension(name: str) -> str:
    """
    Return the base file extension, once a (possible) compression extension
    has been removed
    """
    if isinstance(name, str):
        name = Path(name)
    elif not isinstance(name, Path):
        return ""
    sfx = name.suffix
    return Path(name.stem).suffix if sfx in ('.gz', '.bz2', '.xz') else sfx


def openfile(name: str, mode: str = 'rt', encoding: str = None) -> TextIO:
    """
    Open files, as raw text or compressed text (gzip, bzip2 or xz)
    """
    # Check if we've been given a file-like object; if so just return it
    if mode.startswith("r") and hasattr(name, 'read') or \
       mode.startswith(("w", "a")) and hasattr(name, "write"):
        return name

    # Decide on an encoding
    sname = str(name)
    if mode.endswith('b'):
        encoding = None
    elif encoding is None:
        encoding = CHARSET_ENCODING

    # Open with the right module
    if sname == "-":
        return sys.stdout if mode.startswith("w") else sys.stdin
    elif sname.endswith(".gz"):
        return gzip.open(name, mode, encoding=encoding)
    elif sname.endswith(".bz2"):
        return bz2.open(name, mode, encoding=encoding)
    elif sname.endswith(".xz"):
        return lzma.open(name, mode, encoding=encoding)
    else:
        return open(name, mode, encoding=encoding)


def load_yaml(filename: str) -> Dict:
    """
    Load a YAML file
    """
    with openfile(filename) as f:
        return yaml_load(f, Loader=YamlLoader)


def load_datafile(filename: str) -> Dict:
    """
    Load a YAML or JSON file
    """
    filepath = Path(filename)
    if '.json' in filepath.suffixes:
        with openfile(filename) as f:
            return json.load(f)
    elif '.yml' in filepath.suffixes or '.yaml' in filepath.suffixes:
        return load_yaml(filename)
    else:
        raise InvArgException('cannot load "{}": unsupported format')
