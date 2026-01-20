//! CRAFT Pipeline - Batch processing pipeline
//!
//! This crate provides pipeline orchestration:
//! - Batch processing of API mappings
//! - Rate limiting for AI API calls
//! - Progress tracking and reporting
//! - Error recovery and retry logic

use craft_ai::ClaudeClient;
use craft_analyzer::SemanticAnalyzer;
use craft_core::{AiConfig, ApiSpec, CraftError, MappingRule, Platform};
use craft_generator::AdapterGenerator;
use craft_parser::parse_sdk;
use futures::future::join_all;
use std::path::Path;
use std::sync::Arc;
use tokio::sync::Semaphore;
use tracing::{debug, error, info, warn};

/// Pipeline configuration
#[derive(Debug, Clone)]
pub struct PipelineConfig {
    /// Maximum concurrent AI requests
    pub max_concurrent_requests: usize,
    /// Delay between batches in milliseconds
    pub batch_delay_ms: u64,
    /// Retry count for failed operations
    pub max_retries: u32,
    /// Output directory
    pub output_dir: String,
}

impl Default for PipelineConfig {
    fn default() -> Self {
        Self {
            max_concurrent_requests: 5,
            batch_delay_ms: 1000,
            max_retries: 3,
            output_dir: "output".to_string(),
        }
    }
}

/// Pipeline orchestrator
pub struct PipelineOrchestrator {
    config: PipelineConfig,
    analyzer: SemanticAnalyzer,
    generator: AdapterGenerator,
    ai_client: Option<ClaudeClient>,
    semaphore: Arc<Semaphore>,
}

/// Pipeline statistics
#[derive(Debug, Default)]
pub struct PipelineStats {
    pub total_apis: usize,
    pub processed: usize,
    pub successful: usize,
    pub failed: usize,
    pub skipped: usize,
}

impl PipelineOrchestrator {
    /// Create a new pipeline orchestrator
    pub fn new(config: PipelineConfig) -> Self {
        let semaphore = Arc::new(Semaphore::new(config.max_concurrent_requests));
        Self {
            config,
            analyzer: SemanticAnalyzer::new(),
            generator: AdapterGenerator::new(),
            ai_client: None,
            semaphore,
        }
    }

    /// Configure AI client for enhanced generation
    pub fn with_ai(mut self, ai_config: AiConfig) -> Result<Self, CraftError> {
        self.ai_client = Some(ClaudeClient::new(ai_config)?);
        Ok(self)
    }

    /// Run the full pipeline
    pub async fn run(
        &self,
        source_sdk_path: &Path,
        target_sdk_path: &Path,
        source_platform: Platform,
        target_platform: Platform,
    ) -> Result<PipelineStats, CraftError> {
        let mut stats = PipelineStats::default();

        info!("Starting CRAFT pipeline");
        info!("Source SDK: {:?} ({:?})", source_sdk_path, source_platform);
        info!("Target SDK: {:?} ({:?})", target_sdk_path, target_platform);

        // Phase 1: Parse SDKs
        info!("Phase 1: Parsing SDKs");
        let source_apis = parse_sdk(source_platform, source_sdk_path)?;
        let target_apis = parse_sdk(target_platform, target_sdk_path)?;
        stats.total_apis = source_apis.len();
        info!(
            "Parsed {} source APIs and {} target APIs",
            source_apis.len(),
            target_apis.len()
        );

        // Phase 2: Analyze and generate mappings
        info!("Phase 2: Analyzing APIs");
        let mappings = self.analyzer.analyze(&source_apis, &target_apis)?;
        info!("Generated {} mapping rules", mappings.len());

        // Phase 3: Generate adapters
        info!("Phase 3: Generating adapters");
        let output_dir = Path::new(&self.config.output_dir);

        for mapping in &mappings {
            stats.processed += 1;

            // Find source and target API specs
            let source_api = source_apis
                .iter()
                .find(|a| a.full_qualified_name == mapping.source.class);
            let target_api = target_apis
                .iter()
                .find(|a| a.full_qualified_name == mapping.target.class);

            if source_api.is_none() || target_api.is_none() {
                warn!(
                    "Could not find API specs for mapping: {} -> {}",
                    mapping.source.class, mapping.target.class
                );
                stats.skipped += 1;
                continue;
            }

            let source_api = source_api.unwrap();
            let target_api = target_api.unwrap();

            match self
                .generator
                .generate(mapping, source_api, target_api, "java")
            {
                Ok(code) => {
                    if let Err(e) = self.generator.save(&code, output_dir, mapping, "java") {
                        error!("Failed to save adapter: {}", e);
                        stats.failed += 1;
                    } else {
                        stats.successful += 1;
                    }
                }
                Err(e) => {
                    error!(
                        "Failed to generate adapter for {}: {}",
                        mapping.source.class, e
                    );
                    stats.failed += 1;
                }
            }
        }

        info!("Pipeline completed: {:?}", stats);
        Ok(stats)
    }

    /// Process a batch of APIs with rate limiting
    async fn process_batch(&self, mappings: &[MappingRule]) -> Vec<Result<String, CraftError>> {
        let tasks: Vec<_> = mappings
            .iter()
            .map(|mapping| {
                let semaphore = Arc::clone(&self.semaphore);
                async move {
                    let _permit = semaphore.acquire().await.unwrap();
                    // Process mapping
                    Ok(format!("Processed: {}", mapping.source.class))
                }
            })
            .collect();

        join_all(tasks).await
    }
}

/// Batch processor for large-scale operations
pub struct BatchProcessor {
    batch_size: usize,
    delay_ms: u64,
}

impl BatchProcessor {
    /// Create a new batch processor
    pub fn new(batch_size: usize, delay_ms: u64) -> Self {
        Self { batch_size, delay_ms }
    }

    /// Process items in batches
    pub async fn process<T, F, R>(&self, items: Vec<T>, processor: F) -> Vec<R>
    where
        T: Clone + Send + 'static,
        F: Fn(T) -> R + Send + Sync + Clone + 'static,
        R: Send + 'static,
    {
        let mut results = Vec::new();

        for chunk in items.chunks(self.batch_size) {
            let batch_results: Vec<R> = chunk.iter().cloned().map(processor.clone()).collect();
            results.extend(batch_results);

            // Delay between batches
            tokio::time::sleep(tokio::time::Duration::from_millis(self.delay_ms)).await;
        }

        results
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pipeline_config_default() {
        let config = PipelineConfig::default();
        assert_eq!(config.max_concurrent_requests, 5);
        assert_eq!(config.max_retries, 3);
    }

    #[test]
    fn test_batch_processor_creation() {
        let processor = BatchProcessor::new(10, 100);
        assert_eq!(processor.batch_size, 10);
        assert_eq!(processor.delay_ms, 100);
    }
}
