//! CRAFT Parser - SDK parsing using tree-sitter
//!
//! This crate provides high-performance parsing of SDK source files:
//! - Java source file parsing for Android SDK
//! - ArkTS/TypeScript parsing for HarmonyOS SDK
//! - Incremental parsing support
//! - Parallel processing of large codebases

use craft_core::{ApiSpec, CraftError, Platform};
use std::path::Path;
use tracing::info;

pub mod arkts_parser;
pub mod java_parser;

pub use arkts_parser::ArkTsParser;
pub use java_parser::JavaParser;

/// Trait for SDK parsers
pub trait SdkParser: Send + Sync {
    /// Parse a single source file
    fn parse_file(&self, path: &Path) -> Result<Option<ApiSpec>, CraftError>;

    /// Parse all files in a directory
    fn parse_directory(&self, path: &Path) -> Result<Vec<ApiSpec>, CraftError>;

    /// Get the platform this parser handles
    fn platform(&self) -> Platform;
}

/// Parse SDK at the given path
pub fn parse_sdk(platform: Platform, sdk_path: &Path) -> Result<Vec<ApiSpec>, CraftError> {
    info!("Parsing {:?} SDK at {:?}", platform, sdk_path);

    let parser: Box<dyn SdkParser> = match platform {
        Platform::Android => Box::new(JavaParser::new()),
        Platform::Harmony => Box::new(ArkTsParser::new()),
    };

    parser.parse_directory(sdk_path)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parser_creation() {
        let parser = JavaParser::new();
        assert_eq!(parser.platform(), Platform::Android);
    }
}
