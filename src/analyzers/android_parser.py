"""
Android SDK Parser

Parses Android SDK source code to extract API specifications.
"""

from pathlib import Path
from typing import List, Optional, Dict, Generator
import logging
import re

from ..core.api_spec import APISpec, MethodSpec, ParameterSpec, Platform, Visibility


logger = logging.getLogger(__name__)


class AndroidParser:
    """
    Parser for Android SDK source code.

    Extracts API specifications from Java source files in the Android SDK.
    """

    # Common Android packages to parse
    CORE_PACKAGES = [
        "android.app",
        "android.content",
        "android.os",
        "android.view",
        "android.widget",
        "android.graphics",
        "android.media",
        "android.net",
        "android.database",
        "android.provider",
        "android.util",
        "android.text",
        "android.webkit",
        "android.bluetooth",
        "android.location",
        "android.hardware",
        "android.accounts",
        "android.animation",
        "android.preference",
    ]

    def __init__(self, sdk_path: Path):
        """
        Initialize the Android parser.

        Args:
            sdk_path: Path to Android SDK sources (e.g., AOSP frameworks/base)
        """
        self.sdk_path = Path(sdk_path)
        self._validate_sdk_path()

    def _validate_sdk_path(self):
        """Validate the SDK path exists."""
        if not self.sdk_path.exists():
            raise ValueError(f"SDK path does not exist: {self.sdk_path}")

    def parse_all(self, packages: Optional[List[str]] = None) -> Generator[APISpec, None, None]:
        """
        Parse all classes in specified packages.

        Args:
            packages: List of packages to parse. Defaults to CORE_PACKAGES.

        Yields:
            APISpec for each parsed class.
        """
        packages = packages or self.CORE_PACKAGES

        for package in packages:
            logger.info(f"Parsing package: {package}")
            yield from self.parse_package(package)

    def parse_package(self, package: str) -> Generator[APISpec, None, None]:
        """
        Parse all classes in a single package.

        Args:
            package: Package name (e.g., "android.app")

        Yields:
            APISpec for each class in the package.
        """
        package_path = self._get_package_path(package)

        if not package_path.exists():
            logger.warning(f"Package path not found: {package_path}")
            return

        for java_file in package_path.glob("*.java"):
            try:
                spec = self.parse_file(java_file, package)
                if spec:
                    yield spec
            except Exception as e:
                logger.error(f"Error parsing {java_file}: {e}")

    def parse_file(self, file_path: Path, package: str) -> Optional[APISpec]:
        """
        Parse a single Java source file.

        Args:
            file_path: Path to the Java file.
            package: Package name.

        Returns:
            APISpec or None if parsing fails.
        """
        class_name = file_path.stem

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract class-level information
        is_interface = self._is_interface(content)
        is_abstract = self._is_abstract_class(content)
        is_deprecated = self._is_deprecated(content)
        extends = self._extract_extends(content)
        implements = self._extract_implements(content)

        # Extract methods
        methods = self._extract_methods(content)

        return APISpec(
            platform=Platform.ANDROID,
            package=package,
            class_name=class_name,
            full_qualified_name=f"{package}.{class_name}",
            is_interface=is_interface,
            is_abstract=is_abstract,
            is_deprecated=is_deprecated,
            extends=extends,
            implements=implements,
            methods=methods,
            source_file=str(file_path),
        )

    def _get_package_path(self, package: str) -> Path:
        """Convert package name to file path."""
        package_dir = package.replace(".", "/")
        # Try common Android source locations
        possible_paths = [
            self.sdk_path / "core/java" / package_dir,
            self.sdk_path / "java" / package_dir,
            self.sdk_path / package_dir,
        ]
        for path in possible_paths:
            if path.exists():
                return path
        return possible_paths[0]  # Return first path as default

    def _is_interface(self, content: str) -> bool:
        """Check if the class is an interface."""
        return bool(re.search(r"\binterface\s+\w+", content))

    def _is_abstract_class(self, content: str) -> bool:
        """Check if the class is abstract."""
        return bool(re.search(r"\babstract\s+class\s+\w+", content))

    def _is_deprecated(self, content: str) -> bool:
        """Check if the class is deprecated."""
        return "@Deprecated" in content or "@deprecated" in content

    def _extract_extends(self, content: str) -> Optional[str]:
        """Extract the parent class."""
        match = re.search(r"class\s+\w+\s+extends\s+(\w+)", content)
        return match.group(1) if match else None

    def _extract_implements(self, content: str) -> List[str]:
        """Extract implemented interfaces."""
        match = re.search(r"implements\s+([\w\s,]+?)(?:\s*\{|\s*extends)", content)
        if match:
            interfaces = match.group(1).split(",")
            return [i.strip() for i in interfaces if i.strip()]
        return []

    def _extract_methods(self, content: str) -> List[MethodSpec]:
        """
        Extract method specifications from the source.

        This is a simplified parser. For production, use tree-sitter or JavaParser.
        """
        methods = []

        # Regex pattern for method signatures (simplified)
        method_pattern = re.compile(
            r"(@\w+\s+)*"  # Annotations
            r"(public|protected|private)?\s*"  # Visibility
            r"(static\s+)?"  # Static modifier
            r"(final\s+)?"  # Final modifier
            r"(abstract\s+)?"  # Abstract modifier
            r"([\w<>\[\],\s]+)\s+"  # Return type
            r"(\w+)\s*"  # Method name
            r"\(([^)]*)\)"  # Parameters
            r"(?:\s*throws\s+([\w,\s]+))?"  # Throws clause
        )

        for match in method_pattern.finditer(content):
            annotations = match.group(1) or ""
            visibility_str = match.group(2) or "package"
            is_static = bool(match.group(3))
            is_final = bool(match.group(4))
            is_abstract = bool(match.group(5))
            return_type = match.group(6).strip()
            method_name = match.group(7)
            params_str = match.group(8)
            throws_str = match.group(9)

            # Skip constructors (return type same as class name pattern)
            if not return_type or return_type == method_name:
                continue

            # Parse parameters
            parameters = self._parse_parameters(params_str)

            # Parse throws
            throws = []
            if throws_str:
                throws = [t.strip() for t in throws_str.split(",")]

            # Determine visibility
            visibility_map = {
                "public": Visibility.PUBLIC,
                "protected": Visibility.PROTECTED,
                "private": Visibility.PRIVATE,
                "package": Visibility.PACKAGE,
            }
            visibility = visibility_map.get(visibility_str, Visibility.PACKAGE)

            # Build signature
            param_types = ", ".join(p.type for p in parameters)
            signature = f"{return_type} {method_name}({param_types})"

            method = MethodSpec(
                name=method_name,
                signature=signature,
                return_type=return_type,
                parameters=parameters,
                throws=throws,
                visibility=visibility,
                is_static=is_static,
                is_final=is_final,
                is_abstract=is_abstract,
                is_deprecated="@Deprecated" in annotations,
            )
            methods.append(method)

        return methods

    def _parse_parameters(self, params_str: str) -> List[ParameterSpec]:
        """Parse method parameters from string."""
        parameters = []
        if not params_str.strip():
            return parameters

        # Split by comma (simplified - doesn't handle generics with commas)
        params = params_str.split(",")

        for param in params:
            param = param.strip()
            if not param:
                continue

            # Extract annotations
            annotations = []
            while param.startswith("@"):
                ann_match = re.match(r"@\w+\s*", param)
                if ann_match:
                    annotations.append(ann_match.group().strip())
                    param = param[ann_match.end():].strip()
                else:
                    break

            # Check for final modifier
            if param.startswith("final "):
                param = param[6:].strip()

            # Split type and name
            parts = param.rsplit(None, 1)
            if len(parts) == 2:
                param_type, param_name = parts
                nullable = "@Nullable" in " ".join(annotations)
                parameters.append(ParameterSpec(
                    name=param_name,
                    type=param_type.strip(),
                    nullable=nullable,
                    annotations=annotations,
                ))

        return parameters


def parse_android_sdk(sdk_path: str, packages: Optional[List[str]] = None) -> List[APISpec]:
    """
    Convenience function to parse Android SDK.

    Args:
        sdk_path: Path to Android SDK sources.
        packages: Optional list of packages to parse.

    Returns:
        List of APISpec objects.
    """
    parser = AndroidParser(Path(sdk_path))
    return list(parser.parse_all(packages))
