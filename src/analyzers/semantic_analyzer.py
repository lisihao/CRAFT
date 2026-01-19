"""
Semantic Analyzer

Uses AI to analyze API semantics and find mappings between Android and HarmonyOS APIs.
"""

from typing import List, Optional, Dict, Tuple
import logging
from dataclasses import dataclass

from ..core.api_spec import APISpec, MethodSpec
from ..core.mapping_rule import MappingRule, MappingType, MappingComplexity, MethodMapping
from ..core.config import get_config


logger = logging.getLogger(__name__)


@dataclass
class SemanticMatch:
    """Represents a semantic match between two APIs."""
    android_api: APISpec
    harmony_api: APISpec
    confidence: float
    mapping_type: MappingType
    reasoning: str


class SemanticAnalyzer:
    """
    AI-powered semantic analyzer for API mapping.

    Uses Claude to understand API semantics and find equivalent APIs
    between Android and HarmonyOS.
    """

    # Known semantic equivalences (seed knowledge)
    KNOWN_MAPPINGS = {
        # Activity/UIAbility
        "android.app.Activity": "ohos.app.UIAbility",
        "android.content.Intent": "ohos.app.Want",
        "android.content.Context": "ohos.app.Context",
        "android.os.Bundle": "ohos.app.AbilityConstant.LaunchParam",

        # Views/Components
        "android.view.View": "ohos.arkui.Component",
        "android.widget.TextView": "ohos.arkui.Text",
        "android.widget.Button": "ohos.arkui.Button",
        "android.widget.ImageView": "ohos.arkui.Image",
        "android.widget.EditText": "ohos.arkui.TextInput",

        # Storage
        "android.content.SharedPreferences": "ohos.data.preferences.Preferences",
        "android.database.sqlite.SQLiteDatabase": "ohos.data.relationalStore.RdbStore",

        # Network
        "android.net.ConnectivityManager": "ohos.net.connection",
        "android.net.wifi.WifiManager": "ohos.wifi",

        # System
        "android.os.Handler": "ohos.taskpool",
        "android.os.AsyncTask": "ohos.taskpool.Task",
    }

    def __init__(self, ai_client=None):
        """
        Initialize the semantic analyzer.

        Args:
            ai_client: Optional AI client for semantic analysis.
        """
        self.config = get_config()
        self.ai_client = ai_client

    def find_mapping(
        self,
        android_api: APISpec,
        harmony_apis: List[APISpec]
    ) -> Optional[MappingRule]:
        """
        Find the best HarmonyOS mapping for an Android API.

        Args:
            android_api: The Android API to map.
            harmony_apis: Available HarmonyOS APIs.

        Returns:
            MappingRule if a mapping is found, None otherwise.
        """
        # Step 1: Check known mappings
        known_target = self.KNOWN_MAPPINGS.get(android_api.full_qualified_name)
        if known_target:
            harmony_api = self._find_by_name(harmony_apis, known_target)
            if harmony_api:
                return self._create_mapping_rule(
                    android_api,
                    harmony_api,
                    confidence=0.95,
                    mapping_type=MappingType.DIRECT,
                )

        # Step 2: Try name-based matching
        name_matches = self._find_by_name_similarity(android_api, harmony_apis)
        if name_matches:
            best_match = name_matches[0]
            return self._create_mapping_rule(
                android_api,
                best_match[0],
                confidence=best_match[1],
                mapping_type=MappingType.SEMANTIC,
            )

        # Step 3: Use AI for semantic analysis
        if self.ai_client:
            return self._ai_semantic_match(android_api, harmony_apis)

        return None

    def analyze_method_mapping(
        self,
        android_method: MethodSpec,
        harmony_api: APISpec
    ) -> Optional[MethodMapping]:
        """
        Find the best method mapping for an Android method.

        Args:
            android_method: The Android method to map.
            harmony_api: The target HarmonyOS API class.

        Returns:
            MethodMapping if found, None otherwise.
        """
        # Try exact name match first
        harmony_method = harmony_api.get_method(android_method.name)
        if harmony_method:
            return MethodMapping(
                android_method=android_method.name,
                android_signature=android_method.signature,
                harmony_method=harmony_method.name,
                harmony_signature=harmony_method.signature,
                mapping_type=MappingType.DIRECT,
            )

        # Try semantic matching
        for harmony_method in harmony_api.public_methods:
            if self._methods_semantically_similar(android_method, harmony_method):
                return MethodMapping(
                    android_method=android_method.name,
                    android_signature=android_method.signature,
                    harmony_method=harmony_method.name,
                    harmony_signature=harmony_method.signature,
                    mapping_type=MappingType.SEMANTIC,
                )

        return None

    def _find_by_name(self, apis: List[APISpec], full_name: str) -> Optional[APISpec]:
        """Find an API by its full qualified name."""
        for api in apis:
            if api.full_qualified_name == full_name:
                return api
        return None

    def _find_by_name_similarity(
        self,
        android_api: APISpec,
        harmony_apis: List[APISpec]
    ) -> List[Tuple[APISpec, float]]:
        """
        Find HarmonyOS APIs with similar names.

        Returns list of (APISpec, confidence) tuples sorted by confidence.
        """
        matches = []

        android_name = android_api.class_name.lower()

        for harmony_api in harmony_apis:
            harmony_name = harmony_api.class_name.lower()

            # Exact class name match
            if android_name == harmony_name:
                matches.append((harmony_api, 0.8))
                continue

            # Partial match
            if android_name in harmony_name or harmony_name in android_name:
                matches.append((harmony_api, 0.5))
                continue

            # Semantic tags match
            common_tags = set(android_api.semantic_tags) & set(harmony_api.semantic_tags)
            if len(common_tags) >= 2:
                confidence = min(0.7, 0.3 + 0.1 * len(common_tags))
                matches.append((harmony_api, confidence))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    def _methods_semantically_similar(
        self,
        android_method: MethodSpec,
        harmony_method: MethodSpec
    ) -> bool:
        """Check if two methods are semantically similar."""
        # Same name
        if android_method.name.lower() == harmony_method.name.lower():
            return True

        # Common prefixes (get/set/is/has/on)
        prefixes = ["get", "set", "is", "has", "on", "add", "remove", "start", "stop"]
        for prefix in prefixes:
            if (android_method.name.startswith(prefix) and
                    harmony_method.name.startswith(prefix)):
                # Check if the rest matches
                android_rest = android_method.name[len(prefix):].lower()
                harmony_rest = harmony_method.name[len(prefix):].lower()
                if android_rest == harmony_rest:
                    return True

        # Same semantic tags
        common_tags = set(android_method.semantic_tags) & set(harmony_method.semantic_tags)
        if len(common_tags) >= 1:
            return True

        return False

    def _create_mapping_rule(
        self,
        android_api: APISpec,
        harmony_api: APISpec,
        confidence: float,
        mapping_type: MappingType,
    ) -> MappingRule:
        """Create a mapping rule from two APIs."""
        # Analyze methods
        method_mappings = []
        for android_method in android_api.public_methods:
            method_mapping = self.analyze_method_mapping(android_method, harmony_api)
            if method_mapping:
                method_mappings.append(method_mapping)

        # Determine complexity based on method mapping success rate
        mapped_ratio = len(method_mappings) / max(len(android_api.public_methods), 1)
        if mapped_ratio >= 0.9:
            complexity = MappingComplexity.LOW
        elif mapped_ratio >= 0.7:
            complexity = MappingComplexity.MEDIUM
        elif mapped_ratio >= 0.5:
            complexity = MappingComplexity.HIGH
        else:
            complexity = MappingComplexity.VERY_HIGH

        return MappingRule(
            id=f"{android_api.full_qualified_name}_to_{harmony_api.full_qualified_name}",
            android_class=android_api.full_qualified_name,
            harmony_class=harmony_api.full_qualified_name,
            mapping_type=mapping_type,
            complexity=complexity,
            confidence=confidence,
            method_mappings=method_mappings,
        )

    async def _ai_semantic_match(
        self,
        android_api: APISpec,
        harmony_apis: List[APISpec]
    ) -> Optional[MappingRule]:
        """
        Use AI to find semantic matches.

        This method uses Claude to analyze API semantics and find the best match.
        """
        if not self.ai_client:
            return None

        # Prepare prompt
        prompt = self._build_semantic_match_prompt(android_api, harmony_apis)

        try:
            # Call AI
            response = await self.ai_client.complete(prompt)

            # Parse response
            return self._parse_ai_mapping_response(response, android_api, harmony_apis)
        except Exception as e:
            logger.error(f"AI semantic matching failed: {e}")
            return None

    def _build_semantic_match_prompt(
        self,
        android_api: APISpec,
        harmony_apis: List[APISpec]
    ) -> str:
        """Build prompt for AI semantic matching."""
        harmony_candidates = "\n".join([
            f"- {api.full_qualified_name}: {api.description or 'No description'}"
            for api in harmony_apis[:20]  # Limit candidates
        ])

        return f"""Analyze the following Android API and find the best matching HarmonyOS API.

Android API:
- Name: {android_api.full_qualified_name}
- Description: {android_api.description or 'No description'}
- Methods: {', '.join(m.name for m in android_api.public_methods[:10])}

Available HarmonyOS APIs:
{harmony_candidates}

Respond with:
1. Best matching HarmonyOS API name
2. Confidence score (0-1)
3. Mapping type (direct/semantic/bridge)
4. Brief reasoning

Format: JSON object with keys: harmony_api, confidence, mapping_type, reasoning
"""

    def _parse_ai_mapping_response(
        self,
        response: str,
        android_api: APISpec,
        harmony_apis: List[APISpec]
    ) -> Optional[MappingRule]:
        """Parse AI response and create mapping rule."""
        # TODO: Implement JSON parsing from AI response
        return None
