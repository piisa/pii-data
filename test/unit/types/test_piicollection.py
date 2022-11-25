
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


def test220_piicollection_dump_json(fix_timestamp):
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


def test300_piicollection_load_json(fix_timestamp):
    """Test JSON load"""

    obj = mod.PiiCollectionLoader()
    obj.load_json(fname('piicollection.json'))

    assert len(obj) == 2
    for pii in obj:
        assert isinstance(pii, PiiEntity)

    # Dump again to file
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            obj.dump(f, format='json')
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    # Check that the dumped file has the same data
    exp = readfile(fname('piicollection.json'))
    #print(json.loads(got))
    assert json.loads(exp) == json.loads(got)


def test310_piicollection_load_ndjson(fix_timestamp):
    """Test NDJSON load"""

    obj = mod.PiiCollectionLoader()
    with open(fname('piicollection.ndjson'), encoding='utf-8') as f:
        obj.load_ndjson(f)

    assert len(obj) == 2
    for pii in obj:
        assert isinstance(pii, PiiEntity)

    # Dump again to file
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            obj.dump(f, format='json')
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    # Check that the dumped file has the same data
    exp = readfile(fname('piicollection.json'))
    assert json.loads(exp) == json.loads(got)
