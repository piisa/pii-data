"""
Test reading config files
"""

from pathlib import Path

import pytest

from pii_data.helper.exception import ConfigException

import pii_data.helper.config as mod


DATADIR = Path(__file__).parents[2] / "data" / "config"


# ------------------------------------------------------------------------

def test100_load_error():
    """Test loading a config with errors"""

    fname = DATADIR / "error1.json"
    with pytest.raises(ConfigException) as excinfo:
        mod.load_config(fname)
    assert f"format spec not in config '{fname}'" == str(excinfo.value)

    fname = DATADIR / "error2.json"
    with pytest.raises(ConfigException) as excinfo:
        mod.load_config(fname)
    assert f"invalid format spec 'piisa:foo:blurb:v1' in config '{fname}'" \
        == str(excinfo.value)


def test200_load_mod():
    """Test loading a module config"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname)
    exp = {
        "blurb": {
            'format': 'piisa:config:blurb:v1',
            'foo': 'bar',
            'foodict': {
                'bar1': None,
                'bar2': 40
            }
        }
    }
    assert exp == got


def test200_load_full():
    """Test loading a full config"""

    fname = DATADIR / "full.json"
    for name in (fname, str(fname)):
        got = mod.load_config(fname)
        exp = {
            "format": "piisa:config:full:v1",
            "blurb": {
                "format": "piisa:config:blurb:v1",
                "blob": "abcd"
            },
            "blurb2": {
                "format": "piisa:config:blurb2:v1",
                "foo": "bar",
                "foodict": {
                    "bar1": None,
                    "bar2": 43
                }
            }
        }
        assert exp == got


def test300_load_multi():
    """Test loading several configs"""

    config = DATADIR / "full.json", DATADIR / "blurb.json"
    got = mod.load_config(config)
    exp = {
        "format": "piisa:config:full:v1",
        "blurb": {
            "format": "piisa:config:blurb:v1",
            "blob": "abcd",
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 40
            }
        },
        "blurb2": {
            "format": "piisa:config:blurb2:v1",
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got
