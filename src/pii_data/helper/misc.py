"""
Miscellaneous utilities
"""

import importlib

from typing import Union, Callable, Type

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
