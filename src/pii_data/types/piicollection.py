"""
A class to describe a list of detected PII entities
"""

from datetime import datetime, timezone
import json

from typing import TextIO, Dict

from .. import FORMAT_VERSION
from ..helper.json_encoder import CustomJSONEncoder
from ..helper.exception import InvArgException
from .piientity import PiiEntity
from .defs import PIIC_FORMAT


class PiiDetector:
    """
    Description of a PII Detection module
    """

    __slots__ = "_id", "fields"


    def __init__(self, name: str, version: str, source: str,
                 url: str = None, method: str = None):
        """
          :param name: name of the detector
          :param version: detector version
          :param source: vendor/provider for the detector
          :param url: an optional URL for the detector code
          :param method: an optional string defining the detector method
        """
        self._id = f'{source}/{name}/{version}'
        # Compulsory fields
        self.fields = {'name': name, 'version': version, 'source': source}
        # Optional fields
        if url:
            self.fields['url'] = url
        if method:
            self.fields['method'] = method

    def __repr__(self) -> str:
        return f"<PiiDetector {self._id}>"

    def as_dict(self) -> Dict:
        """
        Return the object data as a plain dictionary
        """
        return self.fields



class PiiCollection:
    """
    A object holding a list of PiiEntity items, plus the PiiDetector objects
    associated with them
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

        # Encoder for generating NDJSON output
        self.encoder = CustomJSONEncoder(ensure_ascii=False)

        # Contained data
        self.detectors = {}
        self.detector_map = {}
        self.pii = []


    def __len__(self) -> int:
        """
        Return the number of PII instances in the object
        """
        return len(self.pii)

    def add_detector(self, detector: PiiDetector) -> str:
        """
        Add a new detector to the header. returns the detector index
        """
        if detector._id not in self.detector_map:
            num = len(self.detectors) + 1
            self.detectors[num] = detector
            self.detector_map[detector._id] = num
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


    def dump(self, out: TextIO, format: str = 'ndjson', **kwargs):
        """
        Dump the collection to an output destination
          :param out: destination to write to
          :param format: output format, either `ndjson` or `json`
        For `json` format, all passed additional arguments will be added to
        the JSON serializer
        """
        header = {
            'date': datetime.utcnow().replace(tzinfo=timezone.utc),
            'format': PIIC_FORMAT,
            'format_version': FORMAT_VERSION,
            'detectors': {k: v.as_dict() for k, v in self.detectors.items()}
        }

        if format == 'ndjson':

            print(self.encoder.encode(header), file=out)
            for pii in self.pii:
                print(self.encoder.encode(pii), file=out)

        elif format == 'json':

            data = {'metadata': header, 'pii_list': self.pii}
            if 'indent' not in kwargs:
                kwargs['indent'] = 2
            json.dump(data, out, ensure_ascii=False, cls=CustomJSONEncoder,
                      **kwargs)

        else:
            raise InvArgException("unknown output format: {}", format)


# --------------------------------------------------------------------------

def check_format(metadata: Dict, source_name: str):
    """
    Check that the PiiCollection header contains valid tags
    """
    fmt = metadata.get('format')
    if fmt != PIIC_FORMAT:
        raise InvArgException('invalid format "{}" found in {}',
                              fmt, source_name)
    ver = metadata.get('format_version')
    if ver != FORMAT_VERSION:
        raise InvArgException('invalid format version "{}" found in {}',
                              fmt, source_name)


class PiiCollectionLoader(PiiCollection):
    """
    A subclass of PiiCollection that can load data from external sources
    """

    def _load_detectors(self, detectors: Dict) -> Dict:
        self.detectors = {k: PiiDetector(**v) for k, v in detectors.items()}
        self.detector_map = {v._id: k for k, v in self.detectors.items()}


    def load_json(self, filename: str):
        """
        Load a PiiCollection from a JSON file
        """
        with open(filename, encoding='utf-8') as f:
            data = json.load(f)
        meta = data['metadata']
        check_format(meta, filename)
        self._load_detectors(meta['detectors'])
        self.pii = data['pii_list']


    def load_ndjson(self, src: TextIO):
        """
        Load a PiiCollection from a file-like source contianing NDJSON data
        """
        header = json.loads(next(src))
        check_format(header, 'ndjson source')
        self._load_detectors(header['detectors'])
        self.pii = [json.loads(line) for line in src]
