//! CRAFT Generator - Code generation using Tera templates
//!
//! This crate provides code generation capabilities:
//! - Adapter code generation (Java, Kotlin, ArkTS)
//! - Test code generation
//! - Template-based generation with Tera

use chrono::Utc;
use craft_core::{ApiSpec, CraftError, MappingRule, MappingType};
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use tera::{Context, Tera};
use tracing::{debug, info};

/// Code generator for adapters
pub struct AdapterGenerator {
    /// Tera template engine
    tera: Option<Tera>,
    /// Generator version
    version: String,
}

impl AdapterGenerator {
    /// Create a new adapter generator
    pub fn new() -> Self {
        Self {
            tera: None,
            version: env!("CARGO_PKG_VERSION").to_string(),
        }
    }

    /// Load templates from a directory
    pub fn with_templates(mut self, templates_dir: &Path) -> Result<Self, CraftError> {
        let glob_pattern = templates_dir.join("**/*").to_string_lossy().to_string();
        self.tera = Some(
            Tera::new(&glob_pattern)
                .map_err(|e| CraftError::Template(e.to_string()))?,
        );
        Ok(self)
    }

    /// Generate adapter code
    pub fn generate(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
        output_format: &str,
    ) -> Result<String, CraftError> {
        let context = self.build_context(mapping_rule, source_api, target_api);

        match output_format {
            "java" => self.generate_java(&context),
            "kotlin" => self.generate_kotlin(&context),
            "arkts" => self.generate_arkts(&context),
            _ => Err(CraftError::Generation(format!(
                "Unsupported output format: {}",
                output_format
            ))),
        }
    }

    /// Build template context
    fn build_context(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> Context {
        let mut context = Context::new();

        // Metadata
        context.insert("generator_version", &self.version);
        context.insert("generated_at", &Utc::now().to_rfc3339());
        context.insert("confidence", &mapping_rule.confidence);

        // Source API
        context.insert("source_package", &source_api.package);
        context.insert("source_class", &source_api.class_name);
        context.insert("source_full_name", &source_api.full_qualified_name);

        // Target API
        context.insert("target_package", &target_api.package);
        context.insert("target_class", &target_api.class_name);
        context.insert("target_full_name", &target_api.full_qualified_name);

        // Mapping info
        context.insert("mapping_type", &format!("{:?}", mapping_rule.mapping_type));
        context.insert("method_mappings", &mapping_rule.method_mappings);
        context.insert("requires_imports", &mapping_rule.requires_imports);

        // Adapter info
        context.insert(
            "adapter_package",
            &format!("craft.adapters.{}", source_api.package),
        );
        context.insert(
            "adapter_class",
            &format!("{}Adapter", source_api.class_name),
        );

        context
    }

    /// Generate Java adapter code
    fn generate_java(&self, context: &Context) -> Result<String, CraftError> {
        // Try template-based generation first
        if let Some(ref tera) = self.tera {
            if tera.get_template_names().any(|n| n == "adapter_java.tera") {
                return tera
                    .render("adapter_java.tera", context)
                    .map_err(|e| CraftError::Template(e.to_string()));
            }
        }

        // Fallback to inline generation
        self.generate_java_inline(context)
    }

    /// Generate Java code without templates
    fn generate_java_inline(&self, context: &Context) -> Result<String, CraftError> {
        let generator_version = context
            .get("generator_version")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let source_full_name = context
            .get("source_full_name")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let target_full_name = context
            .get("target_full_name")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let confidence = context
            .get("confidence")
            .and_then(|v| v.as_f64())
            .unwrap_or(0.0);
        let generated_at = context
            .get("generated_at")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let adapter_package = context
            .get("adapter_package")
            .and_then(|v| v.as_str())
            .unwrap_or("craft.adapters");
        let adapter_class = context
            .get("adapter_class")
            .and_then(|v| v.as_str())
            .unwrap_or("Adapter");
        let source_class = context
            .get("source_class")
            .and_then(|v| v.as_str())
            .unwrap_or("Source");
        let target_class = context
            .get("target_class")
            .and_then(|v| v.as_str())
            .unwrap_or("Target");

        let code = format!(
            r#"/**
 * Auto-generated by CRAFT v{generator_version}
 * Source: {source_full_name}
 * Target: {target_full_name}
 * Confidence: {confidence:.2}
 * Generated: {generated_at}
 *
 * DO NOT EDIT MANUALLY - regenerate using CRAFT pipeline
 */

package {adapter_package};

import {source_full_name};
import {target_full_name};

public class {adapter_class} extends {source_class} {{

    private final {target_class} delegate;

    public {adapter_class}({target_class} delegate) {{
        this.delegate = delegate;
    }}

    // TODO: Implement method adapters
}}
"#
        );

        Ok(code)
    }

    /// Generate Kotlin adapter code
    fn generate_kotlin(&self, context: &Context) -> Result<String, CraftError> {
        let generator_version = context
            .get("generator_version")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let source_full_name = context
            .get("source_full_name")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let target_full_name = context
            .get("target_full_name")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let adapter_package = context
            .get("adapter_package")
            .and_then(|v| v.as_str())
            .unwrap_or("craft.adapters");
        let adapter_class = context
            .get("adapter_class")
            .and_then(|v| v.as_str())
            .unwrap_or("Adapter");
        let source_class = context
            .get("source_class")
            .and_then(|v| v.as_str())
            .unwrap_or("Source");
        let target_class = context
            .get("target_class")
            .and_then(|v| v.as_str())
            .unwrap_or("Target");

        let code = format!(
            r#"/**
 * Auto-generated by CRAFT v{generator_version}
 * Source: {source_full_name}
 * Target: {target_full_name}
 */

package {adapter_package}

import {source_full_name}
import {target_full_name}

class {adapter_class}(
    private val delegate: {target_class}
) : {source_class}() {{

    // TODO: Implement method adapters
}}
"#
        );

        Ok(code)
    }

    /// Generate ArkTS adapter code
    fn generate_arkts(&self, context: &Context) -> Result<String, CraftError> {
        // TODO: Implement ArkTS code generation
        Err(CraftError::Generation(
            "ArkTS generation not yet implemented".to_string(),
        ))
    }

    /// Save generated code to file
    pub fn save(
        &self,
        code: &str,
        output_dir: &Path,
        mapping_rule: &MappingRule,
        format: &str,
    ) -> Result<std::path::PathBuf, CraftError> {
        let class_parts: Vec<&str> = mapping_rule.source.class.split('.').collect();
        let class_name = class_parts.last().unwrap_or(&"Unknown");
        let package_path = class_parts[..class_parts.len() - 1].join("/");

        let ext = match format {
            "java" => "java",
            "kotlin" => "kt",
            "arkts" => "ets",
            _ => "txt",
        };

        let output_path = output_dir
            .join("adapters")
            .join(&package_path)
            .join(format!("{}Adapter.{}", class_name, ext));

        if let Some(parent) = output_path.parent() {
            fs::create_dir_all(parent).map_err(CraftError::Io)?;
        }

        fs::write(&output_path, code).map_err(CraftError::Io)?;

        info!("Saved adapter to: {:?}", output_path);
        Ok(output_path)
    }
}

impl Default for AdapterGenerator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generator_creation() {
        let generator = AdapterGenerator::new();
        assert!(generator.tera.is_none());
    }
}
