"""
The Codex Library - Shared Universe Registry System

This module provides the registry system for tracking artifacts,
characters, and locations across stories in The Codex universe.
"""

from .registry import CodexRegistry
from .query import RegistryQuery

__all__ = ['CodexRegistry', 'RegistryQuery']
