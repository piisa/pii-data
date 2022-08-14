"""
Test writing a SrcDocument as a raw text file
"""

from pathlib import Path
import tempfile

from pii_data.types.localdoc import LocalSrcDocument
import pii_data.doc.textdump as mod


DATADIR = Path(__file__).parents[2] / "data"

def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read()

# ------------------------------------------------------------------------


def test200_write_seq():
    """Test writing a raw file"""

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.close()

        doc = LocalSrcDocument(DATADIR / "doc-example-tree-id.yaml")
        mod.dump_text(doc, f.name, indent=0)
        got = readfile(f.name)

    with open(DATADIR / "doc-example.txt", encoding="utf-8") as f:
        exp = ''.join(ln.lstrip() for ln in f)

    assert got == exp


def test210_write_tree():
    """Test writing a raw file"""

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.close()

        doc = LocalSrcDocument(DATADIR / "doc-example-tree-id.yaml")
        mod.dump_text(doc, f.name, indent=2)
        got = readfile(f.name)

    exp = readfile(DATADIR / "doc-example.txt")
    assert got == exp
