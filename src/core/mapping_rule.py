"""
Mapping Rule Data Structures

Defines the rules for mapping Android APIs to HarmonyOS APIs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime


class MappingType(Enum):
    """Types of API mapping strategies."""
    DIRECT = "direct"           # 1:1 direct mapping
    SEMANTIC = "semantic"       # Semantically equivalent but different API
    DECOMPOSE = "decompose"     # 1:N - one Android API maps to multiple Harmony APIs
    COMPOSE = "compose"         # N:1 - multiple Android APIs map to one Harmony API
    BRIDGE = "bridge"           # Requires custom bridge code
    SHIM = "shim"              # Requires a shim/polyfill implementation
    UNSUPPORTED = "unsupported" # No equivalent in HarmonyOS


class MappingComplexity(Enum):
    """Complexity levels for mapping implementation."""
    LOW = "low"           # Simple signature change
    MEDIUM = "medium"     # Parameter transformation needed
    HIGH = "high"         # Significant logic translation
    VERY_HIGH = "very_high"  # Complex bridge code required


class MappingStatus(Enum):
    """Status of a mapping rule."""
    DRAFT = "draft"           # Initial creation
    ANALYZED = "analyzed"     # AI has analyzed
    GENERATED = "generated"   # Code has been generated
    TESTED = "tested"         # Tests passed
    REVIEWED = "reviewed"     # Human reviewed
    RELEASED = "released"     # In production


@dataclass
class ParameterMapping:
    """Mapping for a single parameter transformation."""
    android_param: str
    harmony_param: str
    transform: Optional[str] = None  # Transformation expression
    notes: Optional[str] = None


@dataclass
class MethodMapping:
    """Mapping for a single method."""
    android_method: str
    android_signature: str
    harmony_method: str
    harmony_signature: str
    mapping_type: MappingType = MappingType.DIRECT
    parameter_mappings: List[ParameterMapping] = field(default_factory=list)
    return_transform: Optional[str] = None
    exception_mappings: Dict[str, str] = field(default_factory=dict)
    pre_call_code: Optional[str] = None   # Code to execute before call
    post_call_code: Optional[str] = None  # Code to execute after call
    notes: Optional[str] = None


@dataclass
class MappingRule:
    """
    Complete mapping rule from Android API to HarmonyOS API.

    This is the core data structure that defines how an Android API
    should be translated to its HarmonyOS equivalent.
    """
    # Identifiers
    id: str
    android_class: str
    harmony_class: str

    # Mapping metadata
    mapping_type: MappingType
    complexity: MappingComplexity = MappingComplexity.MEDIUM
    confidence: float = 0.0  # 0.0 to 1.0
    status: MappingStatus = MappingStatus.DRAFT

    # Method mappings
    method_mappings: List[MethodMapping] = field(default_factory=list)

    # Additional requirements
    requires_imports: List[str] = field(default_factory=list)
    requires_permissions: List[str] = field(default_factory=list)
    requires_capabilities: List[str] = field(default_factory=list)

    # Bridge code (for complex mappings)
    bridge_code: Optional[str] = None
    helper_classes: List[str] = field(default_factory=list)

    # Quality metrics
    test_coverage: float = 0.0
    verified_apps: List[str] = field(default_factory=list)

    # Audit trail
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "ai"  # "ai" or "human"
    reviewed_by: Optional[str] = None
    notes: Optional[str] = None

    @property
    def is_simple(self) -> bool:
        """Check if this is a simple 1:1 mapping."""
        return (
            self.mapping_type == MappingType.DIRECT
            and self.complexity == MappingComplexity.LOW
        )

    @property
    def needs_bridge(self) -> bool:
        """Check if this mapping requires bridge code."""
        return self.mapping_type in (MappingType.BRIDGE, MappingType.SHIM)

    @property
    def is_ready_for_generation(self) -> bool:
        """Check if this mapping is ready for code generation."""
        return (
            self.confidence >= 0.7
            and self.status in (MappingStatus.ANALYZED, MappingStatus.REVIEWED)
        )

    def update_status(self, new_status: MappingStatus):
        """Update the mapping status."""
        self.status = new_status
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "android_class": self.android_class,
            "harmony_class": self.harmony_class,
            "mapping_type": self.mapping_type.value,
            "complexity": self.complexity.value,
            "confidence": self.confidence,
            "status": self.status.value,
            "method_mappings": [
                {
                    "android_method": m.android_method,
                    "android_signature": m.android_signature,
                    "harmony_method": m.harmony_method,
                    "harmony_signature": m.harmony_signature,
                    "mapping_type": m.mapping_type.value,
                }
                for m in self.method_mappings
            ],
            "requires_imports": self.requires_imports,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MappingRule":
        """Create a MappingRule from a dictionary."""
        method_mappings = [
            MethodMapping(
                android_method=m["android_method"],
                android_signature=m["android_signature"],
                harmony_method=m["harmony_method"],
                harmony_signature=m["harmony_signature"],
                mapping_type=MappingType(m.get("mapping_type", "direct")),
            )
            for m in data.get("method_mappings", [])
        ]

        return cls(
            id=data["id"],
            android_class=data["android_class"],
            harmony_class=data["harmony_class"],
            mapping_type=MappingType(data.get("mapping_type", "direct")),
            complexity=MappingComplexity(data.get("complexity", "medium")),
            confidence=data.get("confidence", 0.0),
            status=MappingStatus(data.get("status", "draft")),
            method_mappings=method_mappings,
            requires_imports=data.get("requires_imports", []),
            created_by=data.get("created_by", "ai"),
            notes=data.get("notes"),
        )


@dataclass
class MappingBatch:
    """A batch of mapping rules for bulk processing."""
    batch_id: str
    rules: List[MappingRule]
    android_package: str
    harmony_package: str
    total_methods: int = 0
    processed_methods: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def progress(self) -> float:
        if self.total_methods == 0:
            return 0.0
        return self.processed_methods / self.total_methods

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total
