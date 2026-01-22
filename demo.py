#!/usr/bin/env python3
"""
CRAFT Framework Demo
====================
This demo simulates the CRAFT pipeline without requiring Rust compilation.
It demonstrates: Parsing -> Analysis -> Code Generation

Run: python3 demo.py
"""

import re
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

# ============================================================================
# Data Structures (mirrors Rust craft-core)
# ============================================================================

@dataclass
class ParameterSpec:
    name: str
    param_type: str
    nullable: bool = False

@dataclass
class MethodSpec:
    name: str
    return_type: str
    parameters: List[ParameterSpec] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    semantic_tags: List[str] = field(default_factory=list)
    doc_comment: Optional[str] = None

@dataclass
class ApiSpec:
    platform: str
    package: str
    class_name: str
    class_type: str = "class"
    parent_class: Optional[str] = None
    interfaces: List[str] = field(default_factory=list)
    methods: List[MethodSpec] = field(default_factory=list)
    semantic_tags: List[str] = field(default_factory=list)

# ============================================================================
# Simple Java Parser (simulates tree-sitter parsing)
# ============================================================================

class JavaParser:
    """Simple Java parser for demonstration purposes."""

    LIFECYCLE_METHODS = [
        "onCreate", "onStart", "onResume", "onPause",
        "onStop", "onDestroy", "onSaveInstanceState",
        "onRestoreInstanceState", "onAttach", "onDetach",
        "onCreateView", "onDestroyView"
    ]

    def parse_file(self, file_path: str) -> Optional[ApiSpec]:
        """Parse a Java file and extract API specification."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract package
        package_match = re.search(r'package\s+([\w.]+)\s*;', content)
        package = package_match.group(1) if package_match else "unknown"

        # Extract class declaration
        class_match = re.search(
            r'public\s+(abstract\s+)?(class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?',
            content
        )

        if not class_match:
            return None

        is_abstract = class_match.group(1) is not None
        class_type = "abstract_class" if is_abstract else class_match.group(2)
        class_name = class_match.group(3)
        parent_class = class_match.group(4)
        interfaces = []
        if class_match.group(5):
            interfaces = [i.strip() for i in class_match.group(5).split(',')]

        # Extract methods
        methods = self._extract_methods(content)

        # Generate semantic tags
        semantic_tags = self._generate_class_tags(class_name, class_type)

        return ApiSpec(
            platform="Android",
            package=package,
            class_name=class_name,
            class_type=class_type,
            parent_class=parent_class,
            interfaces=interfaces,
            methods=methods,
            semantic_tags=semantic_tags
        )

    def _extract_methods(self, content: str) -> List[MethodSpec]:
        """Extract method signatures from Java content."""
        methods = []

        # Pattern for method declaration
        method_pattern = re.compile(
            r'/\*\*(.*?)\*/\s*'  # Optional JavaDoc
            r'((?:public|protected|private|static|final|abstract|\s)+)'  # Modifiers
            r'(\w+(?:<[\w<>,\s]+>)?)\s+'  # Return type
            r'(\w+)\s*'  # Method name
            r'\(([^)]*)\)',  # Parameters
            re.DOTALL
        )

        for match in method_pattern.finditer(content):
            doc_comment = match.group(1).strip() if match.group(1) else None
            modifiers = match.group(2).split()
            return_type = match.group(3)
            method_name = match.group(4)
            params_str = match.group(5)

            # Parse parameters
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        parts = param.split()
                        if len(parts) >= 2:
                            param_type = parts[-2]
                            param_name = parts[-1]
                            parameters.append(ParameterSpec(param_name, param_type))

            # Generate semantic tags
            semantic_tags = self._generate_method_tags(method_name, return_type)

            methods.append(MethodSpec(
                name=method_name,
                return_type=return_type,
                parameters=parameters,
                modifiers=[m for m in modifiers if m],
                semantic_tags=semantic_tags,
                doc_comment=self._clean_doc(doc_comment) if doc_comment else None
            ))

        return methods

    def _generate_class_tags(self, class_name: str, class_type: str) -> List[str]:
        """Generate semantic tags for a class."""
        tags = [f"type:{class_type}"]

        lower_name = class_name.lower()
        if "activity" in lower_name:
            tags.append("component:activity")
        elif "fragment" in lower_name:
            tags.append("component:fragment")
        elif "service" in lower_name:
            tags.append("component:service")
        elif "view" in lower_name:
            tags.append("component:view")

        return tags

    def _generate_method_tags(self, name: str, return_type: str) -> List[str]:
        """Generate semantic tags for a method."""
        tags = [f"returns:{return_type}"]

        lower_name = name.lower()
        if lower_name.startswith("get") or lower_name.startswith("is"):
            tags.append("category:getter")
        elif lower_name.startswith("set"):
            tags.append("category:setter")
        elif lower_name.startswith("on"):
            tags.append("category:callback")

        if name in self.LIFECYCLE_METHODS:
            tags.append("lifecycle:true")
            tags.append(f"lifecycle:{name}")

        return tags

    def _clean_doc(self, doc: str) -> str:
        """Clean up JavaDoc comment."""
        lines = doc.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip().lstrip('*').strip()
            if line and not line.startswith('@'):
                cleaned.append(line)
        return ' '.join(cleaned)[:100]

# ============================================================================
# Lifecycle Mapping (mirrors Rust implementation)
# ============================================================================

LIFECYCLE_MAPPING = {
    "onCreate": ("onCreate", "Bundle to Want transformation"),
    "onStart": ("onForeground", None),
    "onResume": ("onForeground", "Note: onResume maps to onForeground in HarmonyOS"),
    "onPause": ("onBackground", None),
    "onStop": ("onBackground", "Note: onStop maps to onBackground in HarmonyOS"),
    "onDestroy": ("onDestroy", None),
    "onSaveInstanceState": ("saveStateToAppStorage", "Use AppStorage for state persistence"),
    "onRestoreInstanceState": ("restoreStateFromAppStorage", "Use AppStorage for state restoration"),
    "onAttach": ("aboutToAppear", None),
    "onDetach": ("aboutToDisappear", None),
    "onCreateView": ("build", "onCreateView maps to build() in ArkUI"),
}

# ============================================================================
# Code Generator (mirrors Rust implementation)
# ============================================================================

class AdapterGenerator:
    """Generate adapter code in Java, Kotlin, and ArkTS."""

    def generate_java(self, source: ApiSpec, target_class: str) -> str:
        """Generate Java adapter code."""
        adapter_class = f"{source.class_name}Adapter"
        adapter_package = f"craft.adapters.{source.package}"

        methods_code = []
        for method in source.methods:
            if "public" not in method.modifiers and "protected" not in method.modifiers:
                continue

            # Check if this is a lifecycle method
            if method.name in LIFECYCLE_MAPPING:
                target_method, comment = LIFECYCLE_MAPPING[method.name]
                methods_code.append(self._generate_lifecycle_method_java(method, target_method, comment))
            else:
                methods_code.append(self._generate_delegation_method_java(method))

        return f'''/**
 * Auto-generated by CRAFT v0.1.0
 * Source: {source.package}.{source.class_name}
 * Target: ohos.app.ability.{target_class}
 *
 * This adapter provides compatibility layer between Android and HarmonyOS APIs.
 */

package {adapter_package};

import {source.package}.{source.class_name};
import ohos.app.ability.{target_class};

public class {adapter_class} extends {source.class_name} {{

    private final {target_class} delegate;

    public {adapter_class}({target_class} delegate) {{
        this.delegate = delegate;
    }}

    public {target_class} getDelegate() {{
        return this.delegate;
    }}

{chr(10).join(methods_code)}
}}
'''

    def _generate_lifecycle_method_java(self, method: MethodSpec, target_method: str, comment: Optional[str]) -> str:
        """Generate a lifecycle method with mapping."""
        params_str = ", ".join(f"{p.param_type} {p.name}" for p in method.parameters)
        delegate_params = ", ".join(p.name for p in method.parameters)

        comment_line = f"\n        // {comment}" if comment else ""

        modifiers = " ".join(method.modifiers) if method.modifiers else "public"

        return f'''    /**
     * Lifecycle adapter: {method.name} -> {target_method}
     * Maps Android {method.name} to HarmonyOS {target_method}
     */
    @Override
    {modifiers} {method.return_type} {method.name}({params_str}) {{{comment_line}
        delegate.{target_method}({delegate_params});
    }}
'''

    def _generate_delegation_method_java(self, method: MethodSpec) -> str:
        """Generate a simple delegation method."""
        params_str = ", ".join(f"{p.param_type} {p.name}" for p in method.parameters)
        delegate_params = ", ".join(p.name for p in method.parameters)

        modifiers = " ".join(method.modifiers) if method.modifiers else "public"

        if method.return_type == "void":
            return_stmt = f"delegate.{method.name}({delegate_params});"
        else:
            return_stmt = f"return delegate.{method.name}({delegate_params});"

        return f'''    /**
     * Delegated method: {method.name}
     */
    @Override
    {modifiers} {method.return_type} {method.name}({params_str}) {{
        {return_stmt}
    }}
'''

    def generate_arkts(self, source: ApiSpec, target_class: str) -> str:
        """Generate ArkTS adapter code."""
        adapter_class = f"{source.class_name}Adapter"

        methods_code = []
        for method in source.methods:
            if "public" not in method.modifiers and "protected" not in method.modifiers:
                continue

            ts_return = self._java_to_ts_type(method.return_type)
            params_str = ", ".join(
                f"{p.name}: {self._java_to_ts_type(p.param_type)}"
                for p in method.parameters
            )
            delegate_params = ", ".join(p.name for p in method.parameters)

            if method.name in LIFECYCLE_MAPPING:
                target_method, _ = LIFECYCLE_MAPPING[method.name]
            else:
                target_method = method.name

            if ts_return == "void":
                body = f"this.delegate.{target_method}({delegate_params});"
            else:
                body = f"return this.delegate.{target_method}({delegate_params});"

            methods_code.append(f'''    /**
     * Adapted method: {method.name} -> {target_method}
     */
    {method.name}({params_str}): {ts_return} {{
        {body}
    }}
''')

        return f'''/**
 * Auto-generated by CRAFT v0.1.0
 * Source: {source.package}.{source.class_name}
 * Target: ohos.app.ability.{target_class}
 */

import {{ {target_class} }} from '@ohos.app.ability';

/**
 * Adapter class providing {source.class_name} API over HarmonyOS {target_class}.
 */
export class {adapter_class} {{
    private delegate: {target_class};

    constructor(delegate: {target_class}) {{
        this.delegate = delegate;
    }}

    getDelegate(): {target_class} {{
        return this.delegate;
    }}

{chr(10).join(methods_code)}
}}
'''

    def _java_to_ts_type(self, java_type: str) -> str:
        """Convert Java type to TypeScript type."""
        type_map = {
            "void": "void",
            "int": "number",
            "long": "number",
            "float": "number",
            "double": "number",
            "boolean": "boolean",
            "String": "string",
            "CharSequence": "string",
            "Object": "any",
            "Bundle": "Record<string, any>",
            "Intent": "Want",
            "View": "Component",
        }
        return type_map.get(java_type, java_type)

# ============================================================================
# Demo Runner
# ============================================================================

def print_separator(title: str):
    """Print a visual separator."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_api_spec(api: ApiSpec):
    """Pretty print an ApiSpec."""
    print(f"\n  Package: {api.package}")
    print(f"  Class: {api.class_name}")
    print(f"  Type: {api.class_type}")
    print(f"  Parent: {api.parent_class or 'None'}")
    print(f"  Interfaces: {', '.join(api.interfaces) if api.interfaces else 'None'}")
    print(f"  Semantic Tags: {api.semantic_tags}")
    print(f"\n  Methods ({len(api.methods)} total):")

    for method in api.methods[:10]:  # Show first 10 methods
        params = ", ".join(f"{p.param_type} {p.name}" for p in method.parameters)
        lifecycle_marker = " [LIFECYCLE]" if any("lifecycle:true" in t for t in method.semantic_tags) else ""
        print(f"    - {method.return_type} {method.name}({params}){lifecycle_marker}")

    if len(api.methods) > 10:
        print(f"    ... and {len(api.methods) - 10} more methods")

def run_demo():
    """Run the CRAFT framework demo."""
    print("\n" + "🚀" * 35)
    print("\n           CRAFT Framework Demo")
    print("    Cross-platform API Adaptation Layer Generator")
    print("\n" + "🚀" * 35)

    # Get the script directory
    script_dir = Path(__file__).parent
    fixtures_dir = script_dir / "tests" / "fixtures"

    # ========================================================================
    # Step 1: Parse Android SDK
    # ========================================================================
    print_separator("Step 1: Parsing Android SDK (Java)")

    parser = JavaParser()
    activity_path = fixtures_dir / "android" / "app" / "Activity.java"

    if not activity_path.exists():
        print(f"  ❌ Fixture not found: {activity_path}")
        print("  Please run: python3 demo.py from the CRAFT directory")
        return

    activity_api = parser.parse_file(str(activity_path))

    if activity_api:
        print(f"  ✅ Successfully parsed: {activity_path.name}")
        print_api_spec(activity_api)
    else:
        print(f"  ❌ Failed to parse: {activity_path}")
        return

    # Parse Fragment too
    fragment_path = fixtures_dir / "android" / "app" / "Fragment.java"
    if fragment_path.exists():
        fragment_api = parser.parse_file(str(fragment_path))
        if fragment_api:
            print(f"\n  ✅ Also parsed: {fragment_path.name}")
            print(f"     {len(fragment_api.methods)} methods found")

    # ========================================================================
    # Step 2: Show Lifecycle Mapping
    # ========================================================================
    print_separator("Step 2: Activity → UIAbility Lifecycle Mapping")

    print("\n  Android Activity      →    HarmonyOS UIAbility")
    print("  " + "-" * 50)

    for android_method, (harmony_method, note) in LIFECYCLE_MAPPING.items():
        note_str = f" ({note})" if note else ""
        print(f"  {android_method:20} →    {harmony_method}{note_str}")

    # ========================================================================
    # Step 3: Generate Java Adapter
    # ========================================================================
    print_separator("Step 3: Generating Java Adapter Code")

    generator = AdapterGenerator()
    java_code = generator.generate_java(activity_api, "UIAbility")

    print("\n  Generated ActivityAdapter.java:")
    print("  " + "-" * 50)

    # Show first 60 lines
    lines = java_code.split('\n')
    for i, line in enumerate(lines[:60]):
        print(f"  {line}")

    if len(lines) > 60:
        print(f"\n  ... ({len(lines) - 60} more lines)")

    # ========================================================================
    # Step 4: Generate ArkTS Adapter
    # ========================================================================
    print_separator("Step 4: Generating ArkTS Adapter Code")

    arkts_code = generator.generate_arkts(activity_api, "UIAbility")

    print("\n  Generated ActivityAdapter.ets:")
    print("  " + "-" * 50)

    # Show first 50 lines
    lines = arkts_code.split('\n')
    for i, line in enumerate(lines[:50]):
        print(f"  {line}")

    if len(lines) > 50:
        print(f"\n  ... ({len(lines) - 50} more lines)")

    # ========================================================================
    # Summary
    # ========================================================================
    print_separator("Demo Summary")

    print(f"""
  ✅ Parsed Android APIs:
     - Activity ({len(activity_api.methods)} methods)
     - Fragment (if available)

  ✅ Lifecycle Mapping:
     - {len(LIFECYCLE_MAPPING)} Android lifecycle methods mapped to HarmonyOS

  ✅ Generated Adapters:
     - Java: ActivityAdapter.java ({len(java_code)} characters)
     - ArkTS: ActivityAdapter.ets ({len(arkts_code)} characters)

  📝 Key Features Demonstrated:
     1. Java source parsing with method extraction
     2. Semantic tag generation (lifecycle, getter/setter detection)
     3. Activity → UIAbility lifecycle mapping
     4. Java adapter code generation with method delegation
     5. ArkTS adapter code generation with type conversion

  🔧 To run the full Rust implementation:
     1. Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
     2. Run tests: cargo test
     3. Run CLI: cargo run -p craft-cli -- parse --platform android --sdk-path ./tests/fixtures/android
""")

if __name__ == "__main__":
    run_demo()
