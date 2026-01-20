//! CRAFT CLI - Command line interface
//!
//! Usage:
//!   craft-cli parse --platform android --sdk-path /path/to/sdk
//!   craft-cli analyze --source android --target harmony
//!   craft-cli generate --package android.app --output ./output
//!   craft-cli pipeline --source-sdk /path/to/android --target-sdk /path/to/harmony

use anyhow::Result;
use clap::{Parser, Subcommand};
use craft_core::Platform;
use craft_parser::parse_sdk;
use craft_pipeline::{PipelineConfig, PipelineOrchestrator};
use std::path::PathBuf;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[derive(Parser)]
#[command(name = "craft-cli")]
#[command(author = "CRAFT Team")]
#[command(version)]
#[command(about = "CRAFT - Cross-platform API adaptation layer generator", long_about = None)]
struct Cli {
    /// Enable verbose output
    #[arg(short, long, global = true)]
    verbose: bool,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Parse SDK and extract API specifications
    Parse {
        /// Platform to parse (android, harmony)
        #[arg(short, long)]
        platform: String,

        /// Path to SDK
        #[arg(short, long)]
        sdk_path: PathBuf,

        /// Output file for parsed specs
        #[arg(short, long)]
        output: Option<PathBuf>,
    },

    /// Analyze APIs and generate mappings
    Analyze {
        /// Source platform
        #[arg(long)]
        source: String,

        /// Target platform
        #[arg(long)]
        target: String,

        /// Source specs directory
        #[arg(long)]
        source_specs: PathBuf,

        /// Target specs directory
        #[arg(long)]
        target_specs: PathBuf,
    },

    /// Generate adapter code
    Generate {
        /// Package to generate adapters for
        #[arg(short, long)]
        package: String,

        /// Output directory
        #[arg(short, long)]
        output: PathBuf,

        /// Output format (java, kotlin, arkts)
        #[arg(short, long, default_value = "java")]
        format: String,
    },

    /// Run full pipeline
    Pipeline {
        /// Source SDK path
        #[arg(long)]
        source_sdk: PathBuf,

        /// Target SDK path
        #[arg(long)]
        target_sdk: PathBuf,

        /// Output directory
        #[arg(short, long, default_value = "output")]
        output: PathBuf,

        /// Maximum concurrent AI requests
        #[arg(long, default_value = "5")]
        max_concurrent: usize,
    },
}

fn parse_platform(s: &str) -> Result<Platform> {
    match s.to_lowercase().as_str() {
        "android" => Ok(Platform::Android),
        "harmony" | "harmonyos" => Ok(Platform::Harmony),
        _ => anyhow::bail!("Unknown platform: {}", s),
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Initialize logging
    let log_level = if cli.verbose { Level::DEBUG } else { Level::INFO };
    let subscriber = FmtSubscriber::builder()
        .with_max_level(log_level)
        .with_target(false)
        .init();

    info!("CRAFT - Cross-platform API Adaptation Layer Generator");

    match cli.command {
        Commands::Parse {
            platform,
            sdk_path,
            output,
        } => {
            let platform = parse_platform(&platform)?;
            info!("Parsing {:?} SDK at {:?}", platform, sdk_path);

            let specs = parse_sdk(platform, &sdk_path)?;
            info!("Parsed {} API specifications", specs.len());

            if let Some(output_path) = output {
                let yaml = serde_yaml::to_string(&specs)?;
                std::fs::write(&output_path, yaml)?;
                info!("Saved specs to {:?}", output_path);
            }
        }

        Commands::Analyze {
            source,
            target,
            source_specs,
            target_specs,
        } => {
            info!("Analyzing {} -> {} mappings", source, target);
            // TODO: Implement analysis command
            info!("Analysis complete");
        }

        Commands::Generate {
            package,
            output,
            format,
        } => {
            info!("Generating {} adapters for {}", format, package);
            // TODO: Implement generation command
            info!("Generation complete");
        }

        Commands::Pipeline {
            source_sdk,
            target_sdk,
            output,
            max_concurrent,
        } => {
            info!("Running full pipeline");

            let config = PipelineConfig {
                max_concurrent_requests: max_concurrent,
                output_dir: output.to_string_lossy().to_string(),
                ..Default::default()
            };

            let orchestrator = PipelineOrchestrator::new(config);
            let stats = orchestrator
                .run(
                    &source_sdk,
                    &target_sdk,
                    Platform::Android,
                    Platform::Harmony,
                )
                .await?;

            info!("Pipeline completed:");
            info!("  Total APIs: {}", stats.total_apis);
            info!("  Processed: {}", stats.processed);
            info!("  Successful: {}", stats.successful);
            info!("  Failed: {}", stats.failed);
            info!("  Skipped: {}", stats.skipped);
        }
    }

    Ok(())
}
