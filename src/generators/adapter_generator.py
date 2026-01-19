"""
Adapter Code Generator

Generates adapter code that bridges Android APIs to HarmonyOS APIs.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader

from ..core.api_spec import APISpec
from ..core.mapping_rule import MappingRule, MappingType
from ..core.config import get_config


logger = logging.getLogger(__name__)


class AdapterGenerator:
    """
    Generates adapter code from mapping rules.

    Supports multiple output formats: Java, Kotlin, and ArkTS.
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the adapter generator.

        Args:
            templates_dir: Path to Jinja2 templates directory.
        """
        self.config = get_config()
        templates_dir = templates_dir or self.config.paths.templates_dir

        # Initialize Jinja2 environment
        if templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            self.jinja_env = None
            logger.warning(f"Templates directory not found: {templates_dir}")

    def generate(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec,
        harmony_api: APISpec,
        output_format: str = "java"
    ) -> str:
        """
        Generate adapter code from a mapping rule.

        Args:
            mapping_rule: The mapping rule defining the adaptation.
            android_api: Source Android API spec.
            harmony_api: Target HarmonyOS API spec.
            output_format: Output format (java, kotlin, arkts).

        Returns:
            Generated adapter code as string.
        """
        # Select generation strategy based on mapping type
        if mapping_rule.mapping_type == MappingType.DIRECT:
            return self._generate_direct_adapter(
                mapping_rule, android_api, harmony_api, output_format
            )
        elif mapping_rule.mapping_type == MappingType.SEMANTIC:
            return self._generate_semantic_adapter(
                mapping_rule, android_api, harmony_api, output_format
            )
        elif mapping_rule.mapping_type in (MappingType.BRIDGE, MappingType.SHIM):
            return self._generate_bridge_adapter(
                mapping_rule, android_api, harmony_api, output_format
            )
        else:
            raise ValueError(f"Unsupported mapping type: {mapping_rule.mapping_type}")

    def _generate_direct_adapter(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec,
        harmony_api: APISpec,
        output_format: str
    ) -> str:
        """Generate adapter for direct 1:1 mapping."""
        context = self._build_template_context(mapping_rule, android_api, harmony_api)

        if output_format == "java":
            return self._generate_java_adapter(context)
        elif output_format == "kotlin":
            return self._generate_kotlin_adapter(context)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_semantic_adapter(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec,
        harmony_api: APISpec,
        output_format: str
    ) -> str:
        """Generate adapter for semantic mapping (requires transformation)."""
        context = self._build_template_context(mapping_rule, android_api, harmony_api)
        context["requires_transformation"] = True

        if output_format == "java":
            return self._generate_java_adapter(context)
        elif output_format == "kotlin":
            return self._generate_kotlin_adapter(context)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_bridge_adapter(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec,
        harmony_api: APISpec,
        output_format: str
    ) -> str:
        """Generate adapter that requires bridge code."""
        context = self._build_template_context(mapping_rule, android_api, harmony_api)
        context["requires_bridge"] = True
        context["bridge_code"] = mapping_rule.bridge_code

        if output_format == "java":
            return self._generate_java_adapter(context)
        elif output_format == "kotlin":
            return self._generate_kotlin_adapter(context)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _build_template_context(
        self,
        mapping_rule: MappingRule,
        android_api: APISpec,
        harmony_api: APISpec
    ) -> Dict[str, Any]:
        """Build context dictionary for template rendering."""
        return {
            # Metadata
            "generator_version": self.config.version,
            "generated_at": datetime.now().isoformat(),
            "confidence": mapping_rule.confidence,

            # Android API info
            "android_package": android_api.package,
            "android_class": android_api.class_name,
            "android_full_name": android_api.full_qualified_name,
            "android_methods": android_api.public_methods,

            # HarmonyOS API info
            "harmony_package": harmony_api.package,
            "harmony_class": harmony_api.class_name,
            "harmony_full_name": harmony_api.full_qualified_name,
            "harmony_methods": harmony_api.public_methods,

            # Mapping info
            "mapping_type": mapping_rule.mapping_type.value,
            "method_mappings": mapping_rule.method_mappings,
            "requires_imports": mapping_rule.requires_imports,

            # Adapter info
            "adapter_package": f"craft.adapters.{android_api.package}",
            "adapter_class": f"{android_api.class_name}Adapter",
        }

    def _generate_java_adapter(self, context: Dict[str, Any]) -> str:
        """Generate Java adapter code."""
        # Try template-based generation first
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template("adapter_java.jinja2")
                return template.render(**context)
            except Exception as e:
                logger.warning(f"Template rendering failed, using inline: {e}")

        # Fallback to inline generation
        return self._generate_java_adapter_inline(context)

    def _generate_java_adapter_inline(self, context: Dict[str, Any]) -> str:
        """Generate Java adapter code without template."""
        lines = [
            f"/**",
            f" * Auto-generated by CRAFT v{context['generator_version']}",
            f" * Source: {context['android_full_name']}",
            f" * Target: {context['harmony_full_name']}",
            f" * Confidence: {context['confidence']}",
            f" * Generated: {context['generated_at']}",
            f" *",
            f" * DO NOT EDIT MANUALLY - regenerate using CRAFT pipeline",
            f" */",
            f"",
            f"package {context['adapter_package']};",
            f"",
        ]

        # Add imports
        lines.append(f"import {context['android_full_name']};")
        lines.append(f"import {context['harmony_full_name']};")
        for imp in context.get("requires_imports", []):
            lines.append(f"import {imp};")
        lines.append("")

        # Class declaration
        lines.append(f"public class {context['adapter_class']} extends {context['android_class']} {{")
        lines.append("")
        lines.append(f"    private final {context['harmony_class']} delegate;")
        lines.append("")

        # Constructor
        lines.append(f"    public {context['adapter_class']}({context['harmony_class']} delegate) {{")
        lines.append(f"        this.delegate = delegate;")
        lines.append(f"    }}")
        lines.append("")

        # Generate method adapters
        for method_mapping in context.get("method_mappings", []):
            lines.extend(self._generate_method_adapter(method_mapping, context))
            lines.append("")

        lines.append("}")

        return "\n".join(lines)

    def _generate_method_adapter(
        self,
        method_mapping,
        context: Dict[str, Any]
    ) -> list:
        """Generate a single method adapter."""
        lines = []

        # Find Android method spec
        android_method = None
        for m in context.get("android_methods", []):
            if m.name == method_mapping.android_method:
                android_method = m
                break

        if not android_method:
            return lines

        # Method signature
        params_str = ", ".join(
            f"{p.type} {p.name}" for p in android_method.parameters
        )
        lines.append(f"    @Override")
        lines.append(f"    public {android_method.return_type} {android_method.name}({params_str}) {{")

        # Method body
        if method_mapping.pre_call_code:
            lines.append(f"        {method_mapping.pre_call_code}")

        # Delegate call
        harmony_params = ", ".join(p.name for p in android_method.parameters)
        if android_method.return_type != "void":
            lines.append(f"        return delegate.{method_mapping.harmony_method}({harmony_params});")
        else:
            lines.append(f"        delegate.{method_mapping.harmony_method}({harmony_params});")

        if method_mapping.post_call_code:
            lines.append(f"        {method_mapping.post_call_code}")

        lines.append(f"    }}")

        return lines

    def _generate_kotlin_adapter(self, context: Dict[str, Any]) -> str:
        """Generate Kotlin adapter code."""
        # Similar to Java but with Kotlin syntax
        lines = [
            f"/**",
            f" * Auto-generated by CRAFT v{context['generator_version']}",
            f" * Source: {context['android_full_name']}",
            f" * Target: {context['harmony_full_name']}",
            f" */",
            f"",
            f"package {context['adapter_package']}",
            f"",
            f"import {context['android_full_name']}",
            f"import {context['harmony_full_name']}",
            f"",
            f"class {context['adapter_class']}(",
            f"    private val delegate: {context['harmony_class']}",
            f") : {context['android_class']}() {{",
            f"",
        ]

        # Generate method adapters
        for method_mapping in context.get("method_mappings", []):
            lines.extend(self._generate_kotlin_method_adapter(method_mapping, context))
            lines.append("")

        lines.append("}")

        return "\n".join(lines)

    def _generate_kotlin_method_adapter(
        self,
        method_mapping,
        context: Dict[str, Any]
    ) -> list:
        """Generate a single Kotlin method adapter."""
        lines = []

        # Find Android method spec
        android_method = None
        for m in context.get("android_methods", []):
            if m.name == method_mapping.android_method:
                android_method = m
                break

        if not android_method:
            return lines

        # Method signature
        params_str = ", ".join(
            f"{p.name}: {self._java_to_kotlin_type(p.type)}"
            for p in android_method.parameters
        )
        return_type = self._java_to_kotlin_type(android_method.return_type)

        if return_type == "Unit":
            lines.append(f"    override fun {android_method.name}({params_str}) {{")
        else:
            lines.append(f"    override fun {android_method.name}({params_str}): {return_type} {{")

        # Method body
        harmony_params = ", ".join(p.name for p in android_method.parameters)
        if return_type != "Unit":
            lines.append(f"        return delegate.{method_mapping.harmony_method}({harmony_params})")
        else:
            lines.append(f"        delegate.{method_mapping.harmony_method}({harmony_params})")

        lines.append(f"    }}")

        return lines

    def _java_to_kotlin_type(self, java_type: str) -> str:
        """Convert Java type to Kotlin type."""
        type_map = {
            "void": "Unit",
            "int": "Int",
            "long": "Long",
            "float": "Float",
            "double": "Double",
            "boolean": "Boolean",
            "char": "Char",
            "byte": "Byte",
            "short": "Short",
            "String": "String",
        }
        return type_map.get(java_type, java_type)

    def save(
        self,
        code: str,
        mapping_rule: MappingRule,
        output_format: str = "java"
    ) -> Path:
        """
        Save generated code to file.

        Args:
            code: Generated code string.
            mapping_rule: The mapping rule (for file naming).
            output_format: Output format (java, kotlin).

        Returns:
            Path to the saved file.
        """
        # Determine output path
        package_dir = mapping_rule.android_class.rsplit(".", 1)[0].replace(".", "/")
        class_name = mapping_rule.android_class.rsplit(".", 1)[1]

        ext = "java" if output_format == "java" else "kt"
        output_path = (
            self.config.paths.output_dir / "adapters" / package_dir /
            f"{class_name}Adapter.{ext}"
        )

        # Create directory and save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code)

        logger.info(f"Saved adapter to: {output_path}")
        return output_path
