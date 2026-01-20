//! CRAFT Core - Core data structures and types
//!
//! This crate provides the fundamental data structures used throughout CRAFT:
//! - `ApiSpec`: API specification for a class/interface
//! - `MethodSpec`: Method specification with parameters and return type
//! - `MappingRule`: Rules for mapping between source and target APIs
//! - `Platform`: Supported platforms (Android, HarmonyOS)

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub mod error;

pub use error::CraftError;

/// Supported platforms for API adaptation
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Platform {
    Android,
    Harmony,
}

impl std::fmt::Display for Platform {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Platform::Android => write!(f, "android"),
            Platform::Harmony => write!(f, "harmony"),
        }
    }
}

/// Parameter specification for a method
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParameterSpec {
    /// Parameter name
    pub name: String,
    /// Parameter type
    #[serde(rename = "type")]
    pub param_type: String,
    /// Whether the parameter is nullable
    #[serde(default)]
    pub nullable: bool,
    /// Default value if any
    pub default_value: Option<String>,
}

/// Method specification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MethodSpec {
    /// Method name
    pub name: String,
    /// Method signature
    pub signature: String,
    /// Return type
    pub return_type: String,
    /// Parameters
    pub parameters: Vec<ParameterSpec>,
    /// Method modifiers (public, static, etc.)
    #[serde(default)]
    pub modifiers: Vec<String>,
    /// Semantic tags for matching
    #[serde(default)]
    pub semantic_tags: Vec<String>,
    /// Documentation comment
    pub doc_comment: Option<String>,
}

/// API specification for a class or interface
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiSpec {
    /// Unique identifier
    pub id: Uuid,
    /// Target platform
    pub platform: Platform,
    /// API version
    pub version: String,
    /// Package name
    pub package: String,
    /// Class or interface name
    pub class_name: String,
    /// Full qualified name
    pub full_qualified_name: String,
    /// Class type (class, interface, abstract class)
    pub class_type: String,
    /// Parent class if any
    pub parent_class: Option<String>,
    /// Implemented interfaces
    #[serde(default)]
    pub interfaces: Vec<String>,
    /// Public methods
    #[serde(default)]
    pub methods: Vec<MethodSpec>,
    /// Semantic tags for the class
    #[serde(default)]
    pub semantic_tags: Vec<String>,
    /// When this spec was created
    pub created_at: DateTime<Utc>,
}

impl ApiSpec {
    /// Create a new API spec
    pub fn new(platform: Platform, package: &str, class_name: &str) -> Self {
        Self {
            id: Uuid::new_v4(),
            platform,
            version: String::new(),
            package: package.to_string(),
            class_name: class_name.to_string(),
            full_qualified_name: format!("{}.{}", package, class_name),
            class_type: "class".to_string(),
            parent_class: None,
            interfaces: Vec::new(),
            methods: Vec::new(),
            semantic_tags: Vec::new(),
            created_at: Utc::now(),
        }
    }

    /// Get public methods
    pub fn public_methods(&self) -> Vec<&MethodSpec> {
        self.methods
            .iter()
            .filter(|m| m.modifiers.contains(&"public".to_string()))
            .collect()
    }

    /// Get a method by name
    pub fn get_method(&self, name: &str) -> Option<&MethodSpec> {
        self.methods.iter().find(|m| m.name == name)
    }
}

/// Type of mapping between APIs
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum MappingType {
    /// Direct 1:1 mapping
    Direct,
    /// Semantic mapping requiring transformation
    Semantic,
    /// Bridge pattern for complex mappings
    Bridge,
    /// Shim layer for missing APIs
    Shim,
}

/// Method-level mapping
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MethodMapping {
    /// Source method name
    pub source_method: String,
    /// Target method name
    pub target_method: String,
    /// Parameter mappings (source_param -> target_param)
    #[serde(default)]
    pub param_mappings: Vec<(String, String)>,
    /// Code to execute before the call
    pub pre_call_code: Option<String>,
    /// Code to execute after the call
    pub post_call_code: Option<String>,
}

/// API reference for mapping
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiReference {
    /// Platform
    pub platform: Platform,
    /// Full qualified class name
    pub class: String,
}

/// Mapping rule between source and target APIs
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingRule {
    /// Unique identifier
    pub id: Uuid,
    /// Source API reference
    pub source: ApiReference,
    /// Target API reference
    pub target: ApiReference,
    /// Mapping type
    pub mapping_type: MappingType,
    /// Confidence score (0.0 - 1.0)
    pub confidence: f64,
    /// Method-level mappings
    #[serde(default)]
    pub method_mappings: Vec<MethodMapping>,
    /// Required imports for the adapter
    #[serde(default)]
    pub requires_imports: Vec<String>,
    /// Bridge code if needed
    pub bridge_code: Option<String>,
    /// When this rule was created
    pub created_at: DateTime<Utc>,
    /// When this rule was last updated
    pub updated_at: DateTime<Utc>,
}

impl MappingRule {
    /// Create a new mapping rule
    pub fn new(source: ApiReference, target: ApiReference, mapping_type: MappingType) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            source,
            target,
            mapping_type,
            confidence: 0.0,
            method_mappings: Vec::new(),
            requires_imports: Vec::new(),
            bridge_code: None,
            created_at: now,
            updated_at: now,
        }
    }
}

/// Configuration for CRAFT
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Project version
    pub version: String,
    /// Paths configuration
    pub paths: PathsConfig,
    /// AI configuration
    pub ai: AiConfig,
}

/// Paths configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PathsConfig {
    /// Output directory
    pub output_dir: String,
    /// Templates directory
    pub templates_dir: String,
    /// Specs directory
    pub specs_dir: String,
}

/// AI configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiConfig {
    /// API provider (anthropic, openai, etc.)
    pub provider: String,
    /// Model to use
    pub model: String,
    /// API key (loaded from environment)
    #[serde(skip)]
    pub api_key: Option<String>,
    /// Maximum tokens per request
    pub max_tokens: u32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_api_spec_creation() {
        let spec = ApiSpec::new(Platform::Android, "android.app", "Activity");
        assert_eq!(spec.platform, Platform::Android);
        assert_eq!(spec.package, "android.app");
        assert_eq!(spec.class_name, "Activity");
        assert_eq!(spec.full_qualified_name, "android.app.Activity");
    }

    #[test]
    fn test_mapping_rule_creation() {
        let source = ApiReference {
            platform: Platform::Android,
            class: "android.app.Activity".to_string(),
        };
        let target = ApiReference {
            platform: Platform::Harmony,
            class: "ohos.app.UIAbility".to_string(),
        };
        let rule = MappingRule::new(source, target, MappingType::Direct);
        assert_eq!(rule.mapping_type, MappingType::Direct);
        assert_eq!(rule.confidence, 0.0);
    }
}
