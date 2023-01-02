"""
A class to describe a list of detected PII entities
"""

from datetime import datetime, timezone
import json

from typing import TextIO, Dict, Iterator

from ...defs import FMT_PIICOLLECTION
from ...helper.json_encoder import CustomJSONEncoder
from ...helper.exception import InvArgException
from ..piientity import PiiEntity


class PiiDetector:
    """
    Description of a PII Detection module
    """

    __slots__ = "_id", "fields"


    def __init__(self, source: str, name: str, version: str,
                 url: str = None, method: str = None):
        """
          :param name: name of the detector
          :param version: detector version
          :param source: vendor/provider for the detector
          :param url: an optional URL for the detector code
          :param method: an optional string defining the detector method
        """
        self._id = f"{source}/{name}/{version}"
        # Compulsory fields
        self.fields = {"source": source, "name": name, "version": version}
        # Optional fields
        if url:
            self.fields["url"] = url
        if method:
            self.fields["method"] = method

    def __repr__(self) -> str:
        return f"<PiiDetector {self._id}>"

    def asdict(self) -> Dict:
        """
        Return the object data as a plain dictionary
        """
        return self.fields



class PiiCollection:
    """
    A object holding a list of PiiEntity items, plus the PiiDetector objects
    associated with them.

    Iterating it returns the instances of PiiEntity object contained in it.
    """

    def __init__(self, lang: str = None, docid: str = None):
        """
         :param lang: default language (ISO 639-1 code) for all entities
           in the collection
         :param docid: default document that entities in the collection will
           refer to
        """
        # Default values
        self.defaults = {}
        if lang:
            self.defaults['lang'] = lang
        if docid:
            self.defaults['docid'] = docid

        # An encoder for generating NDJSON output
        self.encoder = CustomJSONEncoder(ensure_ascii=False)

        # Data contained in the object
        self.detectors = {}
        self.detector_map = {}
        self.pii = []

        # Initialize the collection header
        self._set_header({
            "date": datetime.utcnow().replace(tzinfo=timezone.utc),
            "format": FMT_PIICOLLECTION,
            "lang": self.defaults.get("lang")
        })


    def _set_header(self, header: Dict):
        self._header = header.copy()


    def header(self) -> Dict:
        """
        Return the collection header
        """
        self._header["detectors"] = {k: v.asdict()
                                     for k, v in self.detectors.items()}
        return self._header


    def stage(self, value: str = None) -> str:
        """
        Return the processing stage for the collection status, and optionally
        set it
        """
        if value:
            self._header["stage"] = value
        return self._header.get("stage")


    def __len__(self) -> int:
        """
        Return the number of PII instances in the object
        """
        return len(self.pii)


    def __iter__(self) -> Iterator[PiiEntity]:
        """
        Return an iterator over the PII instances in the object
        """
        return iter(self.pii)


    def add_detector(self, detector: PiiDetector) -> str:
        """
        Add a new detector to the header. Returns the detector index
        """
        if detector._id not in self.detector_map:
            num = len(self.detectors) + 1
            self.detectors[num] = detector
            self.detector_map[detector._id] = num
        self.stage('detection')
        return self.detector_map[detector._id]


    def add(self, entity: PiiEntity, detector: PiiDetector = None):
        """
        Add a PII entity to the collection
         :param entity: the entity to add
         :param detector: the PII Detector used to create this entity
        """
        # Add detector
        if detector:
            entity.fields['detector'] = self.add_detector(detector)

        # Add default values
        for k, v in self.defaults.items():
            if k not in entity.fields:
                entity.fields[k] = v

        # Add entity to the list
        self.pii.append(entity)


    def set_decision(self, info: Dict):
        """
        Set the decision information for the collection, and change the stage
          :param info: decision information to add to the collection header
        """
        self._header["decision"] = info
        self.stage("decision")


    def dump(self, out: TextIO, format: str = 'ndjson', **kwargs):
        """
        Dump the collection to an output destination
          :param out: destination to write to
          :param format: output format, either `ndjson` or `json`
        For `json` format, all passed additional arguments will be added to
        the JSON serializer
        """
        header = self.header()

        if format in ("ndjson", "jsonl"):

            print(self.encoder.encode(header), file=out)
            for pii in self.pii:
                print(self.encoder.encode(pii), file=out)

        elif format == "json":

            data = {"metadata": header, "pii_list": self.pii}
            if "indent" not in kwargs:
                kwargs["indent"] = 2
            json.dump(data, out, cls=CustomJSONEncoder, ensure_ascii=False,
                      **kwargs)

        else:
            raise InvArgException("unknown output format: {}", format)
