"""
Miscellaneous utilities
"""

import importlib

from typing import Union, Callable, Type, Dict

from .exception import ProcException


def import_object(objname: str) -> Union[Callable, Type]:
    """
    Import a Python object (a function or a class) given its fully qualified
    name
    """
    try:
        modname, oname = objname.rsplit(".", 1)
        mod = importlib.import_module(modname)
        return getattr(mod, oname)
    except Exception as e:
        raise ProcException("cannot import object '{}': {}", objname, e) from e


def filter_dict(d: Dict) -> Dict:
    """
    Return a streamlined version of a dict, without the `None` valued fields
    """
    return {k: v for k, v in d.items() if v is not None}
