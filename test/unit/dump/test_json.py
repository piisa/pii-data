"""
Test writing a SrcDocument as a json file
"""

from yaml import safe_load as yaml_load
import json
from pathlib import Path
import tempfile

from pii_data.types.doc import LocalSrcDocumentFile
import pii_data.dump.json as mod


DATADIR = Path(__file__).parents[2] / "data" / "doc-example"


# ------------------------------------------------------------------------


def test100_write_seq():
    """Test writing a sequence document as json"""

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "seq-id.yaml")
        mod.dump_json(doc, f.name)

        with open(f.name, encoding="utf-8") as f:
            got = json.load(f)

    with open(DATADIR / "seq-id.yaml", encoding="utf-8") as f:
        exp = yaml_load(f)

    assert got == exp


def test110_write_tree():
    """Test writing a tree document as json"""

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-id.yaml")
        mod.dump_json(doc, f.name)

        with open(f.name, encoding="utf-8") as f:
            got = json.load(f)

    with open(DATADIR / "tree.json", encoding="utf-8") as f:
        exp = json.load(f)

    assert got == exp


def test200_write_seq_ctx():
    """Test writing a file as json, context"""

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-ctx.yaml")
        mod.dump_json(doc, f.name)

        with open(f.name, encoding="utf-8") as f:
            got = json.load(f)

    with open(DATADIR / "tree-ctx.yaml", encoding="utf-8") as f:
        exp = yaml_load(f)

    assert got == exp


def test210_write_seq_ctx_filter():
    """Test writing a file as json, context"""

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-ctx.yaml")
        mod.dump_json(doc, f.name, context_fields=[])

        with open(f.name, encoding="utf-8") as f:
            got = json.load(f)

    with open(DATADIR / "tree-ctx.yaml", encoding="utf-8") as f:
        exp = yaml_load(f)

    assert got == exp
