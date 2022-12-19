"""
Loading PIISA configuration files

A configuration file is either:
 * a _module_ config file, carrying configuration for one PIISA module
 * a _full_ config fille, carrying configuration for all (or many) PIISA
   modules from different packages
"""

from collections import defaultdict
from pathlib import Path

from typing import List, Dict, Union

from ..defs import FMT_CONFIG_PREFIX, FMT_CONFIG_FULL
from .exception import ConfigException, ProcException
from .io import load_datafile


TYPE_CONFIG = Union[str, List[str]]


def read_config_file(filename: str, formats: List[str] = None) -> Dict:
    """
    Read a configuration file (JSON or YAML)
      :param filename: name of file to read
      :param formats: list of acceptable configuration formats (in addition
         to the "full" config format, which is always accepted)
    """
    data = load_datafile(filename)

    # Check format; return full configs unmodified
    if "format" not in data:
        raise ConfigException("format spec not in config '{}'", filename)
    fmt = data["format"]
    if fmt == FMT_CONFIG_FULL:
        return data

    # Check format string
    if not fmt.startswith(FMT_CONFIG_PREFIX):
        raise ConfigException("invalid format spec '{}' in config '{}'",
                              fmt, filename)
    elif formats and fmt not in formats:
        raise ConfigException("unexpected format spec '{}' in config '{}'",
                              fmt, filename)

    # Return module config
    tag = fmt[len(FMT_CONFIG_PREFIX):]
    return {tag: data}


def load_config(filename: TYPE_CONFIG, formats: List[str] = None) -> Dict:
    """
    Load a PIISA configuration file, or a sequence of them
      :param filename: config filename(s) to load
      :param formats: restrict the accepted formats to those (in addition to
         the "full" format, which is always accepted)
      :return: a dictionary with the config data, indexed by config format
    """
    if isinstance(filename, (str, Path)):
        filename = [filename]

    # Read all config files
    config = defaultdict(dict)
    for f in filename:

        # Read config file
        try:
            data = read_config_file(f)
        except ProcException:
            raise
        except Exception as e:
            raise ConfigException("cannot process config '{}': {}", f, e) from e

        # Add to config data
        for tag, v in data.items():
            if tag == "format":
                config[tag] = v
            else:
                config[tag].update(v)

    return config
