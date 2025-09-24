"""
Custom exceptions for the Pulse Mock API Client.
"""


class MockAPIError(Exception):
    """Base exception for all Mock API errors."""
    pass


class CassetteNotFoundError(MockAPIError):
    """Raised when a VCR cassette file cannot be found."""
    pass


class RequestNotFoundError(MockAPIError):
    """Raised when a request cannot be matched to any recorded interaction."""
    pass


class InvalidCassetteError(MockAPIError):
    """Raised when a VCR cassette file is invalid or malformed."""
    pass
