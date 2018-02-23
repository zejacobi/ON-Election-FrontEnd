"""
File containing any custom exceptions used in this program
"""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class NotFoundError(Error):
    """
    Exception raised when an excepted file or database entry cannot be found. We give this the
    integer representation 404, for easy use with the API.

    :ivar str message: Gives context as to what exactly is missing.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __int__(self):
        return 404


class MalformedError(Error):
    """
    Exception raised when something doesn't conform to internal specifications. We give this the
    integer representation of 400, for easy use with the API.

    :ivar str message: Gives context as to what exactly is messed up.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __int__(self):
        return 400
