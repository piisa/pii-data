"""
Iterate over a PiiCollection by document chunks
"""


from operator import attrgetter

from typing import List, Iterable

from ...helper.peeker import IterationPeeker
from ..piientity import PiiEntity
from .collection import PiiCollection


class PiiChunkIterator:
    """
    Iterate over a PII collection by groups corresponding to all PiiEntity
    instances for the same document chunk
    """

    def __init__(self, piic: PiiCollection):
        self._piic = IterationPeeker(piic)
        self.size = len(piic)

    def __repr__(self) -> str:
        return f"<PiiChunkIterator #{self.size}>"


    def __iter__(self) -> Iterable[List[PiiEntity]]:
        return self.chunks()


    def _chunk_pii(self, chunkid: str) -> Iterable[PiiEntity]:
        """
        Return an iterable over all PiiEntity instances in the collection that
        correspond to the passed chunk id
        """
        chunkid = str(chunkid)
        while True:
            next_pii = self._piic.peek()
            if not next_pii or str(next_pii.fields["chunkid"]) != chunkid:
                return
            yield next(self._piic)


    def chunks(self) -> Iterable[List[PiiEntity]]:
        """
        Group the PiiEntity objects in the source by document chunk.
        Return an iterable of piientity lists, each list corresponding to a
        different document chunk
        """
        while True:
            next_pii = self._piic.peek()
            if not next_pii:
                return
            chunkid = next_pii.fields["chunkid"]
            yield self(chunkid)


    def __call__(self, chunkid: str) -> List[PiiEntity]:
        """
        Return the list of all PiiEntity instances in the collection that
        correspond to the passed chunk id, sorted by their position in
        the chunk.
        Note: it should be called with the chunk ids in document order.
        """
        return sorted(self._chunk_pii(chunkid), key=attrgetter("pos"))
