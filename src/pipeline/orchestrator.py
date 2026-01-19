"""
Pipeline Orchestrator

Coordinates the end-to-end API adaptation pipeline.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio

from ..core.api_spec import APISpec
from ..core.mapping_rule import MappingRule, MappingStatus
from ..core.config import get_config
from ..analyzers import AndroidParser, HarmonyParser, SemanticAnalyzer
from ..generators import AdapterGenerator, TestGenerator


logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline execution stages."""
    INIT = "init"
    PARSE_ANDROID = "parse_android"
    PARSE_HARMONY = "parse_harmony"
    ANALYZE_MAPPINGS = "analyze_mappings"
    GENERATE_CODE = "generate_code"
    GENERATE_TESTS = "generate_tests"
    VALIDATE = "validate"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""
    run_id: str
    stage: PipelineStage
    success: bool
    android_apis_parsed: int = 0
    harmony_apis_parsed: int = 0
    mappings_created: int = 0
    adapters_generated: int = 0
    tests_generated: int = 0
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "stage": self.stage.value,
            "success": self.success,
            "android_apis_parsed": self.android_apis_parsed,
            "harmony_apis_parsed": self.harmony_apis_parsed,
            "mappings_created": self.mappings_created,
            "adapters_generated": self.adapters_generated,
            "tests_generated": self.tests_generated,
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }


class PipelineOrchestrator:
    """
    Orchestrates the complete API adaptation pipeline.

    Pipeline stages:
    1. Parse Android SDK
    2. Parse HarmonyOS SDK
    3. Analyze and create mappings
    4. Generate adapter code
    5. Generate tests
    6. Validate output
    """

    def __init__(
        self,
        android_sdk_path: Path,
        harmony_sdk_path: Path,
        ai_client=None
    ):
        """
        Initialize the pipeline orchestrator.

        Args:
            android_sdk_path: Path to Android SDK sources.
            harmony_sdk_path: Path to HarmonyOS SDK sources.
            ai_client: Optional AI client for semantic analysis.
        """
        self.config = get_config()
        self.android_sdk_path = Path(android_sdk_path)
        self.harmony_sdk_path = Path(harmony_sdk_path)

        # Initialize components
        self.android_parser = AndroidParser(self.android_sdk_path)
        self.harmony_parser = HarmonyParser(self.harmony_sdk_path)
        self.semantic_analyzer = SemanticAnalyzer(ai_client)
        self.adapter_generator = AdapterGenerator()
        self.test_generator = TestGenerator()

        # State
        self.android_apis: List[APISpec] = []
        self.harmony_apis: List[APISpec] = []
        self.mappings: List[MappingRule] = []

    async def run(
        self,
        packages: Optional[List[str]] = None,
        incremental: bool = False
    ) -> PipelineResult:
        """
        Execute the full pipeline.

        Args:
            packages: Optional list of packages to process.
            incremental: If True, only process changed APIs.

        Returns:
            PipelineResult with execution details.
        """
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = PipelineResult(run_id=run_id, stage=PipelineStage.INIT, success=False)

        try:
            # Stage 1: Parse Android SDK
            logger.info("Stage 1: Parsing Android SDK...")
            result.stage = PipelineStage.PARSE_ANDROID
            self.android_apis = list(self.android_parser.parse_all(packages))
            result.android_apis_parsed = len(self.android_apis)
            logger.info(f"Parsed {len(self.android_apis)} Android APIs")

            # Stage 2: Parse HarmonyOS SDK
            logger.info("Stage 2: Parsing HarmonyOS SDK...")
            result.stage = PipelineStage.PARSE_HARMONY
            self.harmony_apis = list(self.harmony_parser.parse_all())
            result.harmony_apis_parsed = len(self.harmony_apis)
            logger.info(f"Parsed {len(self.harmony_apis)} HarmonyOS APIs")

            # Stage 3: Analyze and create mappings
            logger.info("Stage 3: Analyzing mappings...")
            result.stage = PipelineStage.ANALYZE_MAPPINGS
            self.mappings = await self._analyze_all_mappings()
            result.mappings_created = len(self.mappings)
            logger.info(f"Created {len(self.mappings)} mappings")

            # Stage 4: Generate adapter code
            logger.info("Stage 4: Generating adapters...")
            result.stage = PipelineStage.GENERATE_CODE
            adapters_count = await self._generate_all_adapters()
            result.adapters_generated = adapters_count
            logger.info(f"Generated {adapters_count} adapters")

            # Stage 5: Generate tests
            logger.info("Stage 5: Generating tests...")
            result.stage = PipelineStage.GENERATE_TESTS
            tests_count = await self._generate_all_tests()
            result.tests_generated = tests_count
            logger.info(f"Generated {tests_count} test files")

            # Stage 6: Validate
            logger.info("Stage 6: Validating output...")
            result.stage = PipelineStage.VALIDATE
            validation_errors = self._validate_output()
            if validation_errors:
                result.errors.extend(validation_errors)

            # Complete
            result.stage = PipelineStage.COMPLETE
            result.success = len(result.errors) == 0

        except Exception as e:
            logger.error(f"Pipeline failed at stage {result.stage}: {e}")
            result.stage = PipelineStage.FAILED
            result.errors.append(str(e))
            result.success = False

        finally:
            result.completed_at = datetime.now()
            result.duration_seconds = (
                result.completed_at - result.started_at
            ).total_seconds()

        return result

    async def _analyze_all_mappings(self) -> List[MappingRule]:
        """Analyze and create mappings for all Android APIs."""
        mappings = []

        for android_api in self.android_apis:
            try:
                mapping = self.semantic_analyzer.find_mapping(
                    android_api,
                    self.harmony_apis
                )
                if mapping:
                    mappings.append(mapping)
            except Exception as e:
                logger.warning(f"Failed to map {android_api.full_qualified_name}: {e}")

        return mappings

    async def _generate_all_adapters(self) -> int:
        """Generate adapter code for all mappings."""
        count = 0

        for mapping in self.mappings:
            if not mapping.is_ready_for_generation:
                continue

            try:
                # Find the API specs
                android_api = self._find_android_api(mapping.android_class)
                harmony_api = self._find_harmony_api(mapping.harmony_class)

                if android_api and harmony_api:
                    code = self.adapter_generator.generate(
                        mapping, android_api, harmony_api
                    )
                    self.adapter_generator.save(code, mapping)
                    mapping.update_status(MappingStatus.GENERATED)
                    count += 1

            except Exception as e:
                logger.error(f"Failed to generate adapter for {mapping.id}: {e}")

        return count

    async def _generate_all_tests(self) -> int:
        """Generate tests for all generated adapters."""
        count = 0

        for mapping in self.mappings:
            if mapping.status != MappingStatus.GENERATED:
                continue

            try:
                android_api = self._find_android_api(mapping.android_class)
                if android_api:
                    # Generate unit tests
                    test_code = self.test_generator.generate_unit_tests(
                        mapping, android_api, ""
                    )
                    self.test_generator.save(test_code, mapping, "unit")
                    count += 1

            except Exception as e:
                logger.error(f"Failed to generate tests for {mapping.id}: {e}")

        return count

    def _validate_output(self) -> List[str]:
        """Validate generated output."""
        errors = []

        output_dir = self.config.paths.output_dir

        # Check adapters exist
        adapters_dir = output_dir / "adapters"
        if not adapters_dir.exists() or not any(adapters_dir.iterdir()):
            errors.append("No adapters were generated")

        # Check tests exist
        tests_dir = output_dir / "tests"
        if not tests_dir.exists() or not any(tests_dir.iterdir()):
            errors.append("No tests were generated")

        return errors

    def _find_android_api(self, full_name: str) -> Optional[APISpec]:
        """Find an Android API by full qualified name."""
        for api in self.android_apis:
            if api.full_qualified_name == full_name:
                return api
        return None

    def _find_harmony_api(self, full_name: str) -> Optional[APISpec]:
        """Find a HarmonyOS API by full qualified name."""
        for api in self.harmony_apis:
            if api.full_qualified_name == full_name:
                return api
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get current pipeline statistics."""
        return {
            "android_apis": len(self.android_apis),
            "harmony_apis": len(self.harmony_apis),
            "total_mappings": len(self.mappings),
            "mappings_by_status": self._count_mappings_by_status(),
            "mappings_by_type": self._count_mappings_by_type(),
            "average_confidence": self._calculate_average_confidence(),
        }

    def _count_mappings_by_status(self) -> Dict[str, int]:
        """Count mappings by status."""
        counts = {}
        for mapping in self.mappings:
            status = mapping.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts

    def _count_mappings_by_type(self) -> Dict[str, int]:
        """Count mappings by type."""
        counts = {}
        for mapping in self.mappings:
            mapping_type = mapping.mapping_type.value
            counts[mapping_type] = counts.get(mapping_type, 0) + 1
        return counts

    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence across all mappings."""
        if not self.mappings:
            return 0.0
        total = sum(m.confidence for m in self.mappings)
        return total / len(self.mappings)
