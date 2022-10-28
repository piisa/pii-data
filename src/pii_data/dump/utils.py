
from typing import Iterator, Dict


# A class used only for node identification when converting to YAML
class TextNode(str):
    pass


class ChunkIterWrapper:
    """
    A small wrapper around a chunk iterator, to be able to map it to a custom
    YAML representer or JSON dumper
    """
    __slots__ = ["chk"]

    def __init__(self, chunks: Iterator[Dict]):
        self.chk = chunks

    def __iter__(self) -> Iterator[Dict]:
        return iter(self.chk)

    def __repr__(self):
        return "<ChunkWrapper>"
