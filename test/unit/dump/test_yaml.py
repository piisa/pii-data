"""
Test writing a SrcDocument as a yaml file
"""

from pathlib import Path
import tempfile
from yaml import safe_load as yaml_load

from pii_data.types.localdoc import LocalSrcDocumentFile
import pii_data.dump.yaml as mod


DATADIR = Path(__file__).parents[2] / "data" / "doc-example"


# ------------------------------------------------------------------------


def test100_write_seq():
    """Test writing a file as yaml"""

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-id.yaml")
        mod.dump_yaml(doc, f.name)

        with open(f.name, encoding="utf-8") as f:
            got = yaml_load(f)

    with open(DATADIR / "tree-id.yaml", encoding="utf-8") as f:
        exp = yaml_load(f)

    assert got == exp


def test200_write_seq_ctx():
    """Test writing a file as yaml, including context fields"""

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-ctx.yaml")
        mod.dump_yaml(doc, f.name)

        with open(f.name, encoding="utf-8") as f:
            got = yaml_load(f)

    with open(DATADIR / "tree-ctx.yaml", encoding="utf-8") as f:
        exp = yaml_load(f)

    assert got == exp


def test210_write_seq_ctx_filter():
    """Test writing a file as yaml, context field filtering, keep field"""

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-ctx.yaml")
        mod.dump_yaml(doc, f.name, context_fields=["heading"])

        with open(f.name, encoding="utf-8") as f:
            got = yaml_load(f)

    with open(DATADIR / "tree-ctx.yaml", encoding="utf-8") as f:
        exp = yaml_load(f)

    assert got == exp


def test220_write_seq_ctx_filter():
    """Test writing a file as yaml, context field filtering, remove field"""

    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.close()

        doc = LocalSrcDocumentFile(DATADIR / "tree-ctx.yaml")
        mod.dump_yaml(doc, f.name, context_fields=[])

        with open(f.name, encoding="utf-8") as f:
            got = yaml_load(f)

    with open(DATADIR / "tree-id.yaml", encoding="utf-8") as f:
        exp = yaml_load(f)

    assert got == exp
