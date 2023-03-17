"""
Code to open & read files, either local files or remote files
"""

import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlparse
try:
    import ssl
except ImportError:
    ssl = None

import gzip
import bz2
import lzma
import json

from yaml import load as yaml_load, SafeLoader as YamlLoader, YAMLError

from typing import Dict, Callable, IO

from .exception import InvArgException, FileException


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


def is_file_like(name: str, mode: str) -> bool:
    """
    Check if a variable holds a file-like object
    """
    return mode.startswith("r") and hasattr(name, 'read') or \
        mode.startswith(("w", "a")) and hasattr(name, "write")


def openfile(name: str, mode: str = 'rt', encoding: str = None) -> IO:
    """
    Open local files, as raw text or compressed text (gzip, bzip2 or xz)
      :param name: filename to open (if a file-like object is passed, it will
        be returned)
      :param mode: open mode
      :param encoding: for text modes, charset encoding

    If an encoding is given, the file will be opened in text mode. If not,
    and text mode has been specified, a default encoding will be assigned.
    """

    file_like = is_file_like(name, mode)
    if file_like and not isinstance(name, str):
        sname = getattr(name, "url", None) or str(name)
    else:
        sname = str(name)

    # Decide on an encoding
    if mode.endswith('b'):
        encoding = None
    elif encoding is None:
        encoding = CHARSET_ENCODING
    else:
        mode = mode[0] + 't'

    # Open special sources
    if sname == "-":
        return sys.stdout if mode.startswith("w") else sys.stdin
    elif sname.endswith(".gz"):
        return gzip.open(name, mode, encoding=encoding)
    elif sname.endswith(".bz2"):
        return bz2.open(name, mode, encoding=encoding)
    elif sname.endswith(".xz"):
        return lzma.open(name, mode, encoding=encoding)

    # Open plain source
    if file_like:
        return name
    else:
        return open(name, mode, encoding=encoding)


def openuri(name: str, mode: str = 'rt', encoding: str = None,
            schemes: Dict[str, Callable] = None,
            ignore_cert: bool = False) -> IO:
    """
    Open a file from an URI
      :param name: the file to open, as a local filename or as an URI
      :param mode: file opening mode
      :param encoding: charset encoding (assumes text mode)
      :param schemes: a dict mapping URL schemes to functions that can open them
      :param ignore_cert: when opening an HTTP URL, ignore certificate
         validation issues

    The function will open local file and HTTP/HTTPS/FTP sources, for any other
    type of source an appropriate item must be provided, via the `schemes`
    argument
    """
    if is_file_like(name, mode):
        return openfile(name, mode, encoding)

    url = urlparse(str(name))

    if schemes and url.scheme in schemes:
        src = schemes[url.scheme](name)
    elif url.scheme in ('http', 'https', 'ftp'):
        if url.scheme == 'https' and ssl and ignore_cert:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        else:
            ctx = None
        src = urlopen(name, context=ctx)
    elif url.scheme not in ('', 'file'):
        raise InvArgException('unsupported uri scheme: {}', url.scheme)
    else:
        src = url.path

    return openfile(src, mode, encoding)


def load_yaml(filename: str) -> Dict:
    """
    Load a YAML file
    """
    with openfile(filename) as f:
        try:
            return yaml_load(f, Loader=YamlLoader)
        except YAMLError as e:
            raise FileException("read error in YAML file '{}': {}",
                                filename, e) from e


def load_datafile(filename: str) -> Dict:
    """
    Load a YAML or JSON file
    """
    filepath = Path(filename)
    if '.json' in filepath.suffixes:

        with openuri(filename) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise FileException("read error in JSON file '{}': {}",
                                    f, e) from e

    elif '.yml' in filepath.suffixes or '.yaml' in filepath.suffixes:

        return load_yaml(filename)

    else:
        raise InvArgException('cannot load "{}": unsupported format')
