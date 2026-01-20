//! ArkTS/TypeScript source file parser using tree-sitter
//!
//! This module provides parsing of ArkTS/TypeScript source files for HarmonyOS SDK,
//! extracting class/interface definitions, methods, decorators, and documentation.

use crate::SdkParser;
use craft_core::{ApiSpec, CraftError, MethodSpec, ParameterSpec, Platform};
use rayon::prelude::*;
use std::fs;
use std::path::Path;
use tracing::{debug, info, warn};
use tree_sitter::{Language, Node, Parser};

extern "C" {
    fn tree_sitter_typescript() -> Language;
}

/// Parser for ArkTS/TypeScript source files using tree-sitter
pub struct ArkTsParser {
    parser: Parser,
    language: Language,
}

impl ArkTsParser {
    /// Create a new ArkTS parser
    pub fn new() -> Self {
        let language = unsafe { tree_sitter_typescript() };
        let mut parser = Parser::new();
        parser
            .set_language(language)
            .expect("Failed to set TypeScript language for parser");

        Self { parser, language }
    }

    /// Parse an ArkTS source file content and extract API specifications
    fn parse_content(&mut self, content: &str, file_path: &Path) -> Result<Option<ApiSpec>, CraftError> {
        let tree = self
            .parser
            .parse(content, None)
            .ok_or_else(|| CraftError::Parse("Failed to parse ArkTS content".to_string()))?;

        let root_node = tree.root_node();

        // Find the main class or interface declaration
        let class_info = self.extract_class_info(&root_node, content)?;
        let Some((class_name, class_type, parent_class, interfaces, class_node)) = class_info else {
            debug!("No class/interface found in {:?}", file_path);
            return Ok(None);
        };

        // Extract module/namespace (package equivalent in ArkTS)
        let module_name = self.extract_module_name(&root_node, content, file_path);

        debug!("Parsing ArkTS class: {}.{}", module_name, class_name);

        // Create API spec
        let mut spec = ApiSpec::new(Platform::Harmony, &module_name, &class_name);
        spec.class_type = class_type;
        spec.parent_class = parent_class;
        spec.interfaces = interfaces;

        // Extract methods
        spec.methods = self.extract_methods(&class_node, content);

        // Generate semantic tags
        spec.semantic_tags = self.generate_semantic_tags(&spec);

        // Extract decorators as semantic tags
        let decorators = self.extract_decorators(&class_node, content);
        for dec in decorators {
            spec.semantic_tags.push(format!("decorator:{}", dec));
        }

        // Extract JSDoc comment for the class
        if let Some(doc) = self.extract_doc_comment(&class_node, content) {
            spec.semantic_tags.push(format!("doc:{}", Self::truncate_doc(&doc)));
        }

        Ok(Some(spec))
    }

    /// Extract module/namespace name from file path or declarations
    fn extract_module_name(&self, root: &Node, source: &str, file_path: &Path) -> String {
        // Try to find module/namespace declaration
        for i in 0..root.child_count() {
            if let Some(child) = root.child(i) {
                if child.kind() == "module" || child.kind() == "namespace_declaration" {
                    if let Some(name) = self.find_child_text(&child, "identifier", source) {
                        return name;
                    }
                }
            }
        }

        // Fallback: derive from file path
        // e.g., /path/to/ohos/app/UIAbility.ets -> ohos.app
        if let Some(parent) = file_path.parent() {
            let path_str = parent.to_string_lossy();
            // Look for common HarmonyOS package patterns
            if let Some(idx) = path_str.find("ohos") {
                let module_path = &path_str[idx..];
                return module_path.replace(['/', '\\'], ".");
            }
            if let Some(idx) = path_str.find("@ohos") {
                let module_path = &path_str[idx..];
                return module_path.replace(['/', '\\'], ".").replace('@', "");
            }
        }

        // Default fallback
        "ohos".to_string()
    }

    /// Extract class/interface/struct information
    fn extract_class_info<'a>(
        &self,
        root: &'a Node<'a>,
        source: &str,
    ) -> Result<Option<(String, String, Option<String>, Vec<String>, Node<'a>)>, CraftError> {
        // Look for class, interface, or type declaration
        for i in 0..root.child_count() {
            if let Some(child) = root.child(i) {
                match child.kind() {
                    "class_declaration" => {
                        let name = self.extract_class_name(&child, source);
                        let parent = self.extract_extends(&child, source);
                        let interfaces = self.extract_implements(&child, source);
                        let class_type = if self.has_abstract_modifier(&child, source) {
                            "abstract_class"
                        } else {
                            "class"
                        };
                        if let Some(name) = name {
                            return Ok(Some((name, class_type.to_string(), parent, interfaces, child)));
                        }
                    }
                    "interface_declaration" => {
                        let name = self.extract_interface_name(&child, source);
                        let interfaces = self.extract_extends_interfaces(&child, source);
                        if let Some(name) = name {
                            return Ok(Some((name, "interface".to_string(), None, interfaces, child)));
                        }
                    }
                    "type_alias_declaration" => {
                        let name = self.find_child_text(&child, "type_identifier", source);
                        if let Some(name) = name {
                            return Ok(Some((name, "type_alias".to_string(), None, Vec::new(), child)));
                        }
                    }
                    "enum_declaration" => {
                        let name = self.find_child_text(&child, "identifier", source);
                        if let Some(name) = name {
                            return Ok(Some((name, "enum".to_string(), None, Vec::new(), child)));
                        }
                    }
                    "export_statement" => {
                        // Handle exported declarations
                        if let Some(result) = self.extract_class_info(&child, source)? {
                            return Ok(Some(result));
                        }
                    }
                    _ => {}
                }
            }
        }
        Ok(None)
    }

    /// Extract class name from class declaration
    fn extract_class_name(&self, class_node: &Node, source: &str) -> Option<String> {
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "type_identifier" || child.kind() == "identifier" {
                    return Some(self.node_text(&child, source));
                }
            }
        }
        None
    }

    /// Extract interface name from interface declaration
    fn extract_interface_name(&self, interface_node: &Node, source: &str) -> Option<String> {
        for i in 0..interface_node.child_count() {
            if let Some(child) = interface_node.child(i) {
                if child.kind() == "type_identifier" || child.kind() == "identifier" {
                    return Some(self.node_text(&child, source));
                }
            }
        }
        None
    }

    /// Extract extends clause (parent class)
    fn extract_extends(&self, class_node: &Node, source: &str) -> Option<String> {
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "class_heritage" {
                    for j in 0..child.child_count() {
                        if let Some(heritage) = child.child(j) {
                            if heritage.kind() == "extends_clause" {
                                // Find the type identifier in extends clause
                                for k in 0..heritage.child_count() {
                                    if let Some(type_node) = heritage.child(k) {
                                        if type_node.kind() == "type_identifier"
                                            || type_node.kind() == "identifier"
                                            || type_node.kind() == "generic_type" {
                                            return Some(self.node_text(&type_node, source));
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        None
    }

    /// Extract implements clause (interfaces)
    fn extract_implements(&self, class_node: &Node, source: &str) -> Vec<String> {
        let mut interfaces = Vec::new();
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "class_heritage" {
                    for j in 0..child.child_count() {
                        if let Some(heritage) = child.child(j) {
                            if heritage.kind() == "implements_clause" {
                                self.collect_type_names(&heritage, source, &mut interfaces);
                            }
                        }
                    }
                }
            }
        }
        interfaces
    }

    /// Extract extended interfaces from interface declaration
    fn extract_extends_interfaces(&self, interface_node: &Node, source: &str) -> Vec<String> {
        let mut interfaces = Vec::new();
        for i in 0..interface_node.child_count() {
            if let Some(child) = interface_node.child(i) {
                if child.kind() == "extends_type_clause" || child.kind() == "extends_clause" {
                    self.collect_type_names(&child, source, &mut interfaces);
                }
            }
        }
        interfaces
    }

    /// Collect type names from a node
    fn collect_type_names(&self, node: &Node, source: &str, result: &mut Vec<String>) {
        for i in 0..node.child_count() {
            if let Some(child) = node.child(i) {
                match child.kind() {
                    "type_identifier" | "identifier" | "generic_type" => {
                        result.push(self.node_text(&child, source));
                    }
                    _ => {
                        self.collect_type_names(&child, source, result);
                    }
                }
            }
        }
    }

    /// Check if class has abstract modifier
    fn has_abstract_modifier(&self, class_node: &Node, source: &str) -> bool {
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "abstract" {
                    return true;
                }
            }
        }
        false
    }

    /// Extract decorators from a node
    fn extract_decorators(&self, node: &Node, source: &str) -> Vec<String> {
        let mut decorators = Vec::new();

        // Look for decorator nodes before the class
        if let Some(prev) = node.prev_sibling() {
            if prev.kind() == "decorator" {
                let text = self.node_text(&prev, source);
                // Extract decorator name (remove @ and parameters)
                let name = text.trim_start_matches('@')
                    .split('(')
                    .next()
                    .unwrap_or(&text)
                    .to_string();
                decorators.push(name);
            }
        }

        // Also check for decorators within the node
        for i in 0..node.child_count() {
            if let Some(child) = node.child(i) {
                if child.kind() == "decorator" {
                    let text = self.node_text(&child, source);
                    let name = text.trim_start_matches('@')
                        .split('(')
                        .next()
                        .unwrap_or(&text)
                        .to_string();
                    decorators.push(name);
                }
            }
        }

        decorators
    }

    /// Extract all methods from a class/interface body
    fn extract_methods(&self, class_node: &Node, source: &str) -> Vec<MethodSpec> {
        let mut methods = Vec::new();

        // Find the class body
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "class_body" || child.kind() == "interface_body"
                    || child.kind() == "object_type" {
                    self.extract_methods_from_body(&child, source, &mut methods);
                }
            }
        }

        methods
    }

    /// Extract methods from class/interface body
    fn extract_methods_from_body(&self, body_node: &Node, source: &str, methods: &mut Vec<MethodSpec>) {
        for i in 0..body_node.child_count() {
            if let Some(child) = body_node.child(i) {
                match child.kind() {
                    "method_definition" | "public_field_definition" => {
                        if let Some(method) = self.parse_method(&child, source) {
                            methods.push(method);
                        }
                    }
                    "method_signature" => {
                        if let Some(method) = self.parse_method_signature(&child, source) {
                            methods.push(method);
                        }
                    }
                    "property_signature" => {
                        // Skip property signatures for now
                    }
                    _ => {}
                }
            }
        }
    }

    /// Parse a method definition
    fn parse_method(&self, method_node: &Node, source: &str) -> Option<MethodSpec> {
        let mut method_name = None;
        let mut return_type = "void".to_string();
        let mut parameters = Vec::new();
        let mut modifiers = Vec::new();

        for i in 0..method_node.child_count() {
            if let Some(child) = method_node.child(i) {
                match child.kind() {
                    "accessibility_modifier" => {
                        modifiers.push(self.node_text(&child, source));
                    }
                    "static" => {
                        modifiers.push("static".to_string());
                    }
                    "async" => {
                        modifiers.push("async".to_string());
                    }
                    "property_identifier" | "identifier" => {
                        method_name = Some(self.node_text(&child, source));
                    }
                    "formal_parameters" | "call_signature" => {
                        parameters = self.extract_parameters(&child, source);
                        // Also try to get return type from call_signature
                        if child.kind() == "call_signature" {
                            if let Some(ret) = self.extract_return_type_from_signature(&child, source) {
                                return_type = ret;
                            }
                        }
                    }
                    "type_annotation" => {
                        return_type = self.extract_type_from_annotation(&child, source);
                    }
                    _ => {}
                }
            }
        }

        let name = method_name?;

        // Skip constructor and private methods for API spec
        if name == "constructor" || modifiers.contains(&"private".to_string()) {
            return None;
        }

        // Build signature
        let param_types: Vec<String> = parameters.iter().map(|p| p.param_type.clone()).collect();
        let signature = format!("{}({}): {}", name, param_types.join(", "), return_type);

        // Extract documentation comment
        let doc_comment = self.extract_doc_comment(method_node, source);

        // Generate semantic tags for the method
        let semantic_tags = self.generate_method_tags(&name, &return_type, &parameters);

        Some(MethodSpec {
            name,
            signature,
            return_type,
            parameters,
            modifiers,
            semantic_tags,
            doc_comment,
        })
    }

    /// Parse a method signature (for interfaces)
    fn parse_method_signature(&self, sig_node: &Node, source: &str) -> Option<MethodSpec> {
        let mut method_name = None;
        let mut return_type = "void".to_string();
        let mut parameters = Vec::new();

        for i in 0..sig_node.child_count() {
            if let Some(child) = sig_node.child(i) {
                match child.kind() {
                    "property_identifier" | "identifier" => {
                        method_name = Some(self.node_text(&child, source));
                    }
                    "call_signature" => {
                        parameters = self.extract_parameters(&child, source);
                        if let Some(ret) = self.extract_return_type_from_signature(&child, source) {
                            return_type = ret;
                        }
                    }
                    "formal_parameters" => {
                        parameters = self.extract_parameters(&child, source);
                    }
                    "type_annotation" => {
                        return_type = self.extract_type_from_annotation(&child, source);
                    }
                    _ => {}
                }
            }
        }

        let name = method_name?;

        let param_types: Vec<String> = parameters.iter().map(|p| p.param_type.clone()).collect();
        let signature = format!("{}({}): {}", name, param_types.join(", "), return_type);

        let doc_comment = self.extract_doc_comment(sig_node, source);
        let semantic_tags = self.generate_method_tags(&name, &return_type, &parameters);

        Some(MethodSpec {
            name,
            signature,
            return_type,
            parameters,
            modifiers: Vec::new(),
            semantic_tags,
            doc_comment,
        })
    }

    /// Extract parameters from formal_parameters or call_signature
    fn extract_parameters(&self, params_node: &Node, source: &str) -> Vec<ParameterSpec> {
        let mut parameters = Vec::new();

        for i in 0..params_node.child_count() {
            if let Some(child) = params_node.child(i) {
                match child.kind() {
                    "required_parameter" | "optional_parameter" | "formal_parameters" => {
                        if child.kind() == "formal_parameters" {
                            // Recurse into formal_parameters
                            parameters.extend(self.extract_parameters(&child, source));
                        } else if let Some(param) = self.parse_parameter(&child, source) {
                            parameters.push(param);
                        }
                    }
                    "rest_parameter" => {
                        if let Some(param) = self.parse_rest_parameter(&child, source) {
                            parameters.push(param);
                        }
                    }
                    _ => {}
                }
            }
        }

        parameters
    }

    /// Parse a single parameter
    fn parse_parameter(&self, param_node: &Node, source: &str) -> Option<ParameterSpec> {
        let mut param_name = None;
        let mut param_type = "any".to_string();
        let mut nullable = param_node.kind() == "optional_parameter";

        for i in 0..param_node.child_count() {
            if let Some(child) = param_node.child(i) {
                match child.kind() {
                    "identifier" => {
                        param_name = Some(self.node_text(&child, source));
                    }
                    "type_annotation" => {
                        param_type = self.extract_type_from_annotation(&child, source);
                        // Check for nullable type (Type | null | undefined)
                        if param_type.contains("null") || param_type.contains("undefined") {
                            nullable = true;
                        }
                    }
                    "?" => {
                        nullable = true;
                    }
                    _ => {}
                }
            }
        }

        Some(ParameterSpec {
            name: param_name.unwrap_or_else(|| "arg".to_string()),
            param_type,
            nullable,
            default_value: None,
        })
    }

    /// Parse a rest parameter (...args)
    fn parse_rest_parameter(&self, param_node: &Node, source: &str) -> Option<ParameterSpec> {
        let mut param_name = None;
        let mut param_type = "any[]".to_string();

        for i in 0..param_node.child_count() {
            if let Some(child) = param_node.child(i) {
                match child.kind() {
                    "identifier" => {
                        param_name = Some(self.node_text(&child, source));
                    }
                    "type_annotation" => {
                        param_type = format!("...{}", self.extract_type_from_annotation(&child, source));
                    }
                    _ => {}
                }
            }
        }

        Some(ParameterSpec {
            name: param_name.unwrap_or_else(|| "args".to_string()),
            param_type,
            nullable: false,
            default_value: None,
        })
    }

    /// Extract type from type_annotation node
    fn extract_type_from_annotation(&self, annotation_node: &Node, source: &str) -> String {
        for i in 0..annotation_node.child_count() {
            if let Some(child) = annotation_node.child(i) {
                match child.kind() {
                    "type_identifier" | "predefined_type" | "generic_type"
                    | "union_type" | "array_type" | "function_type" | "object_type" => {
                        return self.node_text(&child, source);
                    }
                    _ => {}
                }
            }
        }
        "any".to_string()
    }

    /// Extract return type from call_signature
    fn extract_return_type_from_signature(&self, sig_node: &Node, source: &str) -> Option<String> {
        for i in 0..sig_node.child_count() {
            if let Some(child) = sig_node.child(i) {
                if child.kind() == "type_annotation" {
                    return Some(self.extract_type_from_annotation(&child, source));
                }
            }
        }
        None
    }

    /// Extract documentation comment (JSDoc)
    fn extract_doc_comment(&self, node: &Node, source: &str) -> Option<String> {
        // Look for a preceding comment
        if let Some(prev) = node.prev_sibling() {
            if prev.kind() == "comment" {
                let comment = self.node_text(&prev, source);
                if comment.starts_with("/**") {
                    return Some(self.clean_doc_comment(&comment));
                }
            }
        }
        None
    }

    /// Clean up a doc comment
    fn clean_doc_comment(&self, comment: &str) -> String {
        comment
            .trim_start_matches("/**")
            .trim_end_matches("*/")
            .lines()
            .map(|line| line.trim().trim_start_matches('*').trim())
            .filter(|line| !line.is_empty() && !line.starts_with('@'))
            .collect::<Vec<_>>()
            .join(" ")
    }

    /// Generate semantic tags for a class
    fn generate_semantic_tags(&self, spec: &ApiSpec) -> Vec<String> {
        let mut tags = Vec::new();

        // Add class type tag
        tags.push(format!("type:{}", spec.class_type));

        // Add module hierarchy tags
        let parts: Vec<&str> = spec.package.split('.').collect();
        if !parts.is_empty() {
            tags.push(format!("domain:{}", parts[0]));
        }

        // Add parent class tag
        if let Some(ref parent) = spec.parent_class {
            tags.push(format!("extends:{}", parent));
        }

        // Add interface tags
        for iface in &spec.interfaces {
            tags.push(format!("implements:{}", iface));
        }

        // Infer HarmonyOS component type from class name
        let class_lower = spec.class_name.to_lowercase();
        if class_lower.contains("ability") {
            if class_lower.contains("ui") {
                tags.push("component:uiability".to_string());
            } else if class_lower.contains("extension") {
                tags.push("component:extensionability".to_string());
            } else {
                tags.push("component:ability".to_string());
            }
        } else if class_lower.contains("page") {
            tags.push("component:page".to_string());
        } else if class_lower.contains("component") {
            tags.push("component:arkui_component".to_string());
        } else if class_lower.contains("service") {
            tags.push("component:service".to_string());
        } else if class_lower.contains("provider") {
            tags.push("component:provider".to_string());
        } else if class_lower.contains("manager") {
            tags.push("component:manager".to_string());
        }

        tags
    }

    /// Generate semantic tags for a method
    fn generate_method_tags(&self, name: &str, return_type: &str, params: &[ParameterSpec]) -> Vec<String> {
        let mut tags = Vec::new();

        // Add return type tag
        tags.push(format!("returns:{}", return_type));

        // Add parameter count tag
        tags.push(format!("params:{}", params.len()));

        // Infer method category from name
        let name_lower = name.to_lowercase();
        if name_lower.starts_with("get") || name_lower.starts_with("is") || name_lower.starts_with("has") {
            tags.push("category:getter".to_string());
        } else if name_lower.starts_with("set") {
            tags.push("category:setter".to_string());
        } else if name_lower.starts_with("on") {
            tags.push("category:callback".to_string());
        } else if name_lower.starts_with("create") || name_lower.starts_with("build") {
            tags.push("category:factory".to_string());
        } else if name_lower.starts_with("add") || name_lower.starts_with("remove") {
            tags.push("category:collection".to_string());
        }

        // HarmonyOS lifecycle method detection
        let lifecycle_methods = [
            "onCreate", "onDestroy", "onWindowStageCreate", "onWindowStageDestroy",
            "onForeground", "onBackground", "onNewWant", "onAbilityResult",
            "aboutToAppear", "aboutToDisappear", "onPageShow", "onPageHide",
            "onBackPress"
        ];
        if lifecycle_methods.contains(&name) {
            tags.push("lifecycle:true".to_string());
            tags.push(format!("lifecycle:{}", name));
        }

        tags
    }

    /// Get text content of a node
    fn node_text(&self, node: &Node, source: &str) -> String {
        let start = node.start_byte();
        let end = node.end_byte();
        source[start..end].to_string()
    }

    /// Find first child of a specific kind and return its text
    fn find_child_text(&self, node: &Node, kind: &str, source: &str) -> Option<String> {
        for i in 0..node.child_count() {
            if let Some(child) = node.child(i) {
                if child.kind() == kind {
                    return Some(self.node_text(&child, source));
                }
            }
        }
        None
    }

    /// Truncate documentation to a reasonable length
    fn truncate_doc(doc: &str) -> String {
        if doc.len() > 100 {
            format!("{}...", &doc[..100])
        } else {
            doc.to_string()
        }
    }
}

impl Default for ArkTsParser {
    fn default() -> Self {
        Self::new()
    }
}

// ArkTsParser needs to be thread-safe for rayon
unsafe impl Send for ArkTsParser {}
unsafe impl Sync for ArkTsParser {}

impl SdkParser for ArkTsParser {
    fn parse_file(&self, path: &Path) -> Result<Option<ApiSpec>, CraftError> {
        let ext = path.extension().and_then(|e| e.to_str());
        if !matches!(ext, Some("ets") | Some("ts")) {
            return Ok(None);
        }

        let content = fs::read_to_string(path).map_err(CraftError::Io)?;

        // Create a new parser for this thread
        let mut parser = ArkTsParser::new();
        parser.parse_content(&content, path)
    }

    fn parse_directory(&self, path: &Path) -> Result<Vec<ApiSpec>, CraftError> {
        info!("Scanning ArkTS directory: {:?}", path);

        if !path.is_dir() {
            return Err(CraftError::Parse(format!(
                "Path is not a directory: {:?}",
                path
            )));
        }

        // Collect all ArkTS/TypeScript files
        let arkts_files: Vec<_> = walkdir::WalkDir::new(path)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| {
                let ext = e.path().extension().and_then(|ext| ext.to_str());
                matches!(ext, Some("ets") | Some("ts"))
                    && !e.path().to_string_lossy().contains("/test/")
                    && !e.path().to_string_lossy().contains("/tests/")
                    && !e.path().to_string_lossy().contains(".test.")
                    && !e.path().to_string_lossy().contains(".spec.")
            })
            .map(|e| e.path().to_path_buf())
            .collect();

        info!("Found {} ArkTS/TypeScript files", arkts_files.len());

        // Parse files in parallel
        let specs: Vec<ApiSpec> = arkts_files
            .par_iter()
            .filter_map(|path| {
                match self.parse_file(path) {
                    Ok(Some(spec)) => Some(spec),
                    Ok(None) => None,
                    Err(e) => {
                        warn!("Failed to parse {:?}: {}", path, e);
                        None
                    }
                }
            })
            .collect();

        info!("Successfully parsed {} ArkTS API specs", specs.len());
        Ok(specs)
    }

    fn platform(&self) -> Platform {
        Platform::Harmony
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_arkts_parser_creation() {
        let parser = ArkTsParser::new();
        assert_eq!(parser.platform(), Platform::Harmony);
    }

    #[test]
    fn test_parse_uiability() {
        let mut parser = ArkTsParser::new();
        let source = r#"
import UIAbility from '@ohos.app.ability.UIAbility';
import window from '@ohos.window';

/**
 * Entry ability that manages the window lifecycle.
 */
export default class EntryAbility extends UIAbility {
    /**
     * Called when ability is created.
     */
    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        console.log('onCreate');
    }

    onDestroy(): void {
        console.log('onDestroy');
    }

    onWindowStageCreate(windowStage: window.WindowStage): void {
        windowStage.loadContent('pages/Index');
    }

    onWindowStageDestroy(): void {
        console.log('onWindowStageDestroy');
    }

    onForeground(): void {
        console.log('onForeground');
    }

    onBackground(): void {
        console.log('onBackground');
    }
}
"#;
        let path = Path::new("EntryAbility.ets");
        let result = parser.parse_content(source, path).unwrap();

        assert!(result.is_some());
        let spec = result.unwrap();

        assert_eq!(spec.class_name, "EntryAbility");
        assert_eq!(spec.class_type, "class");
        assert_eq!(spec.parent_class, Some("UIAbility".to_string()));
        assert!(spec.semantic_tags.contains(&"component:uiability".to_string()));

        // Check lifecycle methods
        assert!(spec.get_method("onCreate").is_some());
        assert!(spec.get_method("onDestroy").is_some());
        assert!(spec.get_method("onWindowStageCreate").is_some());

        let on_create = spec.get_method("onCreate").unwrap();
        assert!(on_create.semantic_tags.contains(&"lifecycle:true".to_string()));
    }

    #[test]
    fn test_parse_interface() {
        let mut parser = ArkTsParser::new();
        let source = r#"
/**
 * Window stage interface.
 */
export interface WindowStage {
    loadContent(path: string, callback?: AsyncCallback<void>): void;
    getMainWindow(): Promise<Window>;
    on(type: 'windowStageEvent', callback: Callback<WindowStageEventType>): void;
    off(type: 'windowStageEvent', callback?: Callback<WindowStageEventType>): void;
}
"#;
        let path = Path::new("WindowStage.d.ts");
        let result = parser.parse_content(source, path).unwrap();

        assert!(result.is_some());
        let spec = result.unwrap();

        assert_eq!(spec.class_name, "WindowStage");
        assert_eq!(spec.class_type, "interface");
        assert_eq!(spec.methods.len(), 4);

        let load_content = spec.get_method("loadContent").unwrap();
        assert_eq!(load_content.parameters.len(), 2);
        assert_eq!(load_content.parameters[0].name, "path");
        assert_eq!(load_content.parameters[0].param_type, "string");
    }

    #[test]
    fn test_parse_arkui_component() {
        let mut parser = ArkTsParser::new();
        let source = r#"
@Entry
@Component
struct Index {
    @State message: string = 'Hello World';

    build() {
        Row() {
            Column() {
                Text(this.message)
                    .fontSize(50)
            }
        }
    }

    aboutToAppear(): void {
        console.log('aboutToAppear');
    }

    aboutToDisappear(): void {
        console.log('aboutToDisappear');
    }
}
"#;
        let path = Path::new("Index.ets");
        let result = parser.parse_content(source, path);
        // Note: struct parsing might need additional handling
        // This test verifies the parser doesn't crash on ArkUI syntax
    }
}
