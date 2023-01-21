"""
Test iteration peeker
"""

from pathlib import Path

import pytest

from pii_data.helper.exception import ConfigException

import pii_data.helper.peeker as mod

# ------------------------------------------------------------------------

def test100_peeker():
    """test iteration peeker"""

    n = range(11)
    currval = range(11)
    nextval = list(range(1, 11)) + [None]

    it = mod.IterationPeeker(n)
    for it_value, curr_value, next_value in zip(it, currval, nextval):
        assert it_value == curr_value
        assert it.peek() == next_value

    assert it_value == 10
