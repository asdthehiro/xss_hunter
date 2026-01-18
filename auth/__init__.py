"""
Auth package initialization
"""
from .login import Authenticator, AuthenticationError

__all__ = ['Authenticator', 'AuthenticationError']
