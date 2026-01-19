"""
Configuration Management

Centralized configuration for the CRAFT system.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml
import os


@dataclass
class AIConfig:
    """Configuration for AI services."""
    provider: str = "anthropic"
    model_light: str = "claude-3-haiku-20240307"
    model_standard: str = "claude-sonnet-4-20250514"
    model_advanced: str = "claude-opus-4-5-20251101"
    api_key: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.2
    rate_limit_rpm: int = 50  # Requests per minute
    retry_attempts: int = 3

    def __post_init__(self):
        # Try to load API key from environment
        if not self.api_key:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")


@dataclass
class PipelineConfig:
    """Configuration for the automation pipeline."""
    batch_size: int = 100
    parallel_workers: int = 10
    enable_incremental: bool = True
    auto_test: bool = True
    require_review_threshold: float = 0.8  # Confidence below this requires review
    max_retries: int = 3
    timeout_seconds: int = 300


@dataclass
class QualityConfig:
    """Configuration for quality gates."""
    min_confidence: float = 0.7
    min_test_coverage: float = 0.8
    max_complexity: str = "very_high"
    require_human_review: List[str] = field(default_factory=lambda: ["bridge", "shim"])
    auto_approve_confidence: float = 0.95


@dataclass
class PathConfig:
    """Configuration for file paths."""
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    specs_dir: Path = field(default_factory=lambda: Path("specs"))
    templates_dir: Path = field(default_factory=lambda: Path("templates"))
    output_dir: Path = field(default_factory=lambda: Path("output"))
    configs_dir: Path = field(default_factory=lambda: Path("configs"))

    def __post_init__(self):
        # Make paths absolute
        self.specs_dir = self.project_root / self.specs_dir
        self.templates_dir = self.project_root / self.templates_dir
        self.output_dir = self.project_root / self.output_dir
        self.configs_dir = self.project_root / self.configs_dir


@dataclass
class Config:
    """
    Main configuration class for CRAFT.

    Aggregates all sub-configurations and provides loading/saving functionality.
    """
    ai: AIConfig = field(default_factory=AIConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    paths: PathConfig = field(default_factory=PathConfig)

    # Version info
    version: str = "1.0.0"
    environment: str = "development"  # development, staging, production

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "configs" / "craft_config.yaml"

        config = cls()

        if config_path.exists():
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)

            if data:
                if "ai" in data:
                    config.ai = AIConfig(**data["ai"])
                if "pipeline" in data:
                    config.pipeline = PipelineConfig(**data["pipeline"])
                if "quality" in data:
                    config.quality = QualityConfig(**data["quality"])
                if "version" in data:
                    config.version = data["version"]
                if "environment" in data:
                    config.environment = data["environment"]

        return config

    def save(self, config_path: Optional[Path] = None):
        """Save configuration to YAML file."""
        if config_path is None:
            config_path = self.paths.configs_dir / "craft_config.yaml"

        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": self.version,
            "environment": self.environment,
            "ai": {
                "provider": self.ai.provider,
                "model_light": self.ai.model_light,
                "model_standard": self.ai.model_standard,
                "model_advanced": self.ai.model_advanced,
                "max_tokens": self.ai.max_tokens,
                "temperature": self.ai.temperature,
                "rate_limit_rpm": self.ai.rate_limit_rpm,
            },
            "pipeline": {
                "batch_size": self.pipeline.batch_size,
                "parallel_workers": self.pipeline.parallel_workers,
                "enable_incremental": self.pipeline.enable_incremental,
                "auto_test": self.pipeline.auto_test,
                "require_review_threshold": self.pipeline.require_review_threshold,
            },
            "quality": {
                "min_confidence": self.quality.min_confidence,
                "min_test_coverage": self.quality.min_test_coverage,
                "require_human_review": self.quality.require_human_review,
                "auto_approve_confidence": self.quality.auto_approve_confidence,
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if not self.ai.api_key:
            errors.append("AI API key not configured")

        if self.pipeline.batch_size < 1:
            errors.append("Batch size must be at least 1")

        if not 0 <= self.quality.min_confidence <= 1:
            errors.append("min_confidence must be between 0 and 1")

        return errors


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config():
    """Reload the global configuration."""
    global _config
    _config = Config.load()
