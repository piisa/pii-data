"""
The object holding document data.
A base object is provided, and them a subclass to hold data for a local
document.
Streaming document subclasses would need to implement at least the get_chunks()
method, producing an iterable of chunks.
"""


from collections import namedtuple
import uuid

from typing import Dict, Iterable

from ..doc import dump_raw, dump_yaml
from ..helper.exception import InvArgException, FileException, UnimplementedException
from ..helper.io import load_datafile


# The contents of a document chunk:
#  - a chunk id
#  - the text content
#  - a context for the chunk (TBD)
DocumentChunk = namedtuple('DocumentChunk', 'id text context', defaults=[None])



class BaseSourceDocument:
    """
    An abstract base object to hold the data for a document to be processed.
    Child classes need to provide at least a get_chunks method
    """

    def __init__(self, id: str = None):
        self.id = id if id is not None else str(uuid.uuid4())


    def __repr__(self) -> str:
        return f'<SourceDocument {self.id}>'


    def set_id(self, id: str):
        self.id = id


    def __iter__(self):
        return self.get_chunks()


    def get_chunks(self) -> Iterable[DocumentChunk]:
        raise UnimplementedException('abstract class')


# --------------------------------------------------------------------------


class SourceDocument(BaseSourceDocument):
    """
    A document fully loaded in memory
    """

    def __init__(self, id: str = None, chunks: Iterable[Dict] = None):
        super().__init__(id)
        self.set_chunks(chunks)


    def set_chunks(self, chunks: Iterable[Dict]):
        self.chunks = list(chunks) if chunks else None


    def _data_iter(self, elem: Dict) -> Iterable[DocumentChunk]:
        text = elem.get('text')
        if text:
            yield DocumentChunk(elem['id'], text)
        for chunk in elem.get('chunks', []):
            yield from self._data_iter(chunk)


    def get_chunks(self) -> Iterable[DocumentChunk]:
        """
        Get an iterable over document chunks
        """
        for chunk in self.chunks:
            yield from self._data_iter(chunk)


    def load(self, filename: str):
        """
        Load a document from a file, in yaml format
        """
        data = load_datafile(filename)
        try:
            self.chunks = data['chunks']
        except KeyError:
            raise FileException('no chunks found in: "{}"', filename)
        if 'id' in data:
            self.id = data['id']


    def dump(self, outname: str, format: str = None, indent: int = 0):
        """
        Dump the document to an output file
        """
        if format is not None:
            format = str(format).lower()
        elif outname.endswith(('.yml', '.yaml')):
            format = 'yml'
        elif outname.endswith('.txt'):
            format = 'txt'
        else:
            raise InvArgException('unspecified format for: {}', outname)

        data = {'docid': self.id,
                'chunks': self.chunks}

        if format in ('yaml', 'yml'):
            dump_yaml(data, outname, indent)
        else:
            dump_raw(data, outname, indent)
