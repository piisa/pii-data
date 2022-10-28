"""
Test the TableSrcDocument class
"""

from types import MappingProxyType
from pathlib import Path
import json
from itertools import cycle

from unittest.mock import Mock
import pytest

import pii_data.types.document as mod


DATADIR = Path(__file__).parents[2] / "data"

COLNAMES = ["Date", "Name", "Credit Card", "Currency", "Amount", "Description"]

ROWS = [
    ["2021-03-01", "John Smith", "4273 9666 4581 5642", "USD", "12.39",
     "Our Iceberg Is Melting: Changing and Succeeding Under Any Conditions"],
    ["2022-09-10", "Erik Jonsk", "4273 9666 4581 5642", "EUR", "11.99",
     "Bedtime Originals Choo Choo Express Plush Elephant - Humphrey"],
    ["2022-09-11", "John Smith", "4273 9666 4581 5642", "USD", "339.99",
     "Robot Vacuum Mary, Nobuk Robotic Vacuum Cleaner and Mop, 5000Pa Suction, Intelligent AI Mapping, Virtual Walls, Ideal for Pets Hair, Self-Charging, Carpets, Hard Floors, Tile, Wi-Fi, App Control"]
]


class ExampleTableSrcDoc(mod.TableSrcDocument):
    """A child class for testing purposes"""
    def iter_base(self):
        for r in ROWS:
            yield {"data": r}


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
    obj = mod.TableSrcDocument()
    assert str(obj) == "<SrcDocument 00000-11111>"


def test120_set():
    """Test object creation, id"""
    obj = mod.TableSrcDocument()
    obj.set_id("doc1")
    assert str(obj) == "<SrcDocument doc1>"


def test121_set_hdr():
    """Test object creation, set header"""
    obj = mod.TableSrcDocument()
    obj.add_metadata(document={"id": "doc2"})
    assert str(obj) == "<SrcDocument doc2>"


def test200_iter_struct():
    """Test struct iteration"""

    obj = ExampleTableSrcDoc()

    exp = [
        {"id": f"{rn}", "data": row}
        for rn, row in enumerate(ROWS, start=1)
    ]
    got = list(obj.iter_struct())
    assert exp == got


def test300_iter_full():
    """Test full iteration"""

    obj = ExampleTableSrcDoc()

    exp = [
        mod.DocumentChunk(id=f'{rn}.{cn}', data=e)
        for rn, row in enumerate(ROWS, start=1)
        for cn, e in enumerate(row, start=1)
    ]
    got = list(obj)

    # We check chunk contents, since the final chunks have additional contexts
    for e, g in zip(exp, got):
        assert e.id == g.id
        assert e.data == g.data
        assert sorted(g.context.keys()) == ["column", "row"]


def test310_iter_full_ctx(fix_uuid):
    """Test iteration, with context"""

    obj = ExampleTableSrcDoc(iter_options={"context": True})

    # Prepare the list of expected document chunks
    with open(DATADIR / "table-example.json") as f:
        data = json.load(f)
    exp = [mod.DocumentChunk(**e) for e in data]
    ctx_doc = MappingProxyType({'id': '00000-11111'})
    for e in exp:
        e.context["document"] = ctx_doc

    # We check chunk contents, since the final chunks have additional contexts
    for n, (e, g) in enumerate(zip(exp, list(obj))):
        assert e.id == g.id
        assert e.data == g.data
        cols = ["after", "column", "document", "row"] if n == 0 else \
            ["before", "column", "document", "row"] if n == len(exp)-1 else \
            ["after", "before", "column", "document", "row"]
        assert sorted(g.context.keys()) == cols


def test320_iter_full_ctx_name(fix_uuid):
    """Test iteration, with context, column names"""

    obj = ExampleTableSrcDoc(iter_options={"context": True})
    obj.add_metadata(column={"name": COLNAMES})

    # Prepare the list of expected document chunks
    with open(DATADIR / "table-example.json") as f:
        data = json.load(f)
    exp = [mod.DocumentChunk(**e) for e in data]
    ctx_doc = MappingProxyType({'id': '00000-11111'})
    for e, c in zip(exp, cycle(COLNAMES)):
        e.context["document"] = ctx_doc
        e.context["column"]["name"] = c

    # We check chunk contents, since the final chunks have additional contexts
    got = list(obj)
    for n, (e, g) in enumerate(zip(exp, got)):
        assert e.id == g.id
        assert e.data == g.data
        cols = ["after", "column", "document", "row"] if n == 0 else \
            ["before", "column", "document", "row"] if n == len(exp)-1 else \
            ["after", "before", "column", "document", "row"]
        assert sorted(g.context.keys()) == cols
