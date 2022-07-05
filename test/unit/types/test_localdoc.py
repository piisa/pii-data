"""
Test the LocalSrcDocument class
"""


from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest


from pii_data.helper.io import load_yaml
import pii_data.types.document as doc
import pii_data.types.localdoc as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()


SIMPLEDOC = [
    "an example text",
    "another example text"
]

# ----------------------------------------------------------------

@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(doc, 'uuid', mock_uuid)


def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.LocalSrcDocument()
    assert str(obj) == "<SrcDocument 00000-11111>"


def test110_constructor():
    """Test object creation, data"""
    obj = mod.LocalSrcDocument(document_header={"id": "doc1"}, chunks=SIMPLEDOC)
    assert str(obj) == "<SrcDocument doc1>"


def test120_set():
    """Test object creation, data"""
    obj = mod.LocalSrcDocument()
    obj.set_id("doc1")
    obj.set_chunks(SIMPLEDOC)
    assert str(obj) == "<SrcDocument doc1>"


def test200_iter():
    """Test object iteration"""
    obj = mod.LocalSrcDocument(chunks=SIMPLEDOC)
    got = list(obj)
    exp = [
        mod.DocumentChunk("1", "an example text"),
        mod.DocumentChunk("2", "another example text")
    ]
    assert exp == got


def test210_dump(fix_uuid):
    """Test object dump"""
    obj = mod.LocalSrcDocument(chunks=SIMPLEDOC)
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = {
        'header': {
            'document': {'id': '00000-11111'}
        },
        'chunks': ['an example text', 'another example text']
    }
    assert exp == got


def test300_load_dump(fix_uuid):
    """Test object load/dump, tree document"""

    obj = mod.load_file(fname("doc-example-tree.yaml"))

    # Dump to a YAML file, and load it back
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(fname('doc-example-tree-id.yaml'))
    assert exp == got


def test400_sequential(fix_uuid):
    """Test sequential object dump"""
    obj = mod.SequentialLocalSrcDocument(chunks=SIMPLEDOC)
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = {
        'header': {
            'document': {'id': '00000-11111', 'type': 'sequential'}
        },
        'chunks': ['an example text', 'another example text']
    }
    assert exp == got

