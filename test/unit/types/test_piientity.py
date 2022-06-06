
from pii_data.types.piienum import PiiEnum
import pii_data.types.piientity as mod



def test10_object():
    """Test object creation"""
    obj = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert str(obj) == "<PiiEntity CREDIT_CARD:3412 2121 4121 4212>"


def test20_values():
    """Test object values"""
    obj = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert len(obj) == 19


def test30_eq():
    """Test object equality"""
    obj = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)

    obj2 = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert obj == obj2

    obj2 = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 14)
    assert obj != obj2

    obj2 = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "10", 15)
    assert obj != obj2

    obj2 = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 421x", "12", 15)
    assert obj != obj2

    obj2 = mod.PiiEntity(PiiEnum.GOV_ID, "3412 2121 4121 4212", "12", 15)
    assert obj != obj2


def test40_dict():
    """Test object as dict"""
    obj = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    exp = {'type': 'CREDIT_CARD',
           'chunkid': '12',
           'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212'}

    assert obj.as_dict() == exp


def test50_dict_extra():
    """Test object as dict, extra fields"""
    obj = mod.PiiEntity(PiiEnum.GOV_ID, "12345678", "12", 15,
                        subtype="SSN", country="us", lang="en")
    exp = {'type': 'GOV_ID',
           'chunkid': '12',
           'end': 23,
           'start': 15,
           'value': '12345678',
           'country': 'us',
           'lang': 'en',
           'subtype': 'SSN'}


    assert obj.as_dict() == exp
