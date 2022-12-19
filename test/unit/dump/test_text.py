"""
Test writing a SrcDocument as a raw text file
"""

from pathlib import Path
import tempfile

from pii_data.types.doc import LocalSrcDocumentFile
import pii_data.dump.text as mod


DATADIR = Path(__file__).parents[2] / "data" / "doc-example"

def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read()

# ------------------------------------------------------------------------


def test200_write_seq():
    """Test writing a raw file, as a sequence"""

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-id.yaml")
        mod.dump_text(doc, f.name, indent=0)
        got = readfile(f.name)

    with open(DATADIR / "tree.txt", encoding="utf-8") as f:
        exp = ''.join(ln.lstrip() for ln in f)

    assert got == exp


def test210_write_tree():
    """Test writing a raw file, as a tree"""

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-id.yaml")
        mod.dump_text(doc, f.name, indent=2)
        got = readfile(f.name)

    exp = readfile(DATADIR / "tree.txt")
    assert got == exp
