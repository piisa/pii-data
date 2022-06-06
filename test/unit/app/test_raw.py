from pathlib import Path
import tempfile

import pytest

from pii_data.helper import load_yaml
import pii_data.app.rawdoc as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()


def test10_read():
    """Test reading a raw file"""

    with tempfile.NamedTemporaryFile() as f:
        f.close()

        mod.from_raw(fname('doc-example.txt'), f.name, indent=2)
        #mod.from_raw(fname('doc-example.txt'), fname('doc-example-2.yaml'), 2)
        got = load_yaml(f.name)
        exp = load_yaml(fname('doc-example.yaml'))
        assert got == exp


def test20_write():
    """Test writing a raw file"""

    with tempfile.NamedTemporaryFile() as f:
        f.close()

        mod.to_raw(fname('doc-example.yaml'), f.name, indent=2)
        #mod.from_raw(fname('doc-example.txt'), fname('doc-example-2.yaml'), 2)

        exp = readfile(fname('doc-example.txt'))
        got = readfile(f.name)
        assert got == exp
        
