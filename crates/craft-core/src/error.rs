//! Error types for CRAFT

use thiserror::Error;

/// Main error type for CRAFT operations
#[derive(Error, Debug)]
pub enum CraftError {
    /// Parse error when analyzing SDK files
    #[error("Parse error: {0}")]
    Parse(String),

    /// Mapping error when creating or applying rules
    #[error("Mapping error: {0}")]
    Mapping(String),

    /// Generation error when producing code
    #[error("Generation error: {0}")]
    Generation(String),

    /// AI API error
    #[error("AI API error: {0}")]
    AiApi(String),

    /// Configuration error
    #[error("Configuration error: {0}")]
    Config(String),

    /// IO error
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    /// Serialization error
    #[error("Serialization error: {0}")]
    Serialization(String),

    /// Template error
    #[error("Template error: {0}")]
    Template(String),
}

/// Result type alias for CRAFT operations
pub type CraftResult<T> = Result<T, CraftError>;
