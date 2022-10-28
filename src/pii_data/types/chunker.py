"""
Convert document pieces in DocumentChunk objects, optionally adding context
"""

from types import MappingProxyType

from typing import Dict


class DocumentChunk:
    """
    A class to hold the contents of a document chunk:
     - a chunk id
     - the chunk data (its contents)
     - a context for the chunk (optional)
    """

    __slots__ = ('id', 'data', 'context')

    def __init__(self, id, data, context: dict = None):
        self.id = str(id)
        self.data = data
        self.context = context

    def __repr__(self) -> str:
        return f"<DocumentChunk {self.id} #{len(self.data)}>"

    def __eq__(self, other) -> bool:
        return (self.id, self.data, self.context) == \
            (other.id, other.data, other.context)

    def as_dict(self, context: bool = True) -> Dict:
        doc = {"id": self.id, "data": self.data}
        if context and self.context:
            doc["context"] = self.context
        return doc



class ChunkGenerator:
    """
    Create DocumentChunk objects from document pieces
    """

    def __init__(self, **kwargs):
        self._chunk_id = 0


    def __call__(self, elem: Dict, ctx: Dict = None) -> DocumentChunk:
        """
        Create one chunk from a document element
        """
        # Get or create chunk id
        chunk_id = elem.get("id")
        if chunk_id is None:
            self._chunk_id += 1
            chunk_id = self._chunk_id

        # Create & return the chunk
        context = ctx or elem.get("context")
        return DocumentChunk(chunk_id, elem["data"], context)



class ContextChunkGenerator(ChunkGenerator):
    """
    Create DocumentChunk objects from document pieces, adding context values
    (including before & after fields)
    """

    def __init__(self, meta: Dict = None):
        super().__init__()
        if meta is None:
            meta = {}
        self._ctx = {k: MappingProxyType(v) for k, v in meta.items()}
        self.before = None
        self.current = None


    def __call__(self, elem: Dict) -> DocumentChunk:
        """
        Receive a dict with the current element and create a DocumentChunk from
        it, adding the relevant context
        """

        # A possible pending final chunk
        if elem is None:
            if not self.before:         # document has no chunks
                return
            elif not self.current:      # document has only one chunk
                return self.before
            else:                       # document has at least two chunks
                self.current.context["before"] = self.before.data
                return self.current

        # Create the chunk
        context = self._ctx.copy()
        if "context" in elem:
            context.update(elem["context"])
        chunk = super().__call__(elem, context)

        # If 1st chunk, just store it & return nothing
        if self.before is None:
            self.before = chunk
            return

        # Select chunk, and add before/after context
        if self.current is None:    # 2nd chunk: return 1st chunk
            ret = self.before
        else:                       # 3rd and later chunks
            ret = self.current
            ret.context["before"] = self.before.data
            self.before = self.current

        ret.context["after"] = chunk.data
        self.current = chunk
        return ret
