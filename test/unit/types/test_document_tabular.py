"""
Test the TabularSrcDocument class
"""


from unittest.mock import Mock
import pytest

import pii_data.types.document as mod


COLNAMES = ["Date", "Name", "Credit Card", "Currency", "Amount", "Description"]

ROWS = [
    ["2021-03-01", "John Smith", "4273 9666 4581 5642", "USD", "12.39",
     "Our Iceberg Is Melting: Changing and Succeeding Under Any Conditions"],
    ["2022-09-10", "Erik Jonsk", "4273 9666 4581 5642", "EUR", "11.99",
     "Bedtime Originals Choo Choo Express Plush Elephant - Humphrey"],
    ["2022-09-11", "John Smith", "4273 9666 4581 5642", "USD", "339.99",
     "Robot Vacuum Mary,  Nobuk Robotic Vacuum Cleaner and Mop, 5000Pa Suction, Intelligent AI Mapping, Virtual Walls, Ideal for Pets Hair, Self-Charging, Carpets, Hard Floors, Tile, Wi-Fi, App Control"]
]



class ExampleTabularSrcDoc(mod.TabularSrcDocument):
    """A child class for testing purposes"""
    def get_chunks(self):
        # Return in two chunks
        return ROWS[0:2], ROWS[2:3]



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
    obj = mod.TabularSrcDocument()
    obj.set_id("doc1")
    assert str(obj) == "<SrcDocument doc1>"


def test120_set_hdr():
    """Test object creation, set header"""
    obj = mod.TabularSrcDocument()
    obj.set_header_document({"id": "doc2"})
    assert str(obj) == "<SrcDocument doc2>"


def test200_iter():
    """Test iteration"""

    obj = ExampleTabularSrcDoc()

    exp = [
        mod.DocumentChunk(id='1', data=ROWS[0:2]),
        mod.DocumentChunk(id='2', data=ROWS[2:3])
    ]
    got = list(obj)
    assert exp == got


def test210_iter_ctx(fix_uuid):
    """Test iteration, with context"""

    obj = ExampleTabularSrcDoc(add_chunk_context=True)

    ctx_doc = {'id': '00000-11111'}
    ctx_1 = {'document': ctx_doc, 'after': ROWS[2:3]}
    ctx_2 = {'document': ctx_doc, 'before': ROWS[0:2]}
    exp = [
        mod.DocumentChunk(id='1', data=ROWS[0:2], context=ctx_1),
        mod.DocumentChunk(id='2', data=ROWS[2:3], context=ctx_2)
    ]
    got = list(obj)
    assert exp == got
