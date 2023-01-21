
from pathlib import Path
import tempfile
import json


from pii_data.types.piientity import PiiEntity

import pii_data.types.piicollection.loader as mod


def fname(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def readfile(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read().strip()



# ----------------------------------------------------------------

def test300_piicollection_load_json():
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


def test310_piicollection_load_ndjson():
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
