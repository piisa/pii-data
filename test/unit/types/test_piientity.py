
from pii_data.helper.exception import InvArgException
from pii_data.types.piienum import PiiEnum
import pii_data.types.piientity as mod

import pytest


def test10_object():
    """Test object creation"""
    obj = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert str(obj) == "<PiiEntity CREDIT_CARD:3412 2121 4121 4212>"

def test11_object_error():
    """Test object creation, errors"""
    with pytest.raises(TypeError):
        mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12")

    with pytest.raises(TypeError):
        mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15,
                      44)

def test12_object_kwargs():
    """Test object creation, kwargs"""
    obj = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 10,
                        lang="ch")
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


def test60_from_dict():
    """Test object from dict"""
    pii = {'type': 'CREDIT_CARD',
           'chunkid': '12',
           'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212',
           'lang': 'en'}
    got = mod.PiiEntity.from_dict(pii)

    exp = mod.PiiEntity(PiiEnum.CREDIT_CARD, "3412 2121 4121 4212", "12", 15)
    assert exp == got
    assert got.as_dict() == pii


def test61_from_dict_err():
    """Test object from dict, invalid dict"""
    pii = {'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212',
           'lang': 'en'}
    with pytest.raises(InvArgException):
        mod.PiiEntity.from_dict(pii)

def test62_from_dict_err():
    """Test object from dict, invalid dict"""
    pii = {'type': 'not a type',
           'end': 34,
           'start': 15,
           'value': '3412 2121 4121 4212',
           'lang': 'en'}
    with pytest.raises(InvArgException):
        mod.PiiEntity.from_dict(pii)
