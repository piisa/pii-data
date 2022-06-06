
from pathlib import Path
import tempfile
import datetime
import json

from unittest.mock import Mock
import pytest

from pii_data.types.piienum import PiiEnum
from pii_data.types.piientity import PiiEntity

import pii_data.types.piicollection as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()


@pytest.fixture
def fix_timestamp(monkeypatch):

    mydatetime = Mock(spec=datetime.datetime)
    mydatetime.utcnow = Mock(return_value=mydatetime)
    mydatetime.replace = Mock(return_value=mydatetime)
    mydatetime.isoformat = Mock(return_value = "2000-01-01T00:00:00Z")

    #print("ISINSTANCE", isinstance(mydatetime, datetime.datetime))
    datemock = Mock()
    datemock.datetime = mydatetime

    a = datemock.datetime.utcnow().replace()
    #print("A", a, isinstance(a, datetime.datetime))
    monkeypatch.setattr(mod, 'datetime', datemock)


# ----------------------------------------------------------------

def test100_piidetector():
    """Test object creation"""
    obj = mod.PiiDetector("PII Finder", "0.1.0", "PIISA")
    assert str(obj) == "<PiiDetector PIISA/PII Finder/0.1.0>"


def test110_piidetector():
    """Test object value"""
    obj = mod.PiiDetector("PII Finder", "0.1.0", "PIISA")
    assert obj.as_dict() == {"name": "PII Finder",
                             "version": "0.1.0",
                             "source": "PIISA"}


def test200_piicollection():
    """Test object creation"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")
    assert len(obj) == 0


def test210_piicollection_add():
    """Test adding PII entity"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PII Finder", "0.1.0", "PIISA")
    ent = PiiEntity(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")

    obj.entity(ent, det)
    assert len(obj) == 1


def test220_piicollection_dump_ndjson(fix_timestamp):
    """Test NDJSON dump"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PII Finder", "0.1.0", "PIISA")
    ent1 = PiiEntity(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")
    ent2 = PiiEntity(PiiEnum.CREDIT_CARD, "1234567890", chunk="30", pos=60,
                     country="br")
    obj.entity(ent1, det)
    obj.entity(ent2, det)
    assert len(obj) == 2

    # NDJSON format
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            obj.dump(f)
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    exp = readfile(fname('piicollection.ndjson'))
    assert exp == got


def test230_piicollection_dump_json(fix_timestamp):
    """Test JSON dump"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PII Finder", "0.1.0", "PIISA")
    ent1 = PiiEntity(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")
    ent2 = PiiEntity(PiiEnum.CREDIT_CARD, "1234567890", chunk="30", pos=60,
                     country="br")
    obj.entity(ent1, det)
    obj.entity(ent2, det)
    assert len(obj) == 2

    # JSON format
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            obj.dump(f, format='json')
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    exp = readfile(fname('piicollection.json'))
    assert json.loads(exp) == json.loads(got)


    #with open(fname('piicollection.ndjson'), "w", encoding="utf-8") as f:
    #          obj.dump(f, format="ndjson")

