
from pii_data.helper.exception import InvArgException
from pii_data.types import PiiEnum, PiiEntityInfo
import pii_data.types.piientity as mod

import pytest


def test10_object():
    """Test object creation"""
    info = mod.PiiEntityInfo(PiiEnum.CREDIT_CARD, "any")
    obj = mod.PiiEntity(info, "3412 2121 4121 4212", "12", 15)
    assert str(obj) == "<PiiEntity CREDIT_CARD:3412 2121 4121 4212>"

def test11_object():
    """Test object creation, build"""
    obj = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert str(obj) == "<PiiEntity CREDIT_CARD:3412 2121 4121 4212>"


def test20_object_error():
    """Test object creation, errors"""
    # Missing "pos"
    with pytest.raises(TypeError):
        mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12")

    # Invalid PII type
    with pytest.raises(InvArgException):
        mod.PiiEntity.build("NOT_A_VALID_PII", "3412 2121 4121 4212", "12", 15)


def test21_object_kwargs():
    """Test object creation, kwargs"""
    obj = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12",
                              10, lang="ch")
    assert str(obj) == "<PiiEntity CREDIT_CARD:3412 2121 4121 4212>"


def test22_object_str():
    """Test object creation, type as string"""
    obj = mod.PiiEntity.build("CREDIT_CARD", "3412 2121 4121 4212", "12", 10,
                              lang="ch")
    assert str(obj) == "<PiiEntity CREDIT_CARD:3412 2121 4121 4212>"


def test30_values():
    """Test object values"""
    obj = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212",
                              "12", 15)
    assert obj.info == PiiEntityInfo(PiiEnum.CREDIT_CARD, None)
    assert obj.fields == {"value": "3412 2121 4121 4212", "chunkid": "12",
                          "type": "CREDIT_CARD"}
    assert obj.pos == 15
    assert len(obj) == 19


def test40_eq():
    """Test object equality"""
    obj = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)

    obj2 = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert obj == obj2

    obj2 = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 14)
    assert obj != obj2

    obj2 = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "10", 15)
    assert obj != obj2

    obj2 = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 421x", "12", 15)
    assert obj != obj2

    obj2 = mod.PiiEntity.build(PiiEnum.GOV_ID, "3412 2121 4121 4212", "12", 15)
    assert obj != obj2


def test50_dict():
    """Test object as dict"""
    obj = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    exp = {'type': 'CREDIT_CARD',
           'chunkid': '12',
           'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212'}

    assert obj.asdict() == exp


def test51_dict_extra():
    """Test object as dict, extra fields"""
    obj = mod.PiiEntity.build(PiiEnum.GOV_ID, "12345678", "12", 15,
                              subtype="SSN", country="us", lang="en")
    exp = {'type': 'GOV_ID',
           'chunkid': '12',
           'end': 23,
           'start': 15,
           'value': '12345678',
           'country': 'us',
           'lang': 'en',
           'subtype': 'SSN'}


    assert obj.asdict() == exp


def test60_from_dict():
    """Test object from dict"""
    pii = {'type': 'CREDIT_CARD',
           'chunkid': '12',
           'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212',
           'lang': 'en'}
    got = mod.PiiEntity.fromdict(pii)

    exp = mod.PiiEntity.build(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert exp == got
    assert got.asdict() == pii


def test61_from_dict_err():
    """Test object from dict, invalid dict"""
    pii = {'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212',
           'lang': 'en'}
    with pytest.raises(InvArgException):
        mod.PiiEntity.fromdict(pii)

def test62_from_dict_err():
    """Test object from dict, invalid dict"""
    pii = {'type': 'not a type',
           'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212',
           'lang': 'en'}
    with pytest.raises(InvArgException):
        mod.PiiEntity.fromdict(pii)
