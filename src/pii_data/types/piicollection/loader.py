"""
A class to load PII collection from files
"""

import json

from typing import Dict, TextIO

from ...defs import FMT_PIICOLLECTION
from ...helper.io import base_extension, openfile
from ...helper.exception import InvArgException, ProcException, FileException
from ..piientity import PiiEntity
from .collection import PiiDetector, PiiCollection

# --------------------------------------------------------------------------

def check_format(metadata: Dict, source_name: str):
    """
    Check that the PiiCollection header contains valid tags
    """
    fmt = metadata.get("format")
    if fmt != FMT_PIICOLLECTION:
        raise InvArgException('invalid format "{}" found in {}',
                              fmt, source_name)


class PiiCollectionLoader(PiiCollection):
    """
    A subclass of PiiCollection that can load data from external sources
    """

    def _load_detectors(self, detectors: Dict) -> Dict:
        try:
            self.detectors = {int(k): PiiDetector(**v)
                              for k, v in detectors.items()}
        except Exception as e:
            raise ProcException("error reading detector info from header: {}", e)
        self.detector_map = {v._id: k for k, v in self.detectors.items()}


    def load_json(self, filename: str):
        """
        Load a PiiCollection from a JSON file
        """
        try:
            with openfile(filename, encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise FileException("cannot load collection '{}': {}", filename,
                                e) from e

        meta = data['metadata']
        check_format(meta, filename)
        self._set_header(meta)
        self._load_detectors(meta['detectors'])
        self.pii = [PiiEntity.fromdict(d) for d in data['pii_list']]


    def load_ndjson(self, src: TextIO):
        """
        Load a PiiCollection from a file-like source contianing NDJSON data
        """
        # Read first line (collection header)
        header = json.loads(next(src))
        check_format(header, 'ndjson source')
        self._set_header(header)
        self._load_detectors(header['detectors'])

        # Read all PII instances
        self.pii = [PiiEntity.fromdict(json.loads(line)) for line in src]


    def load(self, filename: str):
        """
        Load either an NDJSON or JSON file containing serialized PII entities
        """
        base_ext = base_extension(filename)
        if base_ext == ".json":
            self.load_json(filename)
        elif base_ext in (".ndjson", ".jsonl"):
            with openfile(filename, encoding="utf-8") as f:
                self.load_ndjson(f)
        else:
            raise FileException("unsupported format for PiiCollection: {}",
                                base_ext)
