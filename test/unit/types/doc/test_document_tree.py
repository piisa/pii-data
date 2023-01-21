"""
Test the TreeSrcDocument class
"""
from types import MappingProxyType

from unittest.mock import Mock
import pytest

import pii_data.types.doc.document as mod


TREEDOC = [
    {
        "data": "section 1",
        "chunks": [
            {"data": "subsection 1.1"},
            {"data": "subsection 1.2"}
        ]
    },
    {
        "data": "section 2",
        "chunks": [
            {
                "data": "subsection 2.1",
                "chunks": [
                    {"data": "subsection 2.1.1"}
                ]
            }
        ]
    },
    {
        "data": "section 3"
    }
]


class ExampleTreeSrcDoc(mod.TreeSrcDocument):
    """A child class for testing purposes"""
    def iter_base(self):
        return iter(TREEDOC)


@pytest.fixture
def fix_uuid(monkeypatch):
    """
    Monkey-patch the document module to ensure a fixed uuid
    """
    mock_uuid = Mock()
    mock_uuid.uuid4 = Mock(return_value="00000-11111")
    monkeypatch.setattr(mod, "uuid", mock_uuid)


# ----------------------------------------------------------------

def test100_constructor(fix_uuid):
    """Test object creation"""
    obj = mod.TreeSrcDocument()
    assert str(obj) == "<SrcDocument 00000-11111>"


def test120_set():
    """Test object creation, id"""
    obj = mod.TreeSrcDocument()
    obj.set_id("doc1")
    assert str(obj) == "<SrcDocument doc1>"


def test121_set_hdr():
    """Test object creation, set header"""
    obj = mod.TreeSrcDocument()
    obj.add_metadata(document={"id": "doc2"})
    assert str(obj) == "<SrcDocument doc2>"


def test200_iter_struct():
    """Test struct iteration"""

    obj = ExampleTreeSrcDoc()

    exp = [{**e, "id": f"{n}"} for n, e in enumerate(TREEDOC, start=1)]
    got = list(obj.iter_struct())
    assert exp == got


def test300_iter_full():
    """Test full iteration"""

    obj = ExampleTreeSrcDoc()

    exp = [
        mod.DocumentChunk(id='1', data='section 1',
                          context={"level": 0}),
        mod.DocumentChunk(id='1.1', data='subsection 1.1',
                          context={"level": 1}),
        mod.DocumentChunk(id='1.2', data='subsection 1.2',
                          context={"level": 1}),
        mod.DocumentChunk(id='2', data='section 2',
                          context={"level": 0}),
        mod.DocumentChunk(id='2.1', data='subsection 2.1',
                          context={"level": 1}),
        mod.DocumentChunk(id='2.1.1', data='subsection 2.1.1',
                          context={"level": 2}),
        mod.DocumentChunk(id='3', data='section 3',
                          context={"level": 0})
    ]
    got = list(obj)
    assert exp == got


def test310_iter_ctx(fix_uuid):
    """Test full iteration, with context"""

    obj = ExampleTreeSrcDoc(iter_options={"context": True})

    ctx_doc = MappingProxyType({'id': '00000-11111'})
    exp = [
        mod.DocumentChunk(id='1', data='section 1',
                          context={'document': ctx_doc, "level": 0,
                                   'after': 'subsection 1.1'}),
        mod.DocumentChunk(id='1.1', data='subsection 1.1',
                          context={'document': ctx_doc, "level": 1,
                                   'before': 'section 1',
                                   'after': 'subsection 1.2'}),
        mod.DocumentChunk(id='1.2', data='subsection 1.2',
                          context={'document': ctx_doc, "level": 1,
                                   'before': 'subsection 1.1',
                                   'after': 'section 2'}),
        mod.DocumentChunk(id='2', data='section 2',
                          context={'document': ctx_doc, "level": 0,
                                   'before': 'subsection 1.2',
                                   'after': 'subsection 2.1'}),
        mod.DocumentChunk(id='2.1', data='subsection 2.1',
                          context={'document': ctx_doc, "level": 1,
                                   'before': 'section 2',
                                   'after': 'subsection 2.1.1'}),
        mod.DocumentChunk(id='2.1.1', data='subsection 2.1.1',
                          context={'document': ctx_doc,  "level": 2,
                                   'before': 'subsection 2.1',
                                   'after': 'section 3'}),
        mod.DocumentChunk(id='3', data='section 3',
                          context={'document': ctx_doc, "level": 0,
                                   'before': 'subsection 2.1.1'})]

    got = list(obj)
    assert exp == got
