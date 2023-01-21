"""
Enumeration that contains all defined PII element types
"""

from enum import Enum, auto


class PiiEnum(str, Enum):

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
    AGE = auto()
    DATE = auto()               # A PII-related date (eg birth date, death date)
    NORP = auto()               # Nationality or Religion or Political Group
    MEDICAL = auto()            # Medical records
    ORG = auto()                # organization or institution
    STREET_ADDRESS = auto()

    # Fallback type
    OTHER = auto()
