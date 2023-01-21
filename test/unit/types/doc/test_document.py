"""
Test the SrcDocument class
"""


from unittest.mock import Mock
import pytest

import pii_data.types.doc.document as mod


SIMPLEDOC = [
    "an example text",
    "another example text",
    "a third chunk"
]


class ExampleSrcDoc(mod.SrcDocument):
    """A child class for testing purposes"""
    def iter_base(self):
        return iter(SIMPLEDOC)


# ----------------------------------------------------------------

@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(mod, "uuid", mock_uuid)



def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.SrcDocument()
    assert str(obj) == "<SrcDocument 00000-11111>"


def test110_set():
    """Test object creation, id"""
    obj = mod.SrcDocument()
    obj.set_id("doc1")
    assert str(obj) == "<SrcDocument doc1>"


def test120_set_hdr():
    """Test object creation, set header"""
    obj = mod.SrcDocument()
    obj.add_metadata(document={"id": "doc2"})
    assert str(obj) == "<SrcDocument doc2>"


def test130_set_get_hdr():
    """Test object creation, set/get header"""
    obj = mod.SrcDocument()
    obj.add_metadata(document={"id": "doc2"})
    assert str(obj) == "<SrcDocument doc2>"


def test200_iter():
    """Test iteration"""

    obj = ExampleSrcDoc()
    got = list(obj)

    exp = [
        mod.DocumentChunk(id="1", data="an example text"),
        mod.DocumentChunk(id="2", data="another example text"),
        mod.DocumentChunk(id="3", data="a third chunk")
    ]

    assert exp == got


def test210_iter_ctx(fix_uuid):
    """Test iteration, with context"""

    obj = ExampleSrcDoc(iter_options={"context": True})
    got = list(obj)

    exp = [
        mod.DocumentChunk(id="1", data="an example text",
                          context={"document": {"id": "00000-11111"},
                                   "after": "another example text"}),
        mod.DocumentChunk(id="2", data="another example text",
                          context={"document": {"id": "00000-11111"},
                                   "before": "an example text",
                                   "after": "a third chunk"}),
        mod.DocumentChunk(id="3", data="a third chunk",
                          context={"document": {"id": "00000-11111"},
                                   "before": "another example text"})]

    assert exp == got


def test211_iter_ctx(fix_uuid):
    """Test iteration, with context, explicit method"""

    obj = ExampleSrcDoc()
    got = obj.iter_full(context=True)

    exp = [
        mod.DocumentChunk(id="1", data="an example text",
                          context={"document": {"id": "00000-11111"},
                                   "after": "another example text"}),
        mod.DocumentChunk(id="2", data="another example text",
                          context={"document": {"id": "00000-11111"},
                                   "before": "an example text",
                                   "after": "a third chunk"}),
        mod.DocumentChunk(id="3", data="a third chunk",
                          context={"document": {"id": "00000-11111"},
                                   "before": "another example text"})]

    assert exp == list(got)


def test220_iter_ctx_doc(fix_uuid):
    """Test iteration, with document & chunk context, inc. lang"""

    hdr = {"document": {"main_lang": "en", "id": "doc33"}}
    obj = ExampleSrcDoc(metadata=hdr, iter_options={"context": True})
    got = list(obj)

    exp = [
        mod.DocumentChunk(id="1", data="an example text",
                          context={"document": {"main_lang": "en", "id": "doc33"},
                                   "lang": "en",
                                   "after": "another example text"}),
        mod.DocumentChunk(id="2", data="another example text",
                          context={"document": {"main_lang": "en", "id": "doc33"},
                                   "lang": "en",
                                   "before": "an example text",
                                   "after": "a third chunk"}),
        mod.DocumentChunk(id="3", data="a third chunk",
                          context={"document": {"main_lang": "en", "id": "doc33"},
                                   "lang": "en",
                                   "before": "another example text"})]
    assert exp == got



def test230_iter_metadata():
    """Test iteration, w/ metadata"""

    meta = {"document": {"id": "doc44"}}
    obj = ExampleSrcDoc(metadata=meta, iter_options={"context": True})
    obj.add_metadata(document={"main_lang": "ch"}, dataset={"name": "BigDataset"})
    got = list(obj)

    exp = [
        mod.DocumentChunk(id="1", data="an example text",
                          context={"document": {"main_lang": "ch", "id": "doc44"},
                                   "dataset": {"name": "BigDataset"},
                                   "lang": "ch",
                                   "after": "another example text"}),
        mod.DocumentChunk(id="2", data="another example text",
                          context={"document": {"main_lang": "ch", "id": "doc44"},
                                   "dataset": {"name": "BigDataset"},
                                   "lang": "ch",
                                   "before": "an example text",
                                   "after": "a third chunk"}),
        mod.DocumentChunk(id="3", data="a third chunk",
                          context={"document": {"main_lang": "ch", "id": "doc44"},
                                   "dataset": {"name": "BigDataset"},
                                   "lang": "ch",
                                   "before": "another example text"})]
    assert exp == got
