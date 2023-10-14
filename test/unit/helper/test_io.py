"""
Test the io module
"""

from os import unlink
from pathlib import Path
import tempfile
import gzip
import bz2
import lzma
import io
import json

import pytest
from unittest.mock import Mock

import pii_data.helper.io as mod


EXAMPLE = Path(__file__).parents[2] / "data" / "config" / "full.json"


# ------------------------------------------------------------------------

def test100_base_extension():
    """Test base_extension function"""

    for name in ("23.abc", "23.abc.gz", "23.abc.xz", "23.abc.bz2"):
        assert mod.base_extension(name) == ".abc"
        assert mod.base_extension(Path(name)) == ".abc"

    assert mod.base_extension([1, 2]) == ""


def test200_openfile():
    """Test openfile"""

    with mod.openfile(EXAMPLE, encoding="utf-8") as f:
        data1 = f.read()

    with mod.openfile(EXAMPLE, "rb") as f:
        data2 = f.read().decode("utf-8")

    assert data1 == data2


def test210_openfile_file():
    """Test openfile, file-like"""

    with mod.openfile(EXAMPLE, encoding="utf-8") as f:
        data1 = f.read()

    with open(EXAMPLE, encoding="utf-8") as f:
        with mod.openfile(f) as f2:
            data2 = f2.read()

    assert data1 == data2


@pytest.mark.parametrize("ext", ["gz", "bz2", "xz"])
def test220_openfile_compressed(ext):
    """Test openfile"""
    with mod.openfile(EXAMPLE, encoding="utf-8") as f:
        data1 = f.read()

    try:
        with tempfile.NamedTemporaryFile(suffix=f".json.{ext}",
                                         delete=False) as f:
            f.close()

            # Write a compressed file
            lib = gzip if ext == "gz" else bz2 if ext == "bz2" else lzma
            with lib.open(f.name, "wb") as ff:
                ff.write(data1.encode("utf-8"))

            # Read it, as text
            with mod.openfile(f.name) as ft2:
                data2 = ft2.read()
            assert data1 == data2

            # Read it, as binary
            with mod.openfile(f.name, "rb") as ft3:
                data3 = ft3.read().decode("utf-8")
            assert data1 == data3

            # Write it, as text, and read it back
            with mod.openfile(f.name, "w", encoding="utf-8") as ft4:
                ft4.write(data1)
            with mod.openfile(f.name) as ft4:
                data4 = ft4.read()
            assert data1 == data4

    finally:
        unlink(f.name)


def test300_openuri():
    """Test openuri, implicit file"""

    # Text
    with mod.openuri(EXAMPLE, encoding="utf-8") as f:
        data1 = f.read()

    # Binary
    with mod.openuri(EXAMPLE, "rb") as f:
        data2 = f.read().decode("utf-8")

    assert data1 == data2


def test310_openuri():
    """Test openuri, explicit file URL"""

    name = f"file://{EXAMPLE}"

    with mod.openuri(name, encoding="utf-8") as f:
        data1 = f.read()

    with mod.openuri(name, "rb") as f:
        data2 = f.read().decode("utf-8")

    assert data1 == data2


def test320_openuri_http_text(monkeypatch):
    """Test openuri, https, text source"""

    exp = "a text buffer"
    buf = Mock(return_value=io.StringIO(exp))
    monkeypatch.setattr(mod, "urlopen", buf)

    name = "https://an.example.com/file.txt"
    with mod.openuri(name, encoding="utf-8") as f:
        got = f.read()

    assert exp == got
    assert buf.call_args[0] == (name,)


def test330_openuri_http_binary(monkeypatch):
    """Test openuri, https, binary source"""

    exp = b"a text buffer"
    buf = Mock(return_value=io.BytesIO(exp))
    monkeypatch.setattr(mod, "urlopen", buf)

    name = "https://an.example.com/file.txt"

    with mod.openuri(name, "rb") as f:
        got = f.read()

    assert exp == got
    assert buf.call_args[0] == (name,)


@pytest.mark.parametrize("ext", ["gz", "bz2", "xz"])
def test340_openuri_compressed(ext, monkeypatch):
    """Test openuri, https, compressed source"""

    name = f"https://an.example.com/file.txt.{ext}"
    exp = b"a text buffer"

    # Mock ah HTTP URL serving a compressed file
    lib = gzip if ext == "gz" else bz2 if ext == "bz2" else lzma
    v = io.BytesIO(lib.compress(exp))
    v.url = name
    buf = Mock(return_value=v)
    monkeypatch.setattr(mod, "urlopen", buf)

    with mod.openuri(name, "rb") as f:
        got = f.read()

    assert exp == got
    assert buf.call_args[0] == (name,)


def test400_yaml():
    """Test read_yaml, dump_yaml"""


    with mod.openfile(EXAMPLE,) as f:
        data1 = json.load(f)

    try:
        with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as f:
            f.close()
            mod.dump_yaml(data1, f.name)
            data2 = mod.load_yaml(f.name)
    finally:
        unlink(f.name)
        #print(f.name)

    assert data1 == data2
