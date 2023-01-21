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
    """Test loading a module config, no specific format"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname)
    exp = {
        "blurb:v1": {
            'format': 'piisa:config:blurb:v1',
            'foo': 'bar',
            'foolist': [
                'elem1',
                'elem2'
            ],
            'foodict': {
                'bar1': None,
                'bar2': 40
            }
        }
    }
    assert exp == got


def test210_load_mod():
    """Test loading a module config, format"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname, "blurb:v1")
    exp = {
        "blurb:v1": {
            'format': 'piisa:config:blurb:v1',
            'foo': 'bar',
            'foolist': [
                'elem1',
                'elem2'
            ],
            'foodict': {
                'bar1': None,
                'bar2': 40
            }
        }
    }
    assert exp == got


def test220_load_mod():
    """Test loading a module config, format list"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname, ["blurb:v1", "blurb:v2"])
    exp = {
        "blurb:v1": {
            'format': 'piisa:config:blurb:v1',
            'foo': 'bar',
            'foolist': [
                'elem1',
                'elem2'
            ],
            'foodict': {
                'bar1': None,
                'bar2': 40
            }
        }
    }
    assert exp == got


def test230_load_mod():
    """Test loading a module config, no module config found"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname, "blurb:v2")
    exp = {}
    assert exp == got


def test300_load_full():
    """Test loading a full config"""

    fname = DATADIR / "full.json"
    for name in (fname, str(fname)):
        got = mod.load_config(fname)
        exp = {
            "blurb:v1": {
                "format": "piisa:config:blurb:v1",
                "blob": "abcd"
            },
            "blurb2:v1": {
                "format": "piisa:config:blurb2:v1",
                "foo": "bar",
                "foodict": {
                    "bar1": None,
                    "bar2": 43
                }
            }
        }
        assert exp == got


def test310_load_multi():
    """Test loading several configs"""

    config = DATADIR / "full.json", DATADIR / "blurb.json"
    got = mod.load_config(config)
    exp = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "blob": "abcd",
            "foo": "bar",
            'foolist': [
                'elem1',
                'elem2'
            ],
            "foodict": {
                "bar1": None,
                "bar2": 40
            }
        },
        "blurb2:v1": {
            "format": "piisa:config:blurb2:v1",
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got


def test320_load_multi_merge():
    """Test loading several configs, merge fields"""

    config = DATADIR / "full.json", DATADIR / "blurb.json", DATADIR / "blurb-add.json"
    got = mod.load_config(config)
    exp = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "blob": "abcd",
            "foo": "bar2",
            "foolist": [
                "elem1",
                "elem2",
                "elem2"
            ],
            "foodict": {
                "bar1": None,
                "bar2": 50,
                "bar3": ["elem"]
            }
        },
        "blurb2:v1": {
            "format": "piisa:config:blurb2:v1",
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    #print("GOT", got, "EXP", exp, sep="\n")
    assert exp == got


def test330_load_multi_merge_add_dict():
    """Test loading several configs, merge fields, additional loaded config"""

    data = mod.load_config(DATADIR / "blurb-add.json")

    config = DATADIR / "full.json", DATADIR / "blurb.json", data
    got = mod.load_config(config)
    exp = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "blob": "abcd",
            "foo": "bar2",
            "foolist": [
                "elem1",
                "elem2",
                "elem2"
            ],
            "foodict": {
                "bar1": None,
                "bar2": 50,
                "bar3": ["elem"]
            }
        },
        "blurb2:v1": {
            "format": "piisa:config:blurb2:v1",
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got


def test340_load_multi_merge_add():
    """Test loading several configs, merge fields, additional config"""

    data = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "foolist": ["elem5"],
            "foodict": {
                "bar1": 33
            }
        }
    }
    configlist = (DATADIR / "full.json", DATADIR / "blurb.json",
                  str(DATADIR / "blurb-add.json"), data)
    got = mod.load_config(configlist)
    exp = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "blob": "abcd",
            "foo": "bar2",
            "foolist": [
                "elem1",
                "elem2",
                "elem2",
                "elem5"
            ],
            "foodict": {
                "bar1": 33,
                "bar2": 50,
                "bar3": ["elem"]
            }
        },
        "blurb2:v1": {
            "format": "piisa:config:blurb2:v1",
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got


def test350_load_multi_error():
    """Test loading several configs, merge error"""

    config = DATADIR / "blurb.json", DATADIR / "error3.json"
    with pytest.raises(ConfigException) as excinfo:
        mod.load_config(config)
    assert f"cannot merge config '{DATADIR / 'error3.json'}': unsupported operand type(s) for +=: 'dict' and 'list'" == str(excinfo.value)


def test500_load_single_config():
    """Test loading a single config section"""

    data = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "foolist": ["elem5"],
            "foodict": {
                "bar1": 33
            }
        }
    }
    configlist = (DATADIR / "blurb.json", str(DATADIR / "blurb-add.json"), data)
    got = mod.load_single_config(DATADIR / "full.json", "blurb:v1", configlist)
    print("GOT", got)
    exp = {
        'format': 'piisa:config:blurb:v1',
        'blob': 'abcd',
        'foo': 'bar2',
        'foolist': ['elem1', 'elem2', 'elem2', 'elem5'],
        'foodict': {'bar1': 33, 'bar2': 50, 'bar3': ['elem']}
    }
    assert exp == got
