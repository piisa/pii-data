"""
A class to define the contents of a detected PII entity
"""

from dataclasses import dataclass

from ..helper.exception import InvArgException
from ..helper.misc import filter_dict
from .piienum import PiiEnum

from typing import Dict, Any, Union


# --------------------------------------------------------------------------

@dataclass(order=True, frozen=True)
class PiiEntityInfo:
    """
    Fixed fields in a PII entity instance
    """
    pii: PiiEnum
    lang: str
    country: str = None
    subtype: str = None

    def asdict(self) -> Dict:
        """
        Return as a dictionary, but without the empty fields
        """
        d = {"type": self.pii.name, "lang": self.lang, "country": self.country,
             "subtype": self.subtype}
        return filter_dict(d)


# --------------------------------------------------------------------------

# Optional fields in the PII instance, in addition to type, value & chunkid
# - docid: id for the document the PII belongs to
# - detector: detector that was used to extract it
# - process: current processing stage the PII is in
# - extra: any other additional information to supply (typically a dict)
FIELDS_OPTIONAL = "docid", "detector", "process", "extra"

TYPE_PTYPE = Union[PiiEnum, str]


class PiiEntity:
    """
    A detected PII entity. It contains as attributes:
      * type: a PiiEnum that describes the type of the detected PII
      * fields: a dictionary holding the info for the PII instance
      * pos: the character position of the PII inside the document chunk
    """

    __slots__ = "info", "fields", "pos"


    @classmethod
    def build(cls, ptype: TYPE_PTYPE, value: str, chunk: str, pos: int,
              lang: str = None, country: str = None, subtype: str = None,
              **kwargs):
        """
        Build an object with an full list of arguments
          :param ptype: PII type
          :param value: the extracted PII string
          :param chunk: the id for the chunk the PII is in
          :param pos: position of the PII in the chunk
          :param lang: language associated with the PII
          :param country: country associated with the PII
          :param subtype: PII subtype
        Additional optional arguments for the fields attribute are as given
        by FIELDS_OPTIONAL
        """
        # Define type
        if not isinstance(ptype, PiiEnum):
            try:
                ptype = PiiEnum[ptype]
            except KeyError as e:
                raise InvArgException("unknown PiiEnum value: {}", e)
        # Build object
        info = PiiEntityInfo(ptype, lang, country, subtype)
        return cls(info, value=value, chunk=chunk, pos=pos, **kwargs)


    def __init__(self, info: PiiEntityInfo, value: str, chunk: str, pos: int,
                 **kwargs):
        """
        Build an object
          :param info: a PiiEntityInfo object describing the entity fixed values
          :param value: the extracted PII string
          :param chunk: the id for the chunk the PII is in
          :param pos: position of the PII in the chunk
        Additional optional arguments are as given by FIELDS_OPTIONAL
        """
        # Compulsory arguments
        if not isinstance(info, PiiEntityInfo):
            raise InvArgException("invalid info object in entity constructor: {}", type(info))
        self.info = info
        self.fields = {'type': info.pii.name, 'value': value, 'chunkid': chunk}
        self.pos = pos
        # Other arguments
        for k in FIELDS_OPTIONAL:
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


    def add_process_stage(self, stage: str, **data):
        """
        Add a stage to the entity processing history
        """
        if "process" not in self.fields:
            self.fields["process"] = {"stage": stage, **data}
            return
        history = self.fields["process"].pop("history", [])
        history.append(self.fields["process"])
        self.fields["process"] = {"stage": stage, **data, "history": history}


    def asdict(self) -> Dict:
        """
        Return the object data as a dict that can then be serialised as JSON
        """
        return {**self.info.asdict(), **self.fields, "start": self.pos,
                "end": self.pos + len(self)}


    @classmethod
    def fromdict(cls, src: Dict) -> "PiiEntity":
        """
        Create an object from a dictionary
        """
        # Main elements
        try:
            ptype = src["type"]
            pos = src["start"]
            value = src["value"]
            chunkid = src["chunkid"]
        except KeyError as e:
            raise InvArgException("missing field in PiiEntity dict: {}", e)

        # Create
        fields = "lang", "country", "subtype", *FIELDS_OPTIONAL
        extra = dict(t for t in map(lambda k: (k, src.get(k)), fields) if t[1])
        return cls.build(ptype, value, chunkid, pos, **filter_dict(extra))
