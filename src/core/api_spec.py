"""
API Specification Data Structures

Defines the core data structures for representing Android and HarmonyOS APIs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class Platform(Enum):
    """Supported platforms."""
    ANDROID = "android"
    HARMONY = "harmony"


class Visibility(Enum):
    """API visibility levels."""
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    PACKAGE = "package"


@dataclass
class ParameterSpec:
    """Specification for a method parameter."""
    name: str
    type: str
    nullable: bool = False
    default_value: Optional[str] = None
    description: Optional[str] = None
    annotations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "nullable": self.nullable,
            "default_value": self.default_value,
            "description": self.description,
            "annotations": self.annotations,
        }


@dataclass
class MethodSpec:
    """Specification for an API method."""
    name: str
    signature: str
    return_type: str
    parameters: List[ParameterSpec] = field(default_factory=list)
    throws: List[str] = field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    is_static: bool = False
    is_final: bool = False
    is_abstract: bool = False
    is_deprecated: bool = False
    since_version: Optional[str] = None
    deprecated_since: Optional[str] = None
    description: Optional[str] = None
    semantic_tags: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "signature": self.signature,
            "return_type": self.return_type,
            "parameters": [p.to_dict() for p in self.parameters],
            "throws": self.throws,
            "visibility": self.visibility.value,
            "is_static": self.is_static,
            "is_final": self.is_final,
            "is_abstract": self.is_abstract,
            "is_deprecated": self.is_deprecated,
            "since_version": self.since_version,
            "deprecated_since": self.deprecated_since,
            "description": self.description,
            "semantic_tags": self.semantic_tags,
            "annotations": self.annotations,
        }


@dataclass
class FieldSpec:
    """Specification for a class field."""
    name: str
    type: str
    visibility: Visibility = Visibility.PUBLIC
    is_static: bool = False
    is_final: bool = False
    default_value: Optional[str] = None
    description: Optional[str] = None


@dataclass
class APISpec:
    """
    Complete specification for an API class/interface.

    This is the core data structure that represents both Android and HarmonyOS APIs.
    """
    platform: Platform
    package: str
    class_name: str
    full_qualified_name: str

    # Class metadata
    is_interface: bool = False
    is_abstract: bool = False
    is_final: bool = False
    is_deprecated: bool = False

    # Inheritance
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)

    # Members
    methods: List[MethodSpec] = field(default_factory=list)
    fields: List[FieldSpec] = field(default_factory=list)
    inner_classes: List[str] = field(default_factory=list)

    # Documentation
    description: Optional[str] = None
    since_version: Optional[str] = None
    deprecated_since: Optional[str] = None

    # Semantic information
    semantic_tags: List[str] = field(default_factory=list)
    usage_patterns: List[str] = field(default_factory=list)

    # Metadata
    source_file: Optional[str] = None
    parsed_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.full_qualified_name:
            self.full_qualified_name = f"{self.package}.{self.class_name}"

    @property
    def method_count(self) -> int:
        return len(self.methods)

    @property
    def public_methods(self) -> List[MethodSpec]:
        return [m for m in self.methods if m.visibility == Visibility.PUBLIC]

    def get_method(self, name: str) -> Optional[MethodSpec]:
        """Get a method by name."""
        for method in self.methods:
            if method.name == name:
                return method
        return None

    def get_methods_by_tag(self, tag: str) -> List[MethodSpec]:
        """Get all methods with a specific semantic tag."""
        return [m for m in self.methods if tag in m.semantic_tags]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "package": self.package,
            "class_name": self.class_name,
            "full_qualified_name": self.full_qualified_name,
            "is_interface": self.is_interface,
            "is_abstract": self.is_abstract,
            "is_final": self.is_final,
            "is_deprecated": self.is_deprecated,
            "extends": self.extends,
            "implements": self.implements,
            "methods": [m.to_dict() for m in self.methods],
            "description": self.description,
            "since_version": self.since_version,
            "semantic_tags": self.semantic_tags,
            "parsed_at": self.parsed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APISpec":
        """Create an APISpec from a dictionary."""
        methods = [
            MethodSpec(
                name=m["name"],
                signature=m["signature"],
                return_type=m["return_type"],
                parameters=[
                    ParameterSpec(**p) for p in m.get("parameters", [])
                ],
                throws=m.get("throws", []),
                visibility=Visibility(m.get("visibility", "public")),
                is_static=m.get("is_static", False),
                is_deprecated=m.get("is_deprecated", False),
                description=m.get("description"),
                semantic_tags=m.get("semantic_tags", []),
            )
            for m in data.get("methods", [])
        ]

        return cls(
            platform=Platform(data["platform"]),
            package=data["package"],
            class_name=data["class_name"],
            full_qualified_name=data.get(
                "full_qualified_name",
                f"{data['package']}.{data['class_name']}"
            ),
            is_interface=data.get("is_interface", False),
            is_abstract=data.get("is_abstract", False),
            is_deprecated=data.get("is_deprecated", False),
            extends=data.get("extends"),
            implements=data.get("implements", []),
            methods=methods,
            description=data.get("description"),
            since_version=data.get("since_version"),
            semantic_tags=data.get("semantic_tags", []),
        )
