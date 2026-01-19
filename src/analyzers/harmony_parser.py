"""
HarmonyOS SDK Parser

Parses HarmonyOS SDK source code to extract API specifications.
"""

from pathlib import Path
from typing import List, Optional, Generator
import logging

from ..core.api_spec import APISpec, Platform


logger = logging.getLogger(__name__)


class HarmonyParser:
    """
    Parser for HarmonyOS SDK source code.

    Extracts API specifications from ArkTS/eTS source files in the HarmonyOS SDK.
    """

    # Core HarmonyOS packages
    CORE_PACKAGES = [
        "ohos.app",
        "ohos.ability",
        "ohos.data",
        "ohos.window",
        "ohos.display",
        "ohos.media",
        "ohos.net",
        "ohos.wifi",
        "ohos.bluetooth",
        "ohos.telephony",
        "ohos.security",
        "ohos.account",
        "ohos.notification",
        "ohos.backgroundTaskManager",
        "ohos.bundle",
        "ohos.contact",
        "ohos.file",
        "ohos.geolocation",
        "ohos.sensor",
        "ohos.vibrator",
    ]

    def __init__(self, sdk_path: Path):
        """
        Initialize the HarmonyOS parser.

        Args:
            sdk_path: Path to HarmonyOS SDK sources (OpenHarmony)
        """
        self.sdk_path = Path(sdk_path)

    def parse_all(self, packages: Optional[List[str]] = None) -> Generator[APISpec, None, None]:
        """
        Parse all classes in specified packages.

        Args:
            packages: List of packages to parse. Defaults to CORE_PACKAGES.

        Yields:
            APISpec for each parsed class/module.
        """
        packages = packages or self.CORE_PACKAGES

        for package in packages:
            logger.info(f"Parsing HarmonyOS package: {package}")
            yield from self.parse_package(package)

    def parse_package(self, package: str) -> Generator[APISpec, None, None]:
        """
        Parse all modules in a single package.

        Args:
            package: Package name (e.g., "ohos.app")

        Yields:
            APISpec for each module in the package.
        """
        # HarmonyOS uses different file structure (d.ts, ets files)
        package_path = self._get_package_path(package)

        if not package_path or not package_path.exists():
            logger.warning(f"HarmonyOS package path not found for: {package}")
            return

        # Parse TypeScript declaration files
        for dts_file in package_path.glob("**/*.d.ts"):
            try:
                spec = self.parse_dts_file(dts_file, package)
                if spec:
                    yield spec
            except Exception as e:
                logger.error(f"Error parsing {dts_file}: {e}")

    def parse_dts_file(self, file_path: Path, package: str) -> Optional[APISpec]:
        """
        Parse a TypeScript declaration file (.d.ts).

        Args:
            file_path: Path to the .d.ts file.
            package: Package name.

        Returns:
            APISpec or None if parsing fails.
        """
        module_name = file_path.stem.replace(".d", "")

        # TODO: Implement full TypeScript/ArkTS parser
        # For now, return a placeholder spec

        return APISpec(
            platform=Platform.HARMONY,
            package=package,
            class_name=module_name,
            full_qualified_name=f"{package}.{module_name}",
            source_file=str(file_path),
        )

    def _get_package_path(self, package: str) -> Optional[Path]:
        """Convert HarmonyOS package name to file path."""
        # HarmonyOS SDK has different structure than Android
        # Common locations: api/, interface/, @ohos/

        possible_paths = [
            self.sdk_path / "api" / package.replace(".", "/"),
            self.sdk_path / "interface" / package.replace(".", "/"),
            self.sdk_path / "@ohos" / package.split(".")[-1],
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None


def parse_harmony_sdk(sdk_path: str, packages: Optional[List[str]] = None) -> List[APISpec]:
    """
    Convenience function to parse HarmonyOS SDK.

    Args:
        sdk_path: Path to HarmonyOS SDK sources.
        packages: Optional list of packages to parse.

    Returns:
        List of APISpec objects.
    """
    parser = HarmonyParser(Path(sdk_path))
    return list(parser.parse_all(packages))
