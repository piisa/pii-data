"""
Test the TreeSrcDocument class
"""


from unittest.mock import Mock
import pytest

import pii_data.types.document as mod


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
    def top_chunks(self):
        return iter(TREEDOC)



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
    obj = mod.TreeSrcDocument()
    assert str(obj) == "<SrcDocument 00000-11111>"


def test120_set():
    """Test object creation, id"""
    obj = mod.TreeSrcDocument()
    obj.set_id("doc1")
    assert str(obj) == "<SrcDocument doc1>"


def test120_set_hdr():
    """Test object creation, set header"""
    obj = mod.TreeSrcDocument()
    obj.set_header_document({"id": "doc2"})
    assert str(obj) == "<SrcDocument doc2>"


def test200_iter():
    """Test iteration"""

    obj = ExampleTreeSrcDoc()

    exp = [
        mod.DocumentChunk(id='1', data='section 1', context=None),
        mod.DocumentChunk(id='2', data='subsection 1.1', context=None),
        mod.DocumentChunk(id='3', data='subsection 1.2', context=None),
        mod.DocumentChunk(id='4', data='section 2', context=None),
        mod.DocumentChunk(id='5', data='subsection 2.1', context=None),
        mod.DocumentChunk(id='6', data='subsection 2.1.1', context=None),
        mod.DocumentChunk(id='7', data='section 3', context=None)
    ]
    got = list(obj)
    assert exp == got


def test210_iter_ctx(fix_uuid):
    """Test iteration, with context"""

    obj = ExampleTreeSrcDoc(add_chunk_context=True)

    ctx_doc = {'id': '00000-11111'}
    exp = [
        mod.DocumentChunk(id='1', data='section 1',
                          context={'document': ctx_doc,
                                   'after': 'subsection 1.1'}),
        mod.DocumentChunk(id='2', data='subsection 1.1',
                          context={'document': ctx_doc,
                                   'before': 'section 1',
                                   'after': 'subsection 1.2'}),
        mod.DocumentChunk(id='3', data='subsection 1.2',
                          context={'document': ctx_doc,
                                   'before': 'subsection 1.1',
                                   'after': 'section 2'}),
        mod.DocumentChunk(id='4', data='section 2',
                          context={'document': ctx_doc,
                                   'before': 'subsection 1.2',
                                   'after': 'subsection 2.1'}),
        mod.DocumentChunk(id='5', data='subsection 2.1',
                          context={'document': ctx_doc,
                                   'before': 'section 2',
                                   'after': 'subsection 2.1.1'}),
        mod.DocumentChunk(id='6', data='subsection 2.1.1',
                          context={'document': ctx_doc,
                                   'before': 'subsection 2.1',
                                   'after': 'section 3'}),
        mod.DocumentChunk(id='7', data='section 3',
                          context={'document': ctx_doc,
                                   'before': 'subsection 2.1.1'})]

    got = list(obj)
    assert exp == got
