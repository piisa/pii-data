"""
Loading PIISA configuration files

A configuration file is either:
 * a _module_ config file, carrying configuration for one PIISA module
 * a _full_ config fille, carrying configuration for all (or many) PIISA
   modules from different packages
"""

from collections import defaultdict
from pathlib import Path

from typing import List, Dict, Union, Set, Optional, Tuple, Iterable

from ..defs import FMT_CONFIG_PREFIX, FMT_CONFIG_FULL
from .exception import ConfigException, ProcException
from .io import load_datafile


TYPE_CONFIG = Union[Dict, str]
TYPE_CONFIG_LIST = Union[TYPE_CONFIG, List[TYPE_CONFIG]]


def config_section(data: Dict, formats: Set[str],
                   filename: str) -> Optional[Tuple[str, Dict]]:
    """
    Parse one config section (i.e. the config for a module)
    """
    # Fetch format
    fmt = data.get("format")
    if not fmt:
        raise ConfigException("format spec missing in config: {}", filename)

    # Check format string
    if not fmt.startswith(FMT_CONFIG_PREFIX):
        raise ConfigException("invalid format spec '{}' in config: {}",
                              fmt, filename)
    elif formats and fmt not in formats:
        # Check if we want this format, but another version
        fmt_f, fmt_v = fmt.rsplit(':', 1)
        for tfmt in formats:
            tfmt_f, tmft_v = tfmt.rsplit(':', 1)
            if tfmt_f == fmt_f:
                raise ConfigException("version '{}' unsupported for format '{}' in: {}", fmt_v, fmt_f, filename)
        return

    # Add filename, if the config does not have a name
    if "name" not in data:
        data["name"] = str(filename)

    # Build the tag and return the config
    tag = fmt[len(FMT_CONFIG_PREFIX):]
    return tag, data



def read_config_file(filename: str,
                     formats: List[str] = None) -> Dict:
    """
    Read a single configuration file (JSON or YAML)
      :param filename: name of file to read
      :param formats: list of acceptable configuration formats (in addition
         to the "full" config format, which is always accepted)
    """
    data = load_datafile(filename)

    # Check format
    if "format" not in data:
        raise ConfigException("format spec missing in config: {}", filename)
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


def merge_config(configdata: Iterable[Dict]) -> Dict:
    """
    Merge a number of configurations
     :param configdata: configuration dictionaries to merge, as an iterable of
       dicts. Each dict contains `{configsection: configdata}` sections
     :return: the merged config, again as a dict

    Configuration sections will be merged in the order they appear in the
    iterable; fields in later configs will override existing ones (if they are
    scalars), update them (if they are dicts) or append to them (if they are
    lists).
    """
    out_config = defaultdict(lambda: defaultdict(dict))
    for sourcedata in configdata:


        for section, config in sourcedata.items():
            dest = out_config[section]
            for k, v in config.items():
                try:
                    if k not in dest:
                        dest[k] = v
                    elif isinstance(v, dict):
                        dest[k].update(v)
                    elif isinstance(v, list):
                        dest[k] += v
                    elif k == "name":
                        dest[k] = [dest[k], v] if isinstance(dest[k], str) else dest[k] + [v]
                    else:
                        dest[k] = v
                except Exception as e:
                    raise ConfigException("cannot merge config '{}': {}",
                                          config.get("name"), e) from e
    return out_config


def load_config(configlist: TYPE_CONFIG_LIST,
                formats: List[str] = None) -> Dict:
    """
    Load & combine PIISA configuration files
      :param filename: config filename(s) to load, or already loaded config
         dictionaries
      :param formats: restrict the formats to load (a "full" format
         is always read, and the valid module sections in it retained)
      :return: a single dictionary with the config data, indexed by config
         section, i.e. a dictionary {configsection: configdata}
    """
    # Sanitize input arguments
    if configlist is None:
        configlist = []
    elif isinstance(configlist, (str, Path, Dict)):
        configlist = [configlist]
    if formats:
        if isinstance(formats, str):
            formats = [formats]
        formats = set(f if f.startswith(FMT_CONFIG_PREFIX)
                      else FMT_CONFIG_PREFIX+f for f in formats)

    # Read all config files and build a list of configurations
    config_data = []
    for f in configlist:

        # An already loaded config?
        if isinstance(f, dict):
            config_data.append(f)
            continue

        # Read config data
        try:
            data = read_config_file(f, formats)
            config_data.append(data)
        except ProcException:
            raise
        except Exception as e:
            raise ConfigException("cannot process config '{}': {}", f, e) from e

    # Merge all read configurations
    return merge_config(config_data)


def load_single_config(base: Union[str, Path], format: str,
                       configlist: TYPE_CONFIG_LIST = None) -> Dict:
    """
    Read the configuration for a single module
     :param base: filename containing a base (default) configuration
     :param format: config section to read
     :param configlist: optional list of additional configurations to add
     :return: the module config
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
