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

        self.type = ptype
        self.fields = {'type': ptype.name, 'value': value, 'chunkid': chunk}
        self.pos = pos

        for k in ('subtype', 'lang', 'country', 'docid'):
            v = kwargs.pop(k, None)
            if v:
                self.fields[k] = v


    def __len__(self):
        return len(self.fields['value'])


    def __repr__(self):
        return f"<PiiEntity {self.fields['type']}:{self.fields['value']}>"


    def __eq__(self, other):
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
