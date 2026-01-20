//! CRAFT Generator - Code generation using Tera templates
//!
//! This crate provides code generation capabilities:
//! - Adapter code generation (Java, Kotlin, ArkTS)
//! - Test code generation
//! - Template-based generation with Tera
//! - Method implementation generation with proper delegation

use chrono::Utc;
use craft_core::{ApiSpec, CraftError, MappingRule, MappingType, MethodMapping, MethodSpec, ParameterSpec};
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use tera::{Context, Tera};
use tracing::{debug, info};

/// Lifecycle mapping between Android Activity and HarmonyOS UIAbility
pub struct LifecycleMapping {
    /// Android lifecycle method to HarmonyOS mapping
    mappings: HashMap<String, LifecycleTarget>,
}

/// Target lifecycle method with optional transformation code
#[derive(Clone)]
pub struct LifecycleTarget {
    /// Target method name
    pub method: String,
    /// Pre-call transformation code
    pub pre_call: Option<String>,
    /// Post-call transformation code
    pub post_call: Option<String>,
    /// Parameter transformation
    pub param_transform: Option<String>,
}

impl LifecycleMapping {
    /// Create default Activity -> UIAbility lifecycle mapping
    pub fn activity_to_uiability() -> Self {
        let mut mappings = HashMap::new();

        // onCreate -> onCreate (with Want parameter transformation)
        mappings.insert("onCreate".to_string(), LifecycleTarget {
            method: "onCreate".to_string(),
            pre_call: Some("// Bundle to Want transformation".to_string()),
            post_call: None,
            param_transform: Some("want".to_string()),
        });

        // onStart -> onForeground
        mappings.insert("onStart".to_string(), LifecycleTarget {
            method: "onForeground".to_string(),
            pre_call: None,
            post_call: None,
            param_transform: None,
        });

        // onResume -> onForeground (combined with onStart)
        mappings.insert("onResume".to_string(), LifecycleTarget {
            method: "onForeground".to_string(),
            pre_call: Some("// Note: onResume maps to onForeground in HarmonyOS".to_string()),
            post_call: None,
            param_transform: None,
        });

        // onPause -> onBackground
        mappings.insert("onPause".to_string(), LifecycleTarget {
            method: "onBackground".to_string(),
            pre_call: None,
            post_call: None,
            param_transform: None,
        });

        // onStop -> onBackground (combined with onPause)
        mappings.insert("onStop".to_string(), LifecycleTarget {
            method: "onBackground".to_string(),
            pre_call: Some("// Note: onStop maps to onBackground in HarmonyOS".to_string()),
            post_call: None,
            param_transform: None,
        });

        // onDestroy -> onDestroy
        mappings.insert("onDestroy".to_string(), LifecycleTarget {
            method: "onDestroy".to_string(),
            pre_call: None,
            post_call: None,
            param_transform: None,
        });

        // onSaveInstanceState -> no direct equivalent (use AppStorage)
        mappings.insert("onSaveInstanceState".to_string(), LifecycleTarget {
            method: "saveStateToAppStorage".to_string(),
            pre_call: Some("// Use AppStorage for state persistence in HarmonyOS".to_string()),
            post_call: None,
            param_transform: None,
        });

        // onRestoreInstanceState -> no direct equivalent (use AppStorage)
        mappings.insert("onRestoreInstanceState".to_string(), LifecycleTarget {
            method: "restoreStateFromAppStorage".to_string(),
            pre_call: Some("// Use AppStorage for state restoration in HarmonyOS".to_string()),
            post_call: None,
            param_transform: None,
        });

        // Fragment lifecycle
        mappings.insert("onAttach".to_string(), LifecycleTarget {
            method: "aboutToAppear".to_string(),
            pre_call: None,
            post_call: None,
            param_transform: None,
        });

        mappings.insert("onDetach".to_string(), LifecycleTarget {
            method: "aboutToDisappear".to_string(),
            pre_call: None,
            post_call: None,
            param_transform: None,
        });

        mappings.insert("onCreateView".to_string(), LifecycleTarget {
            method: "build".to_string(),
            pre_call: Some("// onCreateView maps to build() in ArkUI".to_string()),
            post_call: None,
            param_transform: None,
        });

        Self { mappings }
    }

    /// Get lifecycle target for a source method
    pub fn get_target(&self, source_method: &str) -> Option<&LifecycleTarget> {
        self.mappings.get(source_method)
    }

    /// Check if a method is a lifecycle method
    pub fn is_lifecycle_method(&self, method_name: &str) -> bool {
        self.mappings.contains_key(method_name)
    }
}

/// Code generator for adapters
pub struct AdapterGenerator {
    /// Tera template engine
    tera: Option<Tera>,
    /// Generator version
    version: String,
    /// Lifecycle mapping
    lifecycle_mapping: LifecycleMapping,
}

impl AdapterGenerator {
    /// Create a new adapter generator
    pub fn new() -> Self {
        Self {
            tera: None,
            version: env!("CARGO_PKG_VERSION").to_string(),
            lifecycle_mapping: LifecycleMapping::activity_to_uiability(),
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

    /// Set custom lifecycle mapping
    pub fn with_lifecycle_mapping(mut self, mapping: LifecycleMapping) -> Self {
        self.lifecycle_mapping = mapping;
        self
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
            "java" => self.generate_java(mapping_rule, source_api, target_api),
            "kotlin" => self.generate_kotlin(mapping_rule, source_api, target_api),
            "arkts" => self.generate_arkts(mapping_rule, source_api, target_api),
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

    /// Generate Java adapter code with full method implementations
    fn generate_java(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> Result<String, CraftError> {
        let adapter_package = format!("craft.adapters.{}", source_api.package);
        let adapter_class = format!("{}Adapter", source_api.class_name);

        // Collect all required imports
        let mut imports = vec![
            source_api.full_qualified_name.clone(),
            target_api.full_qualified_name.clone(),
        ];
        imports.extend(mapping_rule.requires_imports.clone());

        // Generate method implementations
        let method_impls = self.generate_java_method_implementations(
            mapping_rule,
            source_api,
            target_api,
        );

        let imports_str = imports
            .iter()
            .map(|i| format!("import {};", i))
            .collect::<Vec<_>>()
            .join("\n");

        let code = format!(
            r#"/**
 * Auto-generated by CRAFT v{version}
 * Source: {source_full_name}
 * Target: {target_full_name}
 * Confidence: {confidence:.2}
 * Generated: {generated_at}
 *
 * This adapter provides compatibility layer between Android and HarmonyOS APIs.
 * DO NOT EDIT MANUALLY - regenerate using CRAFT pipeline
 */

package {adapter_package};

{imports}

public class {adapter_class} extends {source_class} {{

    private final {target_class} delegate;

    /**
     * Create adapter wrapping a HarmonyOS {target_class} instance.
     * @param delegate The HarmonyOS implementation to delegate to
     */
    public {adapter_class}({target_class} delegate) {{
        this.delegate = delegate;
    }}

    /**
     * Get the underlying HarmonyOS delegate.
     * @return The wrapped {target_class} instance
     */
    public {target_class} getDelegate() {{
        return this.delegate;
    }}

{method_impls}
}}
"#,
            version = self.version,
            source_full_name = source_api.full_qualified_name,
            target_full_name = target_api.full_qualified_name,
            confidence = mapping_rule.confidence,
            generated_at = Utc::now().to_rfc3339(),
            adapter_package = adapter_package,
            imports = imports_str,
            adapter_class = adapter_class,
            source_class = source_api.class_name,
            target_class = target_api.class_name,
            method_impls = method_impls,
        );

        Ok(code)
    }

    /// Generate Java method implementations
    fn generate_java_method_implementations(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> String {
        let mut implementations = Vec::new();

        for source_method in &source_api.methods {
            // Skip private and protected methods (only adapt public API)
            if !source_method.modifiers.contains(&"public".to_string()) {
                continue;
            }

            let impl_code = self.generate_java_method(
                source_method,
                mapping_rule,
                target_api,
            );
            implementations.push(impl_code);
        }

        implementations.join("\n\n")
    }

    /// Generate a single Java method implementation
    fn generate_java_method(
        &self,
        source_method: &MethodSpec,
        mapping_rule: &MappingRule,
        target_api: &ApiSpec,
    ) -> String {
        // Check if this is a lifecycle method
        if let Some(lifecycle_target) = self.lifecycle_mapping.get_target(&source_method.name) {
            return self.generate_java_lifecycle_method(source_method, lifecycle_target);
        }

        // Find matching method mapping
        let method_mapping = mapping_rule.method_mappings
            .iter()
            .find(|m| m.source_method == source_method.name);

        // Find matching target method
        let target_method = target_api.get_method(
            method_mapping.map(|m| m.target_method.as_str()).unwrap_or(&source_method.name)
        );

        self.generate_java_delegation_method(source_method, target_method, method_mapping)
    }

    /// Generate Java lifecycle method with HarmonyOS mapping
    fn generate_java_lifecycle_method(
        &self,
        source_method: &MethodSpec,
        lifecycle_target: &LifecycleTarget,
    ) -> String {
        let params_str = source_method.parameters
            .iter()
            .map(|p| format!("{} {}", p.param_type, p.name))
            .collect::<Vec<_>>()
            .join(", ");

        let modifiers = if source_method.modifiers.is_empty() {
            "public".to_string()
        } else {
            source_method.modifiers.join(" ")
        };

        let pre_call = lifecycle_target.pre_call.as_ref()
            .map(|c| format!("        {}\n", c))
            .unwrap_or_default();

        let post_call = lifecycle_target.post_call.as_ref()
            .map(|c| format!("\n        {}", c))
            .unwrap_or_default();

        // Generate parameter passing
        let delegate_params = if let Some(ref transform) = lifecycle_target.param_transform {
            transform.clone()
        } else {
            source_method.parameters
                .iter()
                .map(|p| p.name.clone())
                .collect::<Vec<_>>()
                .join(", ")
        };

        // Handle return type
        let return_stmt = if source_method.return_type == "void" {
            format!("delegate.{}({});", lifecycle_target.method, delegate_params)
        } else {
            format!("return delegate.{}({});", lifecycle_target.method, delegate_params)
        };

        format!(
            r#"    /**
     * Lifecycle adapter: {source_name} -> {target_name}
     * Maps Android {source_name} to HarmonyOS {target_name}
     */
    @Override
    {modifiers} {return_type} {source_name}({params}) {{
{pre_call}        {return_stmt}{post_call}
    }}"#,
            source_name = source_method.name,
            target_name = lifecycle_target.method,
            modifiers = modifiers,
            return_type = source_method.return_type,
            params = params_str,
            pre_call = pre_call,
            return_stmt = return_stmt,
            post_call = post_call,
        )
    }

    /// Generate Java delegation method
    fn generate_java_delegation_method(
        &self,
        source_method: &MethodSpec,
        target_method: Option<&MethodSpec>,
        method_mapping: Option<&MethodMapping>,
    ) -> String {
        let params_str = source_method.parameters
            .iter()
            .map(|p| format!("{} {}", p.param_type, p.name))
            .collect::<Vec<_>>()
            .join(", ");

        let modifiers = if source_method.modifiers.is_empty() {
            "public".to_string()
        } else {
            source_method.modifiers.join(" ")
        };

        let target_name = method_mapping
            .map(|m| m.target_method.as_str())
            .unwrap_or(&source_method.name);

        // Generate parameter mapping
        let delegate_params = if let Some(mapping) = method_mapping {
            if !mapping.param_mappings.is_empty() {
                mapping.param_mappings
                    .iter()
                    .map(|(_, target)| target.clone())
                    .collect::<Vec<_>>()
                    .join(", ")
            } else {
                source_method.parameters
                    .iter()
                    .map(|p| p.name.clone())
                    .collect::<Vec<_>>()
                    .join(", ")
            }
        } else {
            source_method.parameters
                .iter()
                .map(|p| p.name.clone())
                .collect::<Vec<_>>()
                .join(", ")
        };

        // Pre/post call code
        let pre_call = method_mapping
            .and_then(|m| m.pre_call_code.as_ref())
            .map(|c| format!("        {}\n", c))
            .unwrap_or_default();

        let post_call = method_mapping
            .and_then(|m| m.post_call_code.as_ref())
            .map(|c| format!("\n        {}", c))
            .unwrap_or_default();

        // Generate return statement based on return type
        let (return_stmt, needs_conversion) = if let Some(target) = target_method {
            if source_method.return_type == target.return_type {
                // Direct delegation
                if source_method.return_type == "void" {
                    (format!("delegate.{}({});", target_name, delegate_params), false)
                } else {
                    (format!("return delegate.{}({});", target_name, delegate_params), false)
                }
            } else {
                // Type conversion needed
                let conversion = self.generate_type_conversion(
                    &source_method.return_type,
                    &target.return_type,
                    &format!("delegate.{}({})", target_name, delegate_params),
                );
                (format!("return {};", conversion), true)
            }
        } else {
            // No matching target method - generate stub
            if source_method.return_type == "void" {
                ("// No direct mapping available - implement manually".to_string(), false)
            } else {
                (format!(
                    "// No direct mapping available\n        throw new UnsupportedOperationException(\"Method {} has no direct HarmonyOS equivalent\");",
                    source_method.name
                ), false)
            }
        };

        let doc_comment = if needs_conversion {
            format!(
                r#"    /**
     * Adapted method with type conversion: {source_name} -> {target_name}
     * Source return type: {source_ret}
     * Target return type: {target_ret}
     */"#,
                source_name = source_method.name,
                target_name = target_name,
                source_ret = source_method.return_type,
                target_ret = target_method.map(|m| m.return_type.as_str()).unwrap_or("N/A"),
            )
        } else {
            format!(
                r#"    /**
     * Delegated method: {source_name} -> {target_name}
     */"#,
                source_name = source_method.name,
                target_name = target_name,
            )
        };

        format!(
            r#"{doc}
    @Override
    {modifiers} {return_type} {method_name}({params}) {{
{pre_call}        {return_stmt}{post_call}
    }}"#,
            doc = doc_comment,
            modifiers = modifiers,
            return_type = source_method.return_type,
            method_name = source_method.name,
            params = params_str,
            pre_call = pre_call,
            return_stmt = return_stmt,
            post_call = post_call,
        )
    }

    /// Generate type conversion code
    fn generate_type_conversion(&self, source_type: &str, target_type: &str, expr: &str) -> String {
        // Common type conversions
        match (source_type, target_type) {
            ("int", "number") | ("Integer", "number") => format!("(int) {}", expr),
            ("number", "int") | ("number", "Integer") => format!("{}.intValue()", expr),
            ("String", "string") | ("string", "String") => expr.to_string(),
            ("boolean", "Boolean") | ("Boolean", "boolean") => expr.to_string(),
            ("List", "Array") => format!("{}.toArray()", expr),
            ("Array", "List") => format!("Arrays.asList({})", expr),
            _ => {
                // Generic cast
                format!("({}) {}", source_type, expr)
            }
        }
    }

    /// Generate Kotlin adapter code
    fn generate_kotlin(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> Result<String, CraftError> {
        let adapter_package = format!("craft.adapters.{}", source_api.package);
        let adapter_class = format!("{}Adapter", source_api.class_name);

        // Collect imports
        let mut imports = vec![
            source_api.full_qualified_name.clone(),
            target_api.full_qualified_name.clone(),
        ];
        imports.extend(mapping_rule.requires_imports.clone());

        let imports_str = imports
            .iter()
            .map(|i| format!("import {}", i))
            .collect::<Vec<_>>()
            .join("\n");

        // Generate method implementations
        let method_impls = self.generate_kotlin_method_implementations(
            mapping_rule,
            source_api,
            target_api,
        );

        let code = format!(
            r#"/**
 * Auto-generated by CRAFT v{version}
 * Source: {source_full_name}
 * Target: {target_full_name}
 * Confidence: {confidence:.2}
 * Generated: {generated_at}
 */

package {adapter_package}

{imports}

class {adapter_class}(
    private val delegate: {target_class}
) : {source_class}() {{

    /** Get the underlying HarmonyOS delegate. */
    fun getDelegate(): {target_class} = delegate

{method_impls}
}}
"#,
            version = self.version,
            source_full_name = source_api.full_qualified_name,
            target_full_name = target_api.full_qualified_name,
            confidence = mapping_rule.confidence,
            generated_at = Utc::now().to_rfc3339(),
            adapter_package = adapter_package,
            imports = imports_str,
            adapter_class = adapter_class,
            source_class = source_api.class_name,
            target_class = target_api.class_name,
            method_impls = method_impls,
        );

        Ok(code)
    }

    /// Generate Kotlin method implementations
    fn generate_kotlin_method_implementations(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> String {
        let mut implementations = Vec::new();

        for source_method in &source_api.methods {
            if !source_method.modifiers.contains(&"public".to_string()) {
                continue;
            }

            let target_method_name = mapping_rule.method_mappings
                .iter()
                .find(|m| m.source_method == source_method.name)
                .map(|m| m.target_method.as_str())
                .unwrap_or(&source_method.name);

            // Check lifecycle mapping
            let target_name = if let Some(lifecycle_target) = self.lifecycle_mapping.get_target(&source_method.name) {
                lifecycle_target.method.clone()
            } else {
                target_method_name.to_string()
            };

            let params_str = source_method.parameters
                .iter()
                .map(|p| format!("{}: {}", p.name, self.java_to_kotlin_type(&p.param_type)))
                .collect::<Vec<_>>()
                .join(", ");

            let delegate_params = source_method.parameters
                .iter()
                .map(|p| p.name.clone())
                .collect::<Vec<_>>()
                .join(", ");

            let return_type = self.java_to_kotlin_type(&source_method.return_type);

            let impl_code = if return_type == "Unit" {
                format!(
                    r#"    override fun {}({}) {{
        delegate.{}({})
    }}"#,
                    source_method.name,
                    params_str,
                    target_name,
                    delegate_params,
                )
            } else {
                format!(
                    r#"    override fun {}({}): {} {{
        return delegate.{}({})
    }}"#,
                    source_method.name,
                    params_str,
                    return_type,
                    target_name,
                    delegate_params,
                )
            };

            implementations.push(impl_code);
        }

        implementations.join("\n\n")
    }

    /// Convert Java type to Kotlin type
    fn java_to_kotlin_type(&self, java_type: &str) -> String {
        match java_type {
            "void" => "Unit".to_string(),
            "int" => "Int".to_string(),
            "long" => "Long".to_string(),
            "float" => "Float".to_string(),
            "double" => "Double".to_string(),
            "boolean" => "Boolean".to_string(),
            "byte" => "Byte".to_string(),
            "char" => "Char".to_string(),
            "short" => "Short".to_string(),
            "Integer" => "Int".to_string(),
            "Long" => "Long".to_string(),
            "Float" => "Float".to_string(),
            "Double" => "Double".to_string(),
            "Boolean" => "Boolean".to_string(),
            other => other.to_string(),
        }
    }

    /// Generate ArkTS adapter code
    fn generate_arkts(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> Result<String, CraftError> {
        let adapter_class = format!("{}Adapter", source_api.class_name);

        // Generate import statements
        let mut imports = Vec::new();
        imports.push(format!("import {{ {} }} from '@ohos.{}'", target_api.class_name, target_api.package));

        let imports_str = imports.join("\n");

        // Generate method implementations
        let method_impls = self.generate_arkts_method_implementations(
            mapping_rule,
            source_api,
            target_api,
        );

        let code = format!(
            r#"/**
 * Auto-generated by CRAFT v{version}
 * Source: {source_full_name}
 * Target: {target_full_name}
 * Confidence: {confidence:.2}
 * Generated: {generated_at}
 *
 * This adapter provides Android API compatibility layer for HarmonyOS.
 */

{imports}

/**
 * Adapter class providing {source_class} API over HarmonyOS {target_class}.
 */
export class {adapter_class} {{
    private delegate: {target_class};

    /**
     * Create adapter wrapping a HarmonyOS {target_class} instance.
     * @param delegate The HarmonyOS implementation to delegate to
     */
    constructor(delegate: {target_class}) {{
        this.delegate = delegate;
    }}

    /**
     * Get the underlying HarmonyOS delegate.
     * @returns The wrapped {target_class} instance
     */
    getDelegate(): {target_class} {{
        return this.delegate;
    }}

{method_impls}
}}
"#,
            version = self.version,
            source_full_name = source_api.full_qualified_name,
            target_full_name = target_api.full_qualified_name,
            confidence = mapping_rule.confidence,
            generated_at = Utc::now().to_rfc3339(),
            imports = imports_str,
            adapter_class = adapter_class,
            source_class = source_api.class_name,
            target_class = target_api.class_name,
            method_impls = method_impls,
        );

        Ok(code)
    }

    /// Generate ArkTS method implementations
    fn generate_arkts_method_implementations(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> String {
        let mut implementations = Vec::new();

        for source_method in &source_api.methods {
            if !source_method.modifiers.contains(&"public".to_string()) {
                continue;
            }

            let target_method_name = mapping_rule.method_mappings
                .iter()
                .find(|m| m.source_method == source_method.name)
                .map(|m| m.target_method.as_str())
                .unwrap_or(&source_method.name);

            // Check lifecycle mapping
            let target_name = if let Some(lifecycle_target) = self.lifecycle_mapping.get_target(&source_method.name) {
                lifecycle_target.method.clone()
            } else {
                target_method_name.to_string()
            };

            let params_str = source_method.parameters
                .iter()
                .map(|p| format!("{}: {}", p.name, self.java_to_ts_type(&p.param_type)))
                .collect::<Vec<_>>()
                .join(", ");

            let delegate_params = source_method.parameters
                .iter()
                .map(|p| p.name.clone())
                .collect::<Vec<_>>()
                .join(", ");

            let return_type = self.java_to_ts_type(&source_method.return_type);

            let impl_code = if return_type == "void" {
                format!(
                    r#"    /**
     * Adapted method: {source_name} -> {target_name}
     */
    {source_name}({params}): void {{
        this.delegate.{target_name}({delegate_params});
    }}"#,
                    source_name = source_method.name,
                    target_name = target_name,
                    params = params_str,
                    delegate_params = delegate_params,
                )
            } else {
                format!(
                    r#"    /**
     * Adapted method: {source_name} -> {target_name}
     */
    {source_name}({params}): {return_type} {{
        return this.delegate.{target_name}({delegate_params});
    }}"#,
                    source_name = source_method.name,
                    target_name = target_name,
                    params = params_str,
                    return_type = return_type,
                    delegate_params = delegate_params,
                )
            };

            implementations.push(impl_code);
        }

        implementations.join("\n\n")
    }

    /// Convert Java type to TypeScript type
    fn java_to_ts_type(&self, java_type: &str) -> String {
        match java_type {
            "void" => "void".to_string(),
            "int" | "long" | "float" | "double" | "byte" | "short" => "number".to_string(),
            "Integer" | "Long" | "Float" | "Double" | "Byte" | "Short" => "number".to_string(),
            "boolean" | "Boolean" => "boolean".to_string(),
            "String" | "char" | "Character" => "string".to_string(),
            "Object" => "any".to_string(),
            other if other.starts_with("List<") => {
                let inner = &other[5..other.len()-1];
                format!("{}[]", self.java_to_ts_type(inner))
            }
            other if other.starts_with("Map<") => "Record<string, any>".to_string(),
            other if other.ends_with("[]") => {
                let inner = &other[..other.len()-2];
                format!("{}[]", self.java_to_ts_type(inner))
            }
            other => other.to_string(),
        }
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
    use craft_core::{ApiReference, Platform};

    fn create_test_source_api() -> ApiSpec {
        let mut spec = ApiSpec::new(Platform::Android, "android.app", "Activity");
        spec.methods = vec![
            MethodSpec {
                name: "onCreate".to_string(),
                signature: "onCreate(Bundle)".to_string(),
                return_type: "void".to_string(),
                parameters: vec![
                    ParameterSpec {
                        name: "savedInstanceState".to_string(),
                        param_type: "Bundle".to_string(),
                        nullable: true,
                        default_value: None,
                    }
                ],
                modifiers: vec!["public".to_string()],
                semantic_tags: vec!["lifecycle:onCreate".to_string()],
                doc_comment: None,
            },
            MethodSpec {
                name: "onDestroy".to_string(),
                signature: "onDestroy()".to_string(),
                return_type: "void".to_string(),
                parameters: vec![],
                modifiers: vec!["public".to_string()],
                semantic_tags: vec!["lifecycle:onDestroy".to_string()],
                doc_comment: None,
            },
            MethodSpec {
                name: "getTitle".to_string(),
                signature: "getTitle()".to_string(),
                return_type: "String".to_string(),
                parameters: vec![],
                modifiers: vec!["public".to_string()],
                semantic_tags: vec![],
                doc_comment: None,
            },
        ];
        spec
    }

    fn create_test_target_api() -> ApiSpec {
        let mut spec = ApiSpec::new(Platform::Harmony, "ohos.app.ability", "UIAbility");
        spec.methods = vec![
            MethodSpec {
                name: "onCreate".to_string(),
                signature: "onCreate(Want)".to_string(),
                return_type: "void".to_string(),
                parameters: vec![
                    ParameterSpec {
                        name: "want".to_string(),
                        param_type: "Want".to_string(),
                        nullable: false,
                        default_value: None,
                    }
                ],
                modifiers: vec!["public".to_string()],
                semantic_tags: vec!["lifecycle:onCreate".to_string()],
                doc_comment: None,
            },
            MethodSpec {
                name: "onDestroy".to_string(),
                signature: "onDestroy()".to_string(),
                return_type: "void".to_string(),
                parameters: vec![],
                modifiers: vec!["public".to_string()],
                semantic_tags: vec!["lifecycle:onDestroy".to_string()],
                doc_comment: None,
            },
            MethodSpec {
                name: "getTitle".to_string(),
                signature: "getTitle()".to_string(),
                return_type: "string".to_string(),
                parameters: vec![],
                modifiers: vec!["public".to_string()],
                semantic_tags: vec![],
                doc_comment: None,
            },
        ];
        spec
    }

    fn create_test_mapping_rule() -> MappingRule {
        MappingRule::new(
            ApiReference {
                platform: Platform::Android,
                class: "android.app.Activity".to_string(),
            },
            ApiReference {
                platform: Platform::Harmony,
                class: "ohos.app.ability.UIAbility".to_string(),
            },
            MappingType::Semantic,
        )
    }

    #[test]
    fn test_generator_creation() {
        let generator = AdapterGenerator::new();
        assert!(generator.tera.is_none());
    }

    #[test]
    fn test_lifecycle_mapping() {
        let mapping = LifecycleMapping::activity_to_uiability();

        assert!(mapping.is_lifecycle_method("onCreate"));
        assert!(mapping.is_lifecycle_method("onDestroy"));
        assert!(!mapping.is_lifecycle_method("getTitle"));

        let target = mapping.get_target("onStart").unwrap();
        assert_eq!(target.method, "onForeground");
    }

    #[test]
    fn test_generate_java_adapter() {
        let generator = AdapterGenerator::new();
        let source_api = create_test_source_api();
        let target_api = create_test_target_api();
        let mapping_rule = create_test_mapping_rule();

        let code = generator.generate(&mapping_rule, &source_api, &target_api, "java").unwrap();

        assert!(code.contains("class ActivityAdapter"));
        assert!(code.contains("private final UIAbility delegate"));
        assert!(code.contains("onCreate"));
        assert!(code.contains("onDestroy"));
        assert!(code.contains("delegate."));
    }

    #[test]
    fn test_generate_kotlin_adapter() {
        let generator = AdapterGenerator::new();
        let source_api = create_test_source_api();
        let target_api = create_test_target_api();
        let mapping_rule = create_test_mapping_rule();

        let code = generator.generate(&mapping_rule, &source_api, &target_api, "kotlin").unwrap();

        assert!(code.contains("class ActivityAdapter"));
        assert!(code.contains("private val delegate: UIAbility"));
        assert!(code.contains("override fun onCreate"));
    }

    #[test]
    fn test_generate_arkts_adapter() {
        let generator = AdapterGenerator::new();
        let source_api = create_test_source_api();
        let target_api = create_test_target_api();
        let mapping_rule = create_test_mapping_rule();

        let code = generator.generate(&mapping_rule, &source_api, &target_api, "arkts").unwrap();

        assert!(code.contains("export class ActivityAdapter"));
        assert!(code.contains("private delegate: UIAbility"));
        assert!(code.contains("this.delegate."));
    }

    #[test]
    fn test_java_to_ts_type_conversion() {
        let generator = AdapterGenerator::new();

        assert_eq!(generator.java_to_ts_type("int"), "number");
        assert_eq!(generator.java_to_ts_type("String"), "string");
        assert_eq!(generator.java_to_ts_type("boolean"), "boolean");
        assert_eq!(generator.java_to_ts_type("List<String>"), "string[]");
        assert_eq!(generator.java_to_ts_type("int[]"), "number[]");
    }
}
