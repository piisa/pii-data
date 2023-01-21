"""
An utility to wrap an iterator and peek at the next value
"""


from typing import Iterable, Any


class IterationPeeker:
    """
    Wrap an iterable so that we can peek at the next value without retrieving it
    """

    def __init__(self, src: Iterable[Any]):
        self.it = iter(src)
        self._get_next()

    def __iter__(self):
        return self

    def _get_next(self):
        """
        Fetch and store the next value
        """
        try:
            self._next = next(self.it)
        except StopIteration:
            self._next = None

    def __next__(self):
        """
        Advance and return the next value
        """
        if self._next is None:
            raise StopIteration()
        try:
            return self._next
        finally:
            self._get_next()

    def peek(self):
        """
        Return the next value without advancing the iterator.
        If the iteratur would get exhausted, return `None`
        """
        return self._next
