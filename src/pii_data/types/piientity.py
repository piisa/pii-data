"""
A class to define the contents of a detected PII entity
"""

from ..helper.exception import InvArgException
from .piienum import PiiEnum

from typing import Dict, Any


class PiiEntity:
    """
    A detected PII entity. It contains as fields:
      * type, a PiiEnum that describes the type of the detected PII
      * fields: a dictionary holding the PII info
      * pos, the character position of the PII inside the passed document
    """

    __slots__ = "type", "fields", "pos"

    def __init__(self, ptype: PiiEnum, value: str,
                 chunk: str, pos: int, **kwargs):
        """
          :param ptype: PII type
          :param value: the extracted PII string
          :param chunk: the id for the chunk the PII is in
          :param pos: position of the PII in the chunk
        Additional optional arguments are: `subtype`, `lang`, `country`,
        `docid`, `detector`
        """
        # Compulsory arguments
        self.type = ptype
        self.fields = {'type': ptype.name, 'value': value, 'chunkid': chunk}
        self.pos = pos

        # Optional arguments
        for k in ('subtype', 'lang', 'country', 'docid', 'detector'):
            v = kwargs.get(k)
            if v is not None:
                self.fields[k] = v


    def __len__(self):
        """
        Return the size of the PII string
        """
        return len(self.fields['value'])


    def __repr__(self) -> str:
        return f"<PiiEntity {self.fields['type']}:{self.fields['value']}>"


    def __eq__(self, other: "PiiEntity") -> bool:
        """
        Decide on equality of two entities: same type, value, chunkid & pos
        """
        return (all(self.fields[f] == other.fields[f]
                    for f in ('type', 'value', 'chunkid'))
                and self.pos == other.pos)


    def add_field(self, name: str, value: Any):
        """
        Add a field to the entity
        """
        self.fields[name] = value


    def as_dict(self) -> Dict:
        """
        Return the object data as a dict that can then be serialised as JSON
        """
        self.fields['start'] = self.pos
        self.fields['end'] = self.pos + len(self)
        return self.fields


    @classmethod
    def from_dict(cls, src: Dict) -> "PiiEntity":
        """
        Create an object from a dictionary
        """
        src = src.copy()
        # Main elements
        try:
            ptype = src.pop("type")
            pos = src.pop("start")
            value = src.pop("value")
            chunkid = src.pop("chunkid")
        except KeyError as e:
            raise InvArgException("missing field in PiiEntity dict: {}", e)
        # Define type
        try:
            pii_type = PiiEnum[ptype]
        except KeyError as e:
            raise InvArgException("unknown PiiEnum value: {}", e)
        # Create
        return PiiEntity(pii_type, value, chunkid, pos, **src)
