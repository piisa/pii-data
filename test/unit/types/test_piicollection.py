
from pathlib import Path
import tempfile
import datetime
import json

from unittest.mock import Mock
import pytest

from pii_data.types.piienum import PiiEnum
from pii_data.types.piientity import PiiEntity

import pii_data.types.piicollection.collection as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()


@pytest.fixture
def fix_timestamp(monkeypatch):
    """
    Monkey-patch the piicollection module to ensure the timestamps it produces
    have always the same value
    """
    mock_datetime = Mock()
    mock_datetime.utcnow.return_value = datetime.datetime(2000, 1, 1)
    mock_datetime.side_effect = lambda *a, **kw: datetime.datetime(*a, **kw)
    monkeypatch.setattr(mod, 'datetime', mock_datetime)


# ----------------------------------------------------------------

def test100_piidetector():
    """Test object creation"""
    obj = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")
    assert str(obj) == "<PiiDetector PIISA/PII Finder/0.1.0>"


def test110_piidetector():
    """Test object value"""
    obj = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")
    assert obj.asdict() == {"name": "PII Finder",
                            "version": "0.1.0",
                            "source": "PIISA"}


def test200_piicollection():
    """Test object creation"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")
    assert len(obj) == 0


def test210_piicollection_add():
    """Test adding PII entity"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")
    ent = PiiEntity.build(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")

    obj.add(ent, det)
    assert len(obj) == 1


def test320_piicollection_fields(fix_timestamp):
    """Test object fields"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PIISA", "PIICollectionTest", "0.1.0")
    ent1 = PiiEntity.build(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")
    ent2 = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234567890", chunk="30",
                           pos=60, country="br")
    obj.add(ent1, det)
    obj.add(ent2, det)

    det = {
        1: {'name': 'PIICollectionTest', 'source': 'PIISA', 'version': '0.1.0'}
    }
    got = obj.get_detectors()
    assert got == det

    got = obj.get_detector(1)
    assert isinstance(got, mod.PiiDetector)
    assert got.asdict() == det[1]
    d = mod.PiiDetector(**det[1])
    assert got == d

    exp = {
        'format': 'piisa:pii-collection:v1',
        'lang': 'pt',
        'date': datetime.datetime(2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        'stage': 'detection',
        'detectors': det
    }
    got = obj.get_header()
    assert got == exp


def test300_piicollection_dump_json(fix_timestamp):
    """Test JSON dump"""
    obj = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")
    ent1 = PiiEntity.build(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")
    ent2 = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234567890", chunk="30",
                           pos=60, country="br")
    obj.add(ent1, det)
    obj.add(ent2, det)
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




def test310_piicollection_clone(fix_timestamp):
    """Test clone"""
    obj1 = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")
    ent1 = PiiEntity.build(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")
    ent2 = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234567890", chunk="30",
                           pos=60, country="br")
    obj1.add(ent1, det)
    obj1.add(ent2, det)
    assert len(obj1) == 2

    obj2 = mod.PiiCollection.clone(obj1)
    for ent in obj1:
        obj2.add(ent)
    assert len(obj2) == 2

    # JSON format
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            obj2.dump(f, format='json')
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    exp = readfile(fname('piicollection.json'))
    assert json.loads(exp) == json.loads(got)
