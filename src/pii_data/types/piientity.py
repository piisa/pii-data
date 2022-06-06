"""
A class to define the contents of a detected PII entity
"""

from .piienum import PiiEnum

from typing import Dict


class PiiEntity:
    """
    A detected PII entity. It contains as fields:
      * elem, a PiiEnum that describes the type of the detected PII
      * pos, the character position of the PII inside the passed document
      * value, the string containing the PII
      * country, the country this PII is applicable to (or None)
      * name, an optional specific name for this PII
    """

    __slots__ = "type", "fields", "pos"

    def __init__(self, ptype: PiiEnum, value: str,
                 chunk: str, pos: int, **kwargs):
        """
          :param ptype: PII type
          :param value: the extracted PII string
          :param chunk: the id for the chunk the PII is in
          :param pos: position of the PII in the chunk
        Additional optional arguments are: `subtype`, `lang`, `country` and
        `docid`
        """
        # Compulsory arguments
        self.type = ptype
        self.fields = {'type': ptype.name, 'value': value, 'chunkid': chunk}
        self.pos = pos

        # Optional arguments
        for k in ('subtype', 'lang', 'country', 'docid'):
            v = kwargs.pop(k, None)
            if v:
                self.fields[k] = v


    def __len__(self):
        """
        Return the size of the PII string
        """
        return len(self.fields['value'])


    def __repr__(self) -> str:
        return f"<PiiEntity {self.fields['type']}:{self.fields['value']}>"


    def __eq__(self, other: "PiiEntity") -> bool:
        return (all(self.fields[f] == other.fields[f]
                    for f in ('type', 'value', 'chunkid'))
                and self.pos == other.pos)


    def as_dict(self) -> Dict:
        """
        Return the object data as a dict that can then be serialised as JSON
        """
        self.fields['start'] = self.pos
        self.fields['end'] = self.pos + len(self)
        return self.fields
