"""
Test Code Generator

Automatically generates test cases for adapters.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..core.api_spec import APISpec, MethodSpec
from ..core.mapping_rule import MappingRule, MethodMapping
from ..core.config import get_config


logger = logging.getLogger(__name__)


class TestGenerator:
    """
    Generates test cases for adapter code.

    Creates unit tests, integration tests, and compatibility tests.
    """

    def __init__(self):
        """Initialize the test generator."""
        self.config = get_config()

    def generate_unit_tests(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec,
        adapter_code: str
    ) -> str:
        """
        Generate unit tests for an adapter.

        Args:
            mapping_rule: The mapping rule.
            android_api: Source Android API.
            adapter_code: Generated adapter code.

        Returns:
            Generated test code as string.
        """
        context = self._build_test_context(mapping_rule, android_api)
        return self._generate_junit_tests(context)

    def generate_integration_tests(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec,
        harmony_api: APISpec
    ) -> str:
        """
        Generate integration tests that verify adapter behavior.

        Args:
            mapping_rule: The mapping rule.
            android_api: Source Android API.
            harmony_api: Target HarmonyOS API.

        Returns:
            Generated integration test code.
        """
        context = self._build_test_context(mapping_rule, android_api)
        context["harmony_api"] = harmony_api
        return self._generate_integration_tests(context)

    def _build_test_context(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec
    ) -> Dict[str, Any]:
        """Build context for test generation."""
        return {
            "generator_version": self.config.version,
            "generated_at": datetime.now().isoformat(),
            "mapping_rule": mapping_rule,
            "android_api": android_api,
            "adapter_class": f"{android_api.class_name}Adapter",
            "test_class": f"{android_api.class_name}AdapterTest",
            "package": f"craft.adapters.{android_api.package}",
        }

    def _generate_junit_tests(self, context: Dict[str, Any]) -> str:
        """Generate JUnit test class."""
        lines = [
            f"/**",
            f" * Auto-generated tests by CRAFT v{context['generator_version']}",
            f" * Testing: {context['adapter_class']}",
            f" * Generated: {context['generated_at']}",
            f" */",
            f"",
            f"package {context['package']};",
            f"",
            f"import org.junit.jupiter.api.Test;",
            f"import org.junit.jupiter.api.BeforeEach;",
            f"import org.junit.jupiter.api.DisplayName;",
            f"import static org.junit.jupiter.api.Assertions.*;",
            f"import static org.mockito.Mockito.*;",
            f"",
            f"class {context['test_class']} {{",
            f"",
            f"    private {context['adapter_class']} adapter;",
            f"",
            f"    @BeforeEach",
            f"    void setUp() {{",
            f"        // Initialize adapter with mock delegate",
            f"    }}",
            f"",
        ]

        # Generate test methods for each mapped method
        mapping_rule = context["mapping_rule"]
        android_api = context["android_api"]

        for method_mapping in mapping_rule.method_mappings:
            lines.extend(self._generate_method_test(method_mapping, android_api))
            lines.append("")

        lines.append("}")

        return "\n".join(lines)

    def _generate_method_test(
        self,
        method_mapping: MethodMapping,
        android_api: APISpec
    ) -> List[str]:
        """Generate test for a single method."""
        lines = []

        # Find the method spec
        android_method = android_api.get_method(method_mapping.android_method)
        if not android_method:
            return lines

        method_name = method_mapping.android_method
        test_name = f"test{method_name[0].upper()}{method_name[1:]}_ShouldDelegateToHarmony"

        lines.append(f"    @Test")
        lines.append(f"    @DisplayName(\"{method_name} should delegate to HarmonyOS API\")")
        lines.append(f"    void {test_name}() {{")
        lines.append(f"        // Arrange")
        lines.append(f"        // TODO: Set up test data")
        lines.append(f"")
        lines.append(f"        // Act")
        lines.append(f"        // TODO: Call adapter method")
        lines.append(f"")
        lines.append(f"        // Assert")
        lines.append(f"        // TODO: Verify delegation and result")
        lines.append(f"    }}")

        # Add edge case tests
        if android_method.parameters:
            lines.append("")
            lines.extend(self._generate_null_parameter_test(method_mapping, android_method))

        return lines

    def _generate_null_parameter_test(
        self,
        method_mapping: MethodMapping,
        android_method: MethodSpec
    ) -> List[str]:
        """Generate test for null parameter handling."""
        method_name = method_mapping.android_method
        test_name = f"test{method_name[0].upper()}{method_name[1:]}_WithNullParams_ShouldHandleGracefully"

        return [
            f"    @Test",
            f"    @DisplayName(\"{method_name} should handle null parameters\")",
            f"    void {test_name}() {{",
            f"        // Test null parameter handling",
            f"        // TODO: Implement based on API contract",
            f"    }}",
        ]

    def _generate_integration_tests(self, context: Dict[str, Any]) -> str:
        """Generate integration test class."""
        lines = [
            f"/**",
            f" * Integration tests for {context['adapter_class']}",
            f" * Tests actual integration with HarmonyOS APIs",
            f" */",
            f"",
            f"package {context['package']};",
            f"",
            f"import org.junit.jupiter.api.Test;",
            f"import org.junit.jupiter.api.condition.EnabledOnOs;",
            f"import org.junit.jupiter.api.condition.OS;",
            f"",
            f"class {context['test_class']}Integration {{",
            f"",
            f"    @Test",
            f"    @EnabledOnOs(OS.OTHER) // HarmonyOS",
            f"    void testRealHarmonyIntegration() {{",
            f"        // This test runs on actual HarmonyOS device",
            f"        // TODO: Implement real integration test",
            f"    }}",
            f"}}",
        ]

        return "\n".join(lines)

    def save(
        self,
        test_code: str,
        mapping_rule: MappingRule,
        test_type: str = "unit"
    ) -> Path:
        """
        Save generated test code to file.

        Args:
            test_code: Generated test code.
            mapping_rule: The mapping rule.
            test_type: Type of test (unit, integration).

        Returns:
            Path to the saved test file.
        """
        package_dir = mapping_rule.android_class.rsplit(".", 1)[0].replace(".", "/")
        class_name = mapping_rule.android_class.rsplit(".", 1)[1]

        suffix = "" if test_type == "unit" else "Integration"
        output_path = (
            self.config.paths.output_dir / "tests" / test_type / package_dir /
            f"{class_name}Adapter{suffix}Test.java"
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(test_code)

        logger.info(f"Saved {test_type} tests to: {output_path}")
        return output_path
