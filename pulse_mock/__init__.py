"""
Pulse Mock API Client

A Python package for creating mock API clients using VCR cassettes.
Easily simulate API responses for testing and development.
"""

from .client import MockAPIClient, NFLMockClient
from .exceptions import CassetteNotFoundError, RequestNotFoundError, InvalidCassetteError
from .server import create_app

__version__ = "1.0.0"
__all__ = [
    "MockAPIClient", 
    "NFLMockClient", 
    "CassetteNotFoundError", 
    "RequestNotFoundError", 
    "InvalidCassetteError",
    "create_app"
]
