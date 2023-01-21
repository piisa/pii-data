"""
Loading PIISA configuration files

A configuration file is either:
 * a _module_ config file, carrying configuration for one PIISA module
 * a _full_ config fille, carrying configuration for all (or many) PIISA
   modules from different packages
"""

from collections import defaultdict
from pathlib import Path

from typing import List, Dict, Union, Set, Optional, Tuple

from ..defs import FMT_CONFIG_PREFIX, FMT_CONFIG_FULL
from .exception import ConfigException, ProcException
from .io import load_datafile


TYPE_CONFIG = Union[Dict, str]
TYPE_CONFIG_LIST = Union[TYPE_CONFIG, List[TYPE_CONFIG]]


def config_section(data: Dict, formats: Set[str],
                   filename: str) -> Optional[Tuple[str, Dict]]:
    """
    Parse a config module
    """
    # Fetch format
    fmt = data.get("format")
    if not fmt:
        raise ConfigException("format spec not in config '{}'", filename)

    # Check format string
    if not fmt.startswith(FMT_CONFIG_PREFIX):
        raise ConfigException("invalid format spec '{}' in config '{}'",
                              fmt, filename)
    elif formats and fmt not in formats:
        return

    tag = fmt[len(FMT_CONFIG_PREFIX):]
    return tag, data



def read_config_file(filename: str,
                     formats: List[str] = None) -> Dict:
    """
    Read a configuration file (JSON or YAML)
      :param filename: name of file to read
      :param formats: list of acceptable configuration formats (in addition
         to the "full" config format, which is always accepted)
    """
    data = load_datafile(filename)

    # Check format
    if "format" not in data:
        raise ConfigException("format spec not in config '{}'", filename)
    fmt = data["format"]

    # Extract matching configs
    if fmt == FMT_CONFIG_FULL:
        # Process a full config
        cfg = [config_section(config, formats, filename)
               for config in data.get("config", [])]
    else:
        # Process a module config
        cfg = [config_section(data, formats, filename)]

    return dict(c for c in cfg if c)


def merge_config(configdata: Dict[str, Dict]) -> Dict:
    """
    Merge a number of configurations
    """
    config = defaultdict(lambda: defaultdict(dict))
    for sname, data in configdata.items():
        for tag, elem in data.items():
            for k, v in elem.items():
                d = config[tag]
                try:
                    if k not in d:
                        d[k] = v
                    elif isinstance(v, dict):
                        d[k].update(v)
                    elif isinstance(v, list):
                        d[k] += v
                    else:
                        d[k] = v
                except Exception as e:
                    raise ConfigException("cannot merge config '{}': {}",
                                          sname, e) from e
    return config


def load_config(configlist: TYPE_CONFIG_LIST,
                formats: List[str] = None) -> Dict:
    """
    Load & combine PIISA configuration files
      :param filename: config filename(s) to load, or already.loaded config
         dictionaries
      :param formats: restrict the loaded formats to those (a "full" format
         is always accepted, and the valid module sections in it retained)
      :return: a dictionary with the config data, indexed by config section
    """
    if isinstance(configlist, (str, Path, Dict)):
        configlist = [configlist]
    if formats:
        if isinstance(formats, str):
            formats = [formats]
        formats = set(f if f.startswith(FMT_CONFIG_PREFIX)
                      else FMT_CONFIG_PREFIX+f for f in formats)

    # Read all config files
    config_dict = {}
    for n, f in enumerate(configlist, start=1):

        # An already loaded config?
        if isinstance(f, dict):
            config_dict[f"config#{n}"] = f
            continue

        # Read config data
        try:
            config_dict[str(f)] = read_config_file(f, formats)
        except ProcException:
            raise
        except Exception as e:
            raise ConfigException("cannot process config '{}': {}", f, e) from e

    # Merge config information
    return merge_config(config_dict)


def load_single_config(base: Union[str, Path], format: str,
                       configlist: TYPE_CONFIG_LIST = None) -> Dict:
    """
    Read a configuration for a single module
     :param base: filename containing the base configuration
     :param format: config section to read
     :param configlist: optional list of additional configurations to add
    """

    # Ensure configlist is a list
    if not configlist:
        configlist = []
    elif isinstance(configlist, (str, Path, dict)):
        configlist = [configlist]

    # Load configuration
    config = load_config([base]+list(configlist), format)

    # Fetch the part we want
    return config.get(format, {})
