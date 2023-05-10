
from pathlib import Path
import tempfile
import datetime
import json

from unittest.mock import Mock
import pytest

from pii_data.types.piienum import PiiEnum
from pii_data.types.piientity import PiiEntity
from pii_data.helper.json_encoder import CustomJSONEncoder

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


def test220_piicollection_fields(fix_timestamp):
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
    # Create a collection
    obj = mod.PiiCollection(lang="pt", docid="doc1")

    det = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")
    ent1 = PiiEntity.build(PiiEnum.GOV_ID, "12345678", "12", 15, country="br")
    ent2 = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234567890", chunk="30",
                           pos=60, country="br")
    obj.add(ent1, det)
    obj.add(ent2, det)
    assert len(obj) == 2

    exp = json.loads(readfile(fname('piicollection.json')))

    # JSON format, via dump method
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            obj.dump(f, format='json')
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    assert exp == json.loads(got)

    # JSON format, via direct serialization
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            json.dump(obj, f, cls=CustomJSONEncoder)
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    assert exp == json.loads(got)

    # JSONL
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f1:
            obj.dump(f1, format="ndjson")
        with open(f1.name, "rt", encoding="utf-8") as f2:
            meta = json.loads(f2.readline())
            pii = [json.loads(ln) for ln in f2]
    finally:
        Path(f1.name).unlink()

    assert exp == {"metadata": meta, "pii_list": pii}


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
    assert len(obj2.get_detectors()) == 1
    assert len(obj2) == 0

    for ent in obj1:
        obj2.add(ent)
    assert len(obj2) == 2
    assert len(obj2.get_detectors()) == 1

    # JSON format
    try:
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
            obj2.dump(f, format='json')
        got = readfile(f.name)
    finally:
        Path(f.name).unlink()

    exp = readfile(fname('piicollection.json'))
    assert json.loads(exp) == json.loads(got)


def test320_piicollection_add_detector(fix_timestamp):
    """Test clone"""
    obj1 = mod.PiiCollection(lang="pt", docid="doc1")
    assert len(obj1.get_detectors()) == 0

    det1 = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")

    obj1.add_detector(det1)
    assert len(obj1.get_detectors()) == 1

    obj1.add_detector(det1)
    assert len(obj1.get_detectors()) == 1

    det2 = mod.PiiDetector("PIISA", "PII Finder", "0.1.0")
    obj1.add_detector(det2)
    assert len(obj1.get_detectors()) == 1

    det3 = mod.PiiDetector("PIISA", "PII Finder", "0.1.1")
    obj1.add_detector(det3)
    assert len(obj1.get_detectors()) == 2

    r = obj1.add_detectors([det1, det3])
    assert r == 0
    assert len(obj1.get_detectors()) == 2

    det4 = mod.PiiDetector("PIISA", "PII Finder2", "0.1.0")
    r = obj1.add_detectors([det1, det3, det4])
    assert r == 1
    assert len(obj1.get_detectors()) == 3

    d = obj1.get_detector(1)
    assert d.asdict() == {'name': 'PII Finder', 'source': 'PIISA',
                          'version': '0.1.0'}

    exp = [{'name': 'PII Finder', 'source': 'PIISA', 'version': '0.1.0'},
           {'name': 'PII Finder', 'source': 'PIISA', 'version': '0.1.1'},
           {'name': 'PII Finder2', 'source': 'PIISA', 'version': '0.1.0'}]
    d = obj1.get_detectors()
    assert len(d) == 3
    assert d[1] == exp[0]
    assert d[2] == exp[1]
    assert d[3] == exp[2]

    d = obj1.get_detectors(asdict=False)
    assert len(d) == 3
    assert d[1].asdict() == exp[0]
    assert d[2].asdict() == exp[1]
    assert d[3].asdict() == exp[2]
