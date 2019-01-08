"""
pcups.exceptions
~~~~~~~~~~~~~~~~~~~
This module contains the set of PCUPS' exceptions.
"""
from cups import IPPError

__all__ = [
        'JobDocumentNotAvailableError',
        'JobNotFoundError',
        'JobCompletedError',
        'PrinterNotFoundError',
]


class PrintBaseException(IPPError):
    pass


class JobCompletedError(PrintBaseException):
    """Job has been completed, you cannot cancel it."""


class JobNotFoundError(PrintBaseException):
    """CUPS' job does not exist."""


class JobDocumentNotAvailableError(PrintBaseException):
    """Job's document does not exist, you cannot restart it."""


class PrinterNotFoundError(PrintBaseException):
    """Printer not found error."""
