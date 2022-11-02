"""
Test the LocalSrcDocument class
"""


from pathlib import Path
from types import MappingProxyType
import tempfile
import json

from unittest.mock import Mock
import pytest

from typing import Dict

from pii_data.helper.io import load_yaml
from pii_data.helper.exception import InvalidDocument
import pii_data.types.document as doc
import pii_data.types.localdoc as mod


DATADIR = Path(__file__).parents[2] / "data" / "doc-example"

SIMPLEDOC = [
    "an example text",
    "another example text"
]


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()


def save_load(doc: mod.BaseLocalSrcDocument) -> Dict:
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        doc.dump(f, format="yml")
        f.close()
        return load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    
@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(doc, 'uuid', mock_uuid)


# ----------------------------------------------------------------

def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.BaseLocalSrcDocument()
    assert str(obj) == "<SrcDocument 00000-11111>"


def test110_constructor():
    """Test object creation, data"""
    meta = {"document": {"id": "doc1"}}
    obj = mod.BaseLocalSrcDocument(chunks=SIMPLEDOC, metadata=meta)
    assert str(obj) == "<SrcDocument doc1>"


def test120_set():
    """Test object creation, data"""
    obj = mod.BaseLocalSrcDocument()
    obj.set_id("doc1")
    obj.set_chunks(SIMPLEDOC)
    assert str(obj) == "<SrcDocument doc1>"


def test130_set_id_path():
    """Test object creation, set_id_path"""
    obj = mod.BaseLocalSrcDocument()
    obj.set_id_path("doc2")
    assert str(obj) == "<SrcDocument doc2>"
    obj.set_id_path("/base/data/doc2", "/base")
    assert str(obj) == "<SrcDocument data/doc2>"


def test200_iter_struct():
    """Test object struct iteration"""
    obj = mod.BaseLocalSrcDocument(chunks=SIMPLEDOC)
    got = list(obj.iter_struct())
    exp = [
        {"id": "1", "data": "an example text"},
        {"id": "2", "data": "another example text"}
    ]
    assert exp == got


def test250_iter_full():
    """Test object full iteration"""
    obj = mod.BaseLocalSrcDocument(chunks=SIMPLEDOC)
    got = list(obj)
    exp = [
        mod.DocumentChunk("1", "an example text"),
        mod.DocumentChunk("2", "another example text")
    ]
    assert exp == got


def test300_dump(fix_uuid):
    """Test object dump, plain"""
    obj = mod.BaseLocalSrcDocument(chunks=SIMPLEDOC)
    got = save_load(obj)

    exp = {
        'format': 'piisa:src-document:v1',
        'header': {
            'document': {'id': '00000-11111'}
        },
        'chunks': [
            {'id': '1', 'data': 'an example text'},
            {'id': '2', 'data': 'another example text'}
        ]
    }
    assert exp == got


def test310_dump_sequence(fix_uuid):
    """Test object dump, sequence"""
    obj = mod.SequenceLocalSrcDocument(chunks=SIMPLEDOC)
    got = save_load(obj)

    exp = {
        'format': 'piisa:src-document:v1',
        'header': {
            'document': {'id': '00000-11111', 'type': 'sequence'}
        },
        'chunks': [
            {'id': '1', 'data': 'an example text'},
            {'id': '2', 'data': 'another example text'}
        ]
    }
    assert exp == got


def test400_load_dump_sequential():
    """Test object load + dump, sequential"""
    obj = mod.load_file(DATADIR / "seq-id.yaml")
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(DATADIR / "seq-id.yaml")
    assert exp == got


def test401_load_dump_sequential_json():
    """Test object load + dump, sequential, json"""
    obj = mod.load_file(DATADIR / "seq-id.yaml")
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".json", delete=False)
        obj.dump(f.name)
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(DATADIR / "seq-id.yaml")
    assert exp == json.loads(got)


def test410_load_dump_tree(fix_uuid):
    """Test object load/dump, tree document"""

    obj = mod.load_file(DATADIR / "tree.yaml")

    # Dump to a YAML file, and load it back
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(DATADIR / 'tree-id.yaml')
    assert exp == got


def test420_load_dump_tree_id_path():
    """Test object load/dump, tree document, path_prefix"""

    name = DATADIR / "tree.yaml"
    obj = mod.load_file(name)
    obj.set_id_path(name, path_prefix=name.parents[2])

    # Dump to a YAML file, and load it back
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(DATADIR / 'tree-id-path.yaml')
    assert exp == got


def test430_load_dump_tree_class(fix_uuid):
    """Test object load/dump, tree document, class API"""

    obj = mod.LocalSrcDocumentFile(DATADIR / "tree.yaml")
    assert isinstance(obj, mod.TreeLocalSrcDocument)

    # Dump to a YAML file, and load it back
    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".yml", delete=False)
        obj.dump(f.name)
        got = load_yaml(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_yaml(DATADIR / 'tree-id.yaml')
    assert exp == got


def test430_load_dump_error(fix_uuid):
    """Test loading an invalid file"""
    with pytest.raises(InvalidDocument):
        mod.LocalSrcDocumentFile(DATADIR / "tree-error.yaml")


def test500_iter():
    """Test object iteration"""
    obj = mod.load_file(DATADIR / "seq-id.yaml")
    got = list(obj)

    assert len(got) == 19

    exp = [
        mod.DocumentChunk("1", "PII management specification"),
        mod.DocumentChunk("2", "Some rough initial ideas"),
        mod.DocumentChunk("3", "Overall architecture")
    ]
    for e, g in zip(exp, got):
        assert e == g


def test510_iter_context():
    """Test object iteration, iteration options"""
    obj = mod.load_file(DATADIR / "seq-id.yaml", iter_options={"context": True})
    got = list(obj)

    assert len(got) == 19

    doc = MappingProxyType({"id": "00000-11111", "type": "sequence"})
    exp = [
        mod.DocumentChunk(
            "1", "PII management specification",
            {"document": doc, "after": "Some rough initial ideas"}
        ),
        mod.DocumentChunk(
            "2", "Some rough initial ideas",
            {"document": doc, "before": "PII management specification",
             "after": "Overall architecture"}
        ),
        mod.DocumentChunk(
            "3", "Overall architecture",
            {"document": doc,
             "before": "Some rough initial ideas",
             "after": "The general structure of a framework dealing with PII management could be visualized as the following diagram:"}
        )
    ]
    for e, g in zip(exp, got):
        assert e == g



def test600_metadata():
    """Test read, add metadata"""
    meta = {"document": {"foo": "bar"}}
    obj = mod.load_file(DATADIR / "seq-id.yaml", metadata=meta)
    got = obj.metadata
    exp = MappingProxyType({
        "document": {
            "foo": "bar",
            "id": "00000-11111",
            "type": "sequence"
        }
    })
    assert exp == got


def test610_metadata_class():
    """Test read, add metadata, class object"""
    meta = {"document": {"foo": "bar"}}
    obj = mod.LocalSrcDocumentFile(DATADIR / "seq-id.yaml", metadata=meta)
    got = obj.metadata
    exp = MappingProxyType({
        "document": {
            "foo": "bar",
            "id": "00000-11111",
            "type": "sequence"
        }
    })
    assert exp == got
