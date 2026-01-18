"""
Scanner package initialization
"""
from .payloads import XSSPayloads, PayloadGenerator
from .detector import XSSDetector, XSSContext

__all__ = [
    'XSSPayloads',
    'PayloadGenerator',
    'XSSDetector',
    'XSSContext'
]
