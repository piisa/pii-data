
from pathlib import Path
import tempfile

from unittest.mock import Mock
import pytest


from pii_data.helper.io import load_yaml
import pii_data.types.document as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()


SIMPLEDOC = [
    {"id": 1, "text": "an example text"},
    {"id": 2, "text": "another example text"}
]

# ----------------------------------------------------------------

@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(mod, 'uuid', mock_uuid)



def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.SourceDocument()
    assert str(obj) == "<SourceDocument 00000-11111>"


def test110_constructor():
    """Test object creation, data"""
    obj = mod.SourceDocument(id="doc1", chunks=SIMPLEDOC)
    assert str(obj) == "<SourceDocument doc1>"


def test120_set():
    """Test object creation, data"""
    obj = mod.SourceDocument()
    obj.set_id("doc1")
    obj.set_chunks(SIMPLEDOC)
    assert str(obj) == "<SourceDocument doc1>"


def test200_iter():
    """Test object iteration"""
    obj = mod.SourceDocument("doc1", SIMPLEDOC)
    got = list(obj)
    exp = [
        mod.DocumentChunk(1, "an example text"),
        mod.DocumentChunk(2, "another example text")
    ]
    assert exp == got


def test200_dump():
    """Test object dump"""
    obj = mod.SourceDocument("00000-11111")
    obj.load(fname("doc-example.yaml"))

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(fname('doc-example-id.yaml'))
    assert exp == got
