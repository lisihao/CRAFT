"""
Batch Processor

Handles large-scale parallel processing of API adaptations.
"""

from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

from ..core.api_spec import APISpec
from ..core.mapping_rule import MappingRule, MappingType, MappingComplexity
from ..core.config import get_config


logger = logging.getLogger(__name__)


class ProcessingStrategy(Enum):
    """Strategy for processing APIs."""
    RULE_BASED = "rule_based"     # Use rule engine only
    AI_LIGHT = "ai_light"         # Use lightweight AI model
    AI_STANDARD = "ai_standard"   # Use standard AI model
    AI_ADVANCED = "ai_advanced"   # Use most capable AI model


@dataclass
class BatchJob:
    """Represents a batch processing job."""
    job_id: str
    apis: List[APISpec]
    strategy: ProcessingStrategy
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[MappingRule] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.completed_at is not None

    @property
    def success_rate(self) -> float:
        total = len(self.results) + len(self.errors)
        if total == 0:
            return 0.0
        return len(self.results) / total


@dataclass
class BatchResult:
    """Result of batch processing."""
    total_apis: int
    processed_apis: int
    successful_mappings: int
    failed_mappings: int
    duration_seconds: float
    strategy_breakdown: Dict[str, int] = field(default_factory=dict)


class BatchProcessor:
    """
    Processes API adaptations in parallel batches.

    Optimizes throughput by:
    1. Classifying APIs by complexity
    2. Using appropriate processing strategy for each class
    3. Parallel processing with rate limiting
    """

    def __init__(self, ai_client=None):
        """
        Initialize the batch processor.

        Args:
            ai_client: Optional AI client for AI-powered processing.
        """
        self.config = get_config()
        self.ai_client = ai_client

        # Processing queues by strategy
        self.queues: Dict[ProcessingStrategy, List[APISpec]] = {
            ProcessingStrategy.RULE_BASED: [],
            ProcessingStrategy.AI_LIGHT: [],
            ProcessingStrategy.AI_STANDARD: [],
            ProcessingStrategy.AI_ADVANCED: [],
        }

        # Rate limiting
        self.ai_semaphore = asyncio.Semaphore(self.config.pipeline.parallel_workers)

    def classify_apis(self, apis: List[APISpec]) -> Dict[ProcessingStrategy, List[APISpec]]:
        """
        Classify APIs by complexity to determine processing strategy.

        Args:
            apis: List of APIs to classify.

        Returns:
            Dictionary mapping strategy to list of APIs.
        """
        classified = {strategy: [] for strategy in ProcessingStrategy}

        for api in apis:
            strategy = self._determine_strategy(api)
            classified[strategy].append(api)

        return classified

    def _determine_strategy(self, api: APISpec) -> ProcessingStrategy:
        """Determine the best processing strategy for an API."""
        # Check known mappings (rule-based)
        from ..analyzers.semantic_analyzer import SemanticAnalyzer
        if api.full_qualified_name in SemanticAnalyzer.KNOWN_MAPPINGS:
            return ProcessingStrategy.RULE_BASED

        # Check complexity indicators
        complexity_score = self._calculate_complexity(api)

        if complexity_score < 0.3:
            return ProcessingStrategy.RULE_BASED
        elif complexity_score < 0.5:
            return ProcessingStrategy.AI_LIGHT
        elif complexity_score < 0.8:
            return ProcessingStrategy.AI_STANDARD
        else:
            return ProcessingStrategy.AI_ADVANCED

    def _calculate_complexity(self, api: APISpec) -> float:
        """
        Calculate complexity score for an API.

        Returns a value between 0 and 1.
        """
        score = 0.0

        # Number of methods
        method_count = len(api.methods)
        if method_count > 50:
            score += 0.3
        elif method_count > 20:
            score += 0.2
        elif method_count > 10:
            score += 0.1

        # Has callbacks/listeners
        callback_patterns = ["Listener", "Callback", "Handler", "Observer"]
        for method in api.methods:
            for param in method.parameters:
                if any(pattern in param.type for pattern in callback_patterns):
                    score += 0.1
                    break

        # Is abstract or interface
        if api.is_interface or api.is_abstract:
            score += 0.1

        # Has complex inheritance
        if api.extends and api.implements:
            score += 0.1

        # Uses generics
        for method in api.methods:
            if "<" in method.return_type or any("<" in p.type for p in method.parameters):
                score += 0.1
                break

        return min(1.0, score)

    async def process_batch(
        self,
        apis: List[APISpec],
        harmony_apis: List[APISpec],
        mapping_func: Callable
    ) -> BatchResult:
        """
        Process a batch of APIs.

        Args:
            apis: APIs to process.
            harmony_apis: Available HarmonyOS APIs.
            mapping_func: Function to create mapping (api, harmony_apis) -> MappingRule.

        Returns:
            BatchResult with processing statistics.
        """
        start_time = datetime.now()

        # Classify APIs
        classified = self.classify_apis(apis)

        # Process each category
        results = []
        errors = []
        strategy_breakdown = {}

        for strategy, strategy_apis in classified.items():
            if not strategy_apis:
                continue

            strategy_breakdown[strategy.value] = len(strategy_apis)

            if strategy == ProcessingStrategy.RULE_BASED:
                # Process synchronously with rule engine
                for api in strategy_apis:
                    try:
                        mapping = mapping_func(api, harmony_apis)
                        if mapping:
                            results.append(mapping)
                    except Exception as e:
                        errors.append(f"{api.full_qualified_name}: {str(e)}")
            else:
                # Process in parallel with AI (with rate limiting)
                tasks = [
                    self._process_with_ai(api, harmony_apis, mapping_func, strategy)
                    for api in strategy_apis
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, Exception):
                        errors.append(str(result))
                    elif result:
                        results.append(result)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return BatchResult(
            total_apis=len(apis),
            processed_apis=len(results) + len(errors),
            successful_mappings=len(results),
            failed_mappings=len(errors),
            duration_seconds=duration,
            strategy_breakdown=strategy_breakdown,
        )

    async def _process_with_ai(
        self,
        api: APISpec,
        harmony_apis: List[APISpec],
        mapping_func: Callable,
        strategy: ProcessingStrategy
    ) -> Optional[MappingRule]:
        """Process a single API with AI assistance."""
        async with self.ai_semaphore:
            try:
                # Add delay for rate limiting
                await asyncio.sleep(0.1)

                return mapping_func(api, harmony_apis)

            except Exception as e:
                logger.error(f"AI processing failed for {api.full_qualified_name}: {e}")
                raise

    def estimate_processing_time(self, apis: List[APISpec]) -> Dict[str, Any]:
        """
        Estimate processing time for a batch of APIs.

        Returns estimated time and resource usage.
        """
        classified = self.classify_apis(apis)

        # Time estimates per strategy (seconds per API)
        time_per_api = {
            ProcessingStrategy.RULE_BASED: 0.01,
            ProcessingStrategy.AI_LIGHT: 0.5,
            ProcessingStrategy.AI_STANDARD: 2.0,
            ProcessingStrategy.AI_ADVANCED: 5.0,
        }

        # Cost estimates per strategy (relative units)
        cost_per_api = {
            ProcessingStrategy.RULE_BASED: 0,
            ProcessingStrategy.AI_LIGHT: 1,
            ProcessingStrategy.AI_STANDARD: 5,
            ProcessingStrategy.AI_ADVANCED: 20,
        }

        total_time = 0.0
        total_cost = 0.0
        breakdown = {}

        for strategy, strategy_apis in classified.items():
            count = len(strategy_apis)
            time_estimate = count * time_per_api[strategy]
            cost_estimate = count * cost_per_api[strategy]

            # Account for parallelization
            parallel_workers = self.config.pipeline.parallel_workers
            if strategy != ProcessingStrategy.RULE_BASED:
                time_estimate /= min(count, parallel_workers)

            total_time += time_estimate
            total_cost += cost_estimate

            breakdown[strategy.value] = {
                "count": count,
                "estimated_time_seconds": time_estimate,
                "estimated_cost_units": cost_estimate,
            }

        return {
            "total_apis": len(apis),
            "estimated_time_seconds": total_time,
            "estimated_cost_units": total_cost,
            "strategy_breakdown": breakdown,
        }
