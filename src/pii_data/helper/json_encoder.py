"""
Provide a custom JSON encoder, able to serialize additional object types
"""

import sys
import datetime
import json
import base64
from collections.abc import Iterator


from typing import Union

def keygetter_set(v):
    return str(v).lower()


class CustomJSONEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that can serialize additional objects:
      - datetime objects (into ISO 8601 strings)
      - sets (as sorted lists)
      - iterators (as lists)
      - binary data as Base64 strings (or optionally skipped)
      - any object having a to_json() or as_dict() method

    Any other non-serializable object is converted to its string representation
    """

    def __init__(self, *args, binary: Union[bool, int] = True, **kwargs):
        """
          :param binary: if False, do not serialize binary data, but turn into
             a placeholder string. If an integer, use it as the size limit to
             activate placeholder. If `True` always serialize binary data
          All other arguments are passed to the parent class
        """
        self._binary = sys.maxsize if binary is True else int(binary)
        super().__init__(*args, **kwargs)


    def default(self, obj):
        """
        Serialize some special types
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, set):
            return sorted(obj, key=keygetter_set)
        elif hasattr(obj, 'to_json'):
            return obj.to_json()
        elif hasattr(obj, 'as_dict'):
            return obj.as_dict()
        elif isinstance(obj, Iterator):
            return list(obj)
        elif isinstance(obj, (bytes, bytearray)):
            size = len(obj)
            if size < self._binary:
                return base64.b64encode(obj).decode('ascii')
            else:
                return 'BinaryData size={}'.format(len(obj))

        # Else, use the parent class default, or if error, convert to string
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
