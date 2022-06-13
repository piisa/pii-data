"""
Code to open & read local files
"""


import sys
from pathlib import Path
import gzip
import bz2
import lzma
import json
from yaml import load as yaml_load, SafeLoader as YamlLoader

from typing import Dict, TextIO

from .exception import InvArgException


CHARSET_ENCODING = "utf-8"


def openfile(name: str, mode: str = 'r') -> TextIO:
    """
    Open files, raw text or compressed (gzip, bzip2 or xz)
    """
    name = str(name)
    if name == "-":
        return sys.stdout if mode.startswith("w") else sys.stdin
    elif name.endswith(".gz"):
        return gzip.open(name, mode, encoding=CHARSET_ENCODING)
    elif name.endswith(".bz2"):
        return bz2.open(name, mode, encoding=CHARSET_ENCODING)
    elif name.endswith(".xz"):
        return lzma.open(name, mode, encoding=CHARSET_ENCODING)
    else:
        return open(name, mode, encoding=CHARSET_ENCODING)


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
