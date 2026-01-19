"""
CRAFT Core Module
Core data structures and utilities for API adaptation layer generation.
"""

from .api_spec import APISpec, MethodSpec, ParameterSpec
from .mapping_rule import MappingRule, MappingType
from .config import Config

__all__ = [
    "APISpec",
    "MethodSpec",
    "ParameterSpec",
    "MappingRule",
    "MappingType",
    "Config",
]
