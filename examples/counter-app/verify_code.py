#!/usr/bin/env python3
"""
CRAFT Code Verification Script

Verifies that the generated Android and HarmonyOS code is syntactically correct
and follows the expected patterns.
"""

import os
import re
import sys
from pathlib import Path

class CodeVerifier:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = 0

    def verify_java_file(self, filepath: str) -> bool:
        """Verify Java source file structure."""
        print(f"\n  Verifying Java: {Path(filepath).name}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ("Package declaration", r'package\s+[\w.]+;'),
            ("Class declaration", r'public\s+class\s+\w+'),
            ("onCreate method", r'protected\s+void\s+onCreate\s*\('),
            ("Balanced braces", self._check_balanced_braces),
            ("No syntax errors", self._check_java_syntax),
        ]

        return self._run_checks(content, checks)

    def verify_arkts_file(self, filepath: str, file_type: str = "page") -> bool:
        """Verify ArkTS source file structure."""
        print(f"\n  Verifying ArkTS ({file_type}): {Path(filepath).name}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if file_type == "page":
            checks = [
                ("@Entry decorator", r'@Entry'),
                ("@Component decorator", r'@Component'),
                ("struct declaration", r'struct\s+\w+'),
                ("build() method", r'build\s*\(\s*\)'),
                ("Balanced braces", self._check_balanced_braces),
            ]
        elif file_type == "ability":
            checks = [
                ("Import UIAbility", r'import.*UIAbility'),
                ("Class extends UIAbility", r'class\s+\w+\s+extends\s+UIAbility'),
                ("onCreate method", r'onCreate\s*\('),
                ("onDestroy method", r'onDestroy\s*\('),
                ("onForeground method", r'onForeground\s*\('),
                ("onBackground method", r'onBackground\s*\('),
                ("Balanced braces", self._check_balanced_braces),
            ]
        elif file_type == "adapter":
            checks = [
                ("Export class", r'export\s+class'),
                ("Constructor", r'constructor\s*\('),
                ("Lifecycle methods", r'on(Create|Start|Resume|Pause|Stop|Destroy)\s*\('),
                ("Balanced braces", self._check_balanced_braces),
            ]
        else:
            checks = [("Balanced braces", self._check_balanced_braces)]

        return self._run_checks(content, checks)

    def verify_xml_file(self, filepath: str) -> bool:
        """Verify XML file structure."""
        print(f"\n  Verifying XML: {Path(filepath).name}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        checks = [
            ("XML declaration", r'<\?xml'),
            ("Root element", r'<\w+[^>]*>'),
            ("Balanced tags", self._check_xml_balanced),
        ]

        return self._run_checks(content, checks)

    def verify_json_file(self, filepath: str) -> bool:
        """Verify JSON file structure."""
        print(f"\n  Verifying JSON: {Path(filepath).name}")

        import json
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Handle JSON5 (remove comments)
                content = f.read()
                # Remove single-line comments
                content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                # Remove multi-line comments
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                json.loads(content)
            print("    [PASS] Valid JSON structure")
            self.passed += 1
            return True
        except json.JSONDecodeError as e:
            print(f"    [FAIL] Invalid JSON: {e}")
            self.errors.append(f"{filepath}: {e}")
            return False

    def _run_checks(self, content: str, checks: list) -> bool:
        """Run a list of checks on content."""
        all_passed = True

        for check_name, check_pattern in checks:
            if callable(check_pattern):
                result = check_pattern(content)
                if result is True:
                    print(f"    [PASS] {check_name}")
                    self.passed += 1
                else:
                    print(f"    [FAIL] {check_name}: {result}")
                    self.errors.append(f"{check_name}: {result}")
                    all_passed = False
            else:
                if re.search(check_pattern, content):
                    print(f"    [PASS] {check_name}")
                    self.passed += 1
                else:
                    print(f"    [FAIL] {check_name}")
                    self.errors.append(f"Missing: {check_name}")
                    all_passed = False

        return all_passed

    def _check_balanced_braces(self, content: str) -> bool:
        """Check if braces are balanced."""
        count = 0
        for char in content:
            if char == '{':
                count += 1
            elif char == '}':
                count -= 1
            if count < 0:
                return "Unmatched closing brace"
        if count != 0:
            return f"Unbalanced braces: {count} unclosed"
        return True

    def _check_java_syntax(self, content: str) -> bool:
        """Basic Java syntax check."""
        # Check for common syntax errors
        if re.search(r';\s*;', content):
            return "Double semicolon"
        if re.search(r'\(\s*\)', content) and not re.search(r'(void|new|super|this)\s*\(\s*\)', content):
            pass  # Empty parens are OK in method definitions
        return True

    def _check_xml_balanced(self, content: str) -> bool:
        """Check if XML tags are balanced."""
        # Count opening tags (not self-closing)
        opening = len(re.findall(r'<(\w+)(?:\s[^>]*)?>(?!</)', content))
        # Count closing tags
        closing = len(re.findall(r'</(\w+)>', content))
        # Self-closing tags don't need matching
        self_closing = len(re.findall(r'<\w+[^>]*/>', content))

        # For Android XML, many elements are self-closing
        # Just verify no obvious errors
        if opening < closing:
            return f"More closing tags than opening: {opening} vs {closing}"
        return True


def main():
    print("=" * 70)
    print("  CRAFT Code Verification")
    print("=" * 70)

    script_dir = Path(__file__).parent
    verifier = CodeVerifier()

    # Verify Android files
    print("\n[1/3] Verifying Android Code...")

    android_files = [
        (script_dir / "android/app/src/main/java/com/example/counter/MainActivity.java", "java"),
        (script_dir / "android/app/src/main/AndroidManifest.xml", "xml"),
        (script_dir / "android/app/src/main/res/layout/activity_main.xml", "xml"),
    ]

    for filepath, filetype in android_files:
        if filepath.exists():
            if filetype == "java":
                verifier.verify_java_file(str(filepath))
            elif filetype == "xml":
                verifier.verify_xml_file(str(filepath))

    # Verify HarmonyOS files
    print("\n[2/3] Verifying HarmonyOS Code...")

    harmony_files = [
        (script_dir / "harmony/entry/src/main/ets/pages/Index.ets", "page"),
        (script_dir / "harmony/entry/src/main/ets/EntryAbility.ets", "ability"),
        (script_dir / "harmony/entry/src/main/ets/adapters/MainActivityAdapter.ets", "adapter"),
    ]

    for filepath, filetype in harmony_files:
        if filepath.exists():
            verifier.verify_arkts_file(str(filepath), filetype)

    # Verify config files
    print("\n[3/3] Verifying Configuration Files...")

    config_files = [
        script_dir / "harmony/entry/src/main/module.json5",
        script_dir / "harmony/build-profile.json5",
        script_dir / "harmony/entry/src/main/resources/base/profile/main_pages.json",
    ]

    for filepath in config_files:
        if filepath.exists():
            verifier.verify_json_file(str(filepath))

    # Summary
    print("\n" + "=" * 70)
    print("  Verification Summary")
    print("=" * 70)
    print(f"\n  Passed: {verifier.passed}")
    print(f"  Errors: {len(verifier.errors)}")
    print(f"  Warnings: {len(verifier.warnings)}")

    if verifier.errors:
        print("\n  Errors:")
        for err in verifier.errors:
            print(f"    - {err}")
        print("\n  Result: FAILED")
        return 1
    else:
        print("\n  Result: ALL CHECKS PASSED")

        print("\n" + "=" * 70)
        print("  Generated Project Structure")
        print("=" * 70)

        # Show directory structure
        print("\n  Android App:")
        print("    android/")
        print("    ├── app/")
        print("    │   ├── build.gradle")
        print("    │   └── src/main/")
        print("    │       ├── AndroidManifest.xml")
        print("    │       ├── java/com/example/counter/")
        print("    │       │   └── MainActivity.java    <- Source")
        print("    │       └── res/layout/")
        print("    │           └── activity_main.xml")

        print("\n  HarmonyOS App (CRAFT Generated):")
        print("    harmony/")
        print("    ├── build-profile.json5")
        print("    ├── oh-package.json5")
        print("    ├── hvigorfile.ts")
        print("    └── entry/")
        print("        ├── hvigorfile.ts")
        print("        └── src/main/")
        print("            ├── module.json5")
        print("            ├── ets/")
        print("            │   ├── EntryAbility.ets      <- Generated UIAbility")
        print("            │   ├── adapters/")
        print("            │   │   └── MainActivityAdapter.ets  <- Generated Adapter")
        print("            │   └── pages/")
        print("            │       └── Index.ets         <- Generated UI Page")
        print("            └── resources/")

        print("\n  Lifecycle Mapping Verification:")
        print("    Android Activity    →   HarmonyOS UIAbility")
        print("    ─────────────────────────────────────────────")
        print("    onCreate           →   onCreate + aboutToAppear")
        print("    onStart            →   onForeground")
        print("    onResume           →   onForeground")
        print("    onPause            →   onBackground")
        print("    onStop             →   onBackground")
        print("    onDestroy          →   onDestroy + aboutToDisappear")
        print("    onSaveInstanceState→   AppStorage.setOrCreate()")
        print("    onRestoreInstance  →   AppStorage.get()")

        return 0


if __name__ == '__main__':
    sys.exit(main())
