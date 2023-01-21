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
    assert f"format spec missing in config: {fname}" == str(excinfo.value)

    fname = DATADIR / "error2.json"
    with pytest.raises(ConfigException) as excinfo:
        mod.load_config(fname)
    assert f"invalid format spec 'piisa:foo:blurb:v1' in config: {fname}" \
        == str(excinfo.value)


def test200_load_mod():
    """Test loading a module config, no specific format"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname)
    exp = {
        "blurb:v1": {
            'name': str(fname),
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
    """Test loading a module config, specify format"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname, "blurb:v1")
    exp = {
        "blurb:v1": {
            'name': str(fname),
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
    """Test loading a module config, specify a format list"""

    fname = DATADIR / "blurb.json"
    got = mod.load_config(fname, ["blurb:v1", "blurb:v2"])
    exp = {
        "blurb:v1": {
            'name': str(fname),
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
    got = mod.load_config(fname, "anotherblurb:v2")
    exp = {}
    assert exp == got


def test240_load_mod():
    """Test loading a module config, invalid format version"""

    fname = DATADIR / "blurb.json"
    with pytest.raises(ConfigException) as excinfo:
        mod.load_config(fname, "blurb:v2")
    assert f"version 'v1' unsupported for format 'piisa:config:blurb' in: {fname}" == str(excinfo.value)


def test300_load_full():
    """Test loading a full config"""

    fname = DATADIR / "full.json"
    for name in (fname, str(fname)):
        got = mod.load_config(fname)
        exp = {
            "blurb:v1": {
                "format": "piisa:config:blurb:v1",
                "name": str(fname),
                "blob": "abcd"
            },
            "blurb2:v1": {
                "format": "piisa:config:blurb2:v1",
                "name": str(fname),
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
            'name': [str(config[0]), str(config[1])],
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
            'name': str(config[0]),
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
            "name": [str(c) for c in config],
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
            "name": str(config[0]),
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got


def test330_load_multi_merge_add_dict():
    """Test loading several configs, merge fields, additional loaded config"""

    data = mod.load_config(DATADIR / "blurb-add.json")

    config = DATADIR / "full.json", DATADIR / "blurb.json", data
    got = mod.load_config(config)
    exp = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "name": [str(config[0]), str(config[1]),
                     str(DATADIR / "blurb-add.json")],
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
            "name": str(config[0]),
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got


def test340_load_multi_merge_add():
    """Test loading several configs, merge fields, additional dict config"""

    data = {
        "blurb:v1": {
            "format": "piisa:config:blurb:v1",
            "name": "a name",
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
            "name": [str(c) for c in configlist[:3]] + ["a name"],
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
            "name": str(configlist[0]),
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got


def test350_load_multi_merge_add_no_name():
    """
    Test loading several configs, merge fields, additional dict config, no name
    """

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
            "name": [str(c) for c in configlist[:3]],
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
            "name": str(configlist[0]),
            "foo": "bar",
            "foodict": {
                "bar1": None,
                "bar2": 43
            }
        }
    }
    assert exp == got


def test360_load_multi_error():
    """Test loading several configs, merge error"""

    config = DATADIR / "blurb.json", DATADIR / "error3.json"
    with pytest.raises(ConfigException) as excinfo:
        mod.load_config(config)
    assert f"cannot merge config '{DATADIR / 'error3.json'}': unsupported operand type(s) for +=: 'dict' and 'list'" == str(excinfo.value)


def test500_load_single_config():
    """Test loading a single config section from the sources"""

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
    exp = {
        'format': 'piisa:config:blurb:v1',
        "name": [str(DATADIR / "full.json")] + [str(c) for c in configlist[:2]],
        'blob': 'abcd',
        'foo': 'bar2',
        'foolist': ['elem1', 'elem2', 'elem2', 'elem5'],
        'foodict': {'bar1': 33, 'bar2': 50, 'bar3': ['elem']}
    }
    #import json; print(json.dumps(got, indent=2))
    assert exp == got
