"""
Test reading config files
"""

from os import unlink
from pathlib import Path
import tempfile
import gzip

import pytest

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

    with open(EXAMPLE, encoding="utf-8") as f:
        with mod.openfile(f) as f2:
            data3 = f2.read()

    assert data1 == data3


def test210_openfile_compressed():
    """Test openfile"""
    with mod.openfile(EXAMPLE, encoding="utf-8") as f:
        data1 = f.read()

    try:
        with tempfile.NamedTemporaryFile(suffix=".json.gz", delete=False) as f:
            f.close()

            # Write a gzip file
            with gzip.open(f.name, "wb") as ff:
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
