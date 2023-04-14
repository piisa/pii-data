"""
Enumeration that contains all defined PII element types
"""

from enum import IntEnum, auto


class PiiEnum(IntEnum):

    CREDIT_CARD = auto()
    BANK_ACCOUNT = auto()
    BLOCKCHAIN_ADDRESS = auto()

    IP_ADDRESS = auto()
    EMAIL_ADDRESS = auto()
    USERNAME = auto()           # a username or user handler

    PHONE_NUMBER = auto()
    LICENSE_PLATE = auto()
    GOV_ID = auto()             # Government-issued ID (SSN, NIF, etc)

    PASSWORD = auto()           # an access password
    KEY = auto()                # a software key (e.g. SSH key or DB access key)

    PERSON = auto()             # a person name
    LOCATION = auto()           # physical address
    AGE = auto()                # person age
    DATE = auto()               # A PII-related date (eg birth date, death date)
    NORP = auto()               # Nationality or Religion or Political Group
    MEDICAL = auto()            # medical records
    ORG = auto()                # organization or institution

    # Fallback type
    OTHER = auto()

    # Old name
    STREET_ADDRESS = LOCATION
