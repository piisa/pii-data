"""
Enumeration that contains all defined PII element types
"""

from enum import Enum, auto


class PiiEnum(str, Enum):

    # Predefined types

    CREDIT_CARD = auto()
    BANK_ACCOUNT = auto()
    BITCOIN_ADDRESS = auto()

    IP_ADDRESS = auto()
    EMAIL_ADDRESS = auto()

    GOV_ID = auto()
    PHONE_NUMBER = auto()
    LICENSE_PLATE = auto()

    PERSON = auto()
    AGE = auto()
    BIRTH_DATE = auto()
    DEATH_DATE = auto()
    NORP = auto()               # Nationality, Religion or Political Group
    DISEASE = auto()

    STREET_ADDRESS = auto()


    # Fallback type
    OTHER = auto()
