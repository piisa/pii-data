"""
An exception hierarchy for PIISA applications

  PiiDataException
    |
    |-> InvArgException
    |-> BuildException
    |     |-> ConfigException
    |     |-> MissingDependency
    |     |-> UnimplementedException
    |
    |-> ProcException
    |     |
    |     |-> InvalidDocument
    |     |-> FileException
    |

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


class BuildException(PiiDataException):
    """
    A problem while building objects
    """
    pass


class ConfigException(BuildException):
    """
    A problem with a configuration
    """
    pass


class MissingDependency(BuildException):
    """
    A package dependency that is not satisfied
    """
    pass


class UnimplementedException(BuildException):
    """
    Unimplemented methods/functions
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
    A problem with a file
    """
    pass
