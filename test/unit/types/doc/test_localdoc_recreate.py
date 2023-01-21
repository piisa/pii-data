"""
Test recreating a document in the LocalSrcDocument class
"""

from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest

from typing import Dict

from pii_data.helper.io import load_yaml
from pii_data.types.doc import DocumentChunk
import pii_data.types.doc.localdoc as mod


DATADIR = Path(__file__).parents[3] / "data"

SIMPLEDOC = [
    "an example text",
    "another example text",
    "a third text",
    "and yet another"
]


def save_load(doc: mod.BaseLocalSrcDocument) -> Dict:
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        doc.dump(f, format="yml")
        f.close()
        return load_yaml(f.name)
    finally:
        Path(f.name).unlink()


# ----------------------------------------------------------------


def test120_seq_create():
    """Test object creation, sequence"""
    obj = mod.SequenceLocalSrcDocument()
    obj.set_id("doc1")
    for n, c in enumerate(SIMPLEDOC, start=1):
        obj.add_chunk(DocumentChunk(n, c))

    exp = [DocumentChunk(i, v) for i, v in enumerate(SIMPLEDOC, start=1)]
    assert exp == list(obj)


def test121_seq_clone():
    """Test object cloning, sequence"""
    # Read a sequence document
    docfile = DATADIR / "doc-example" / "seq-id.yaml"
    doc1 = mod.LocalSrcDocumentFile(docfile)

    # Clone the object: create a new one, add the header, and then all chunks
    doc2 = mod.SequenceLocalSrcDocument()
    doc2.add_metadata(**doc1.metadata)
    for chunk in doc1:
        doc2.add_chunk(chunk)

    # Dump the new document to file, and compare with the original
    got = save_load(doc2)
    assert load_yaml(docfile) == got


def test130_tree_create():
    """Test object creation, tree"""
    obj = mod.TreeLocalSrcDocument()
    obj.set_id("doc2")

    # Create a small tree
    chunks = [
        DocumentChunk(1, SIMPLEDOC[0], {"level": 0}),
        DocumentChunk(2, SIMPLEDOC[1], {"level": 1}),
        DocumentChunk(3, SIMPLEDOC[2], {"level": 2}),
        DocumentChunk(4, SIMPLEDOC[3], {"level": 1})
    ]
    for c in chunks:
        obj.add_chunk(c)

    assert chunks == list(obj)

    got = save_load(obj)
    assert load_yaml(DATADIR / "doc-build" / "build-tree.yaml") == got


def test131_tree_clone():
    """Test object cloning, tree"""
    # Read a tree document - we use the "string ids" version so that we can
    # match with the original
    docfile = DATADIR / "doc-example" / "tree-ctx-str.yaml"
    doc1 = mod.LocalSrcDocumentFile(docfile)

    # Clone the object: create a new one, add the header, and then all chunks
    doc2 = mod.TreeLocalSrcDocument()
    doc2.add_metadata(**doc1.metadata)
    for chunk in doc1:
        doc2.add_chunk(chunk)

    # Dump the new document to file, and compare with the original
    assert load_yaml(docfile) == save_load(doc2)


def test140_table_create():
    """Test object creation, table"""
    obj = mod.TableLocalSrcDocument()
    obj.set_id("doc3")

    # Create a small table
    chunks = [
        DocumentChunk(1, SIMPLEDOC[0], {"row": 0}),
        DocumentChunk(2, SIMPLEDOC[1], {"row": 0}),
        DocumentChunk(3, SIMPLEDOC[2], {"row": 1}),
        DocumentChunk(4, SIMPLEDOC[3], {"row": 1})
    ]
    for c in chunks:
        obj.add_chunk(c)

    got = save_load(obj)
    assert load_yaml(DATADIR / "doc-build" / "build-table.yaml") == got


def test141_table_clone():
    """Test object cloning, table"""
    # Read a table document
    docfile = DATADIR / "doc-example" / "table.yaml"
    doc1 = mod.LocalSrcDocumentFile(docfile)

    # Clone the object: create a new one, add the header, and then all chunks
    doc2 = mod.TableLocalSrcDocument()
    doc2.add_metadata(**doc1.metadata)
    for chunk in doc1:
        doc2.add_chunk(chunk)

    assert load_yaml(docfile) == save_load(doc2)
