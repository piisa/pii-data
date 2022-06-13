"""
Read raw documents
"""

from typing import Dict, TextIO

from .utils import TextNode
from ..helper.io import openfile


class RawReader:
    """
    Convert a plain text to a YAML PII Source Document, line by line.
    Can infer hiearchy from leading indent.
    """

    def __init__(self, indent: int):
        self.ind = indent


    def read_file(self, src: TextIO) -> Dict:
        """
        Read chunks from the file and push them to the data stack
        """
        chunkid = 0
        currlev = 0
        doc = {'chunks': []}
        stack = [doc]

        for line in src:
            # Read a line, compute hierarchy level from indent
            raw = line.strip()
            lev = (len(line) - len(raw))//self.ind if self.ind else 0

            # Create the chunk
            chunkid += 1
            chunk = dict(id=chunkid, text=TextNode(raw))

            # Find the place where to add the chunk
            if lev < currlev:
                stack = stack[:-1]
            elif lev > currlev:
                top = stack[-1]['chunks'][-1]
                top['chunks'] = []
                stack.append(top)

            # Add it
            stack[-1]['chunks'].append(chunk)
            currlev = lev

        return doc


    def read(self, inputfile: str) -> Dict:
        '''
        Open a raw text file and read it as a PII Source Document
        '''
        with openfile(inputfile) as f:
            return self.read_file(f)


def load_raw(inputfile: str, indent: int) -> Dict:
    """
    Read a raw text file and convert it to PII Source Document
    """
    reader = RawReader(indent)
    return reader.read(inputfile)
