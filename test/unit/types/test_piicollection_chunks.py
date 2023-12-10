
from pathlib import Path
from itertools import zip_longest

from pii_data.types.piicollection.loader import PiiCollectionLoader

from pii_data.types.piienum import PiiEnum


import pii_data.types.piicollection.chunk as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name

def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()



# ----------------------------------------------------------------

def test100_constructor():
    """Test object creation"""
    piic = PiiCollectionLoader()
    piic.load_json(fname('piicollection_it.json'))

    obj = mod.PiiChunkIterator(piic)
    assert str(obj) == "<PiiChunkIterator #5>"


def test110_iterate():
    """Test object iteration, continuous"""

    piic = PiiCollectionLoader()
    piic.load_json(fname('piicollection_it.json'))

    exp = [
        [PiiEnum.GOV_ID],
        [PiiEnum.CREDIT_CARD, PiiEnum.PHONE_NUMBER],
        [PiiEnum.BANK_ACCOUNT, PiiEnum.IP_ADDRESS]
    ]

    # Explicit method
    obj = mod.PiiChunkIterator(piic)
    for exp_pii, got in zip_longest(exp, obj.chunks()):
        got_pii = [p.info.pii for p in got]
        assert exp_pii == got_pii

    # Use as iterator
    obj = mod.PiiChunkIterator(piic)
    for exp_pii, got in zip_longest(exp, obj):
        got_pii = [p.info.pii for p in got]
        assert exp_pii == got_pii


def test120_iterate_chunk():
    """Test object iteration, by chunk"""

    piic = PiiCollectionLoader()
    piic.load_json(fname('piicollection_it.json'))

    chunks = ("12", "30", "50")
    exp = [
        [PiiEnum.GOV_ID],
        [PiiEnum.CREDIT_CARD, PiiEnum.PHONE_NUMBER],
        [PiiEnum.BANK_ACCOUNT, PiiEnum.IP_ADDRESS]
    ]

    obj = mod.PiiChunkIterator(piic)
    for exp_pii, chunk_id in zip_longest(exp, chunks):
        got_pii = [p.info.pii for p in obj(chunk_id)]
        assert exp_pii == got_pii
