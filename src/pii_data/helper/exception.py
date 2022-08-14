"""
A simple exception hiearchy
"""


class PiiDataException(Exception):
    """
    Base exception
     :param msg: an output exception message string, for which the format method
       is called
    """
    def __init__(self, msg: str, *args):
        super().__init__(msg.format(*args) if args else msg)


class InvArgException(PiiDataException):
    """
    An invalid argument
    """
    pass


class ProcException(PiiDataException):
    """
    A processing exception
    """
    pass


class InvalidDocument(ProcException):
    """
    An document invalid for some reason
    """
    pass


class FileException(ProcException):
    """
    An problem with a file
    """
    pass


class UnimplementedException(PiiDataException):
    """
    Unimplemented methods/functions
    """
    pass
