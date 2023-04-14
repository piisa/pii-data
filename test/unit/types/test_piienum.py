
from pii_data.helper.exception import InvArgException
from pii_data.types import PiiEnum, PiiEntityInfo
import pii_data.types.piienum as mod



def test10_object():
    """Test object creation"""
    pii = mod.PiiEnum.CREDIT_CARD
    assert str(pii) == "PiiEnum.CREDIT_CARD"


def test20_value():
    """Test object value"""
    pii = mod.PiiEnum.CREDIT_CARD
    assert pii.name == "CREDIT_CARD"
    assert pii.value == 1


def test30_access():
    """Test object access"""
    pii = mod.PiiEnum(1)
    assert pii == mod.PiiEnum.CREDIT_CARD
    pii = mod.PiiEnum["CREDIT_CARD"]
    assert pii == mod.PiiEnum.CREDIT_CARD


def test40_list():
    """Test all defined values"""
    names = ["CREDIT_CARD", "BANK_ACCOUNT", "BLOCKCHAIN_ADDRESS",
             "IP_ADDRESS", "EMAIL_ADDRESS", "USERNAME", "PHONE_NUMBER",
             "LICENSE_PLATE", "GOV_ID", "PASSWORD", "KEY", "PERSON",
             "LOCATION", "AGE", "DATE", "NORP", "MEDICAL", "ORG", "OTHER"]
    for n, name in enumerate(names, start=1):
        assert mod.PiiEnum[name] == mod.PiiEnum(n)


def test100_alias():
    """Test aliases"""
    assert mod.PiiEnum["STREET_ADDRESS"] == mod.PiiEnum.LOCATION
