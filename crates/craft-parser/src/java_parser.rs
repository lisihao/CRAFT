//! Java source file parser using tree-sitter
//!
//! This module provides accurate parsing of Java source files using tree-sitter,
//! extracting class/interface definitions, methods, fields, and documentation.

use crate::SdkParser;
use craft_core::{ApiSpec, CraftError, MethodSpec, ParameterSpec, Platform};
use rayon::prelude::*;
use std::fs;
use std::path::Path;
use tracing::{debug, info, warn};
use tree_sitter::{Language, Node, Parser};

extern "C" {
    fn tree_sitter_java() -> Language;
}

/// Parser for Java source files using tree-sitter
pub struct JavaParser {
    parser: Parser,
    language: Language,
}

impl JavaParser {
    /// Create a new Java parser
    pub fn new() -> Self {
        let language = unsafe { tree_sitter_java() };
        let mut parser = Parser::new();
        parser
            .set_language(language)
            .expect("Failed to set Java language for parser");

        Self { parser, language }
    }

    /// Parse a Java source file content and extract API specifications
    fn parse_content(&mut self, content: &str, file_path: &Path) -> Result<Option<ApiSpec>, CraftError> {
        let tree = self
            .parser
            .parse(content, None)
            .ok_or_else(|| CraftError::Parse("Failed to parse Java content".to_string()))?;

        let root_node = tree.root_node();

        // Extract package name
        let package = self.extract_package(&root_node, content);
        if package.is_none() {
            debug!("No package found in {:?}", file_path);
        }

        // Find class or interface declaration
        let class_info = self.extract_class_info(&root_node, content)?;
        let Some((class_name, class_type, parent_class, interfaces, class_node)) = class_info else {
            debug!("No class/interface found in {:?}", file_path);
            return Ok(None);
        };

        let package_name = package.unwrap_or_else(|| "".to_string());
        debug!("Parsing class: {}.{}", package_name, class_name);

        // Create API spec
        let mut spec = ApiSpec::new(Platform::Android, &package_name, &class_name);
        spec.class_type = class_type;
        spec.parent_class = parent_class;
        spec.interfaces = interfaces;

        // Extract methods
        spec.methods = self.extract_methods(&class_node, content);

        // Generate semantic tags
        spec.semantic_tags = self.generate_semantic_tags(&spec);

        // Extract documentation comment for the class
        if let Some(doc) = self.extract_doc_comment(&class_node, content) {
            spec.semantic_tags.push(format!("doc:{}", Self::truncate_doc(&doc)));
        }

        Ok(Some(spec))
    }

    /// Extract package name from the AST
    fn extract_package(&self, root: &Node, source: &str) -> Option<String> {
        for i in 0..root.child_count() {
            if let Some(child) = root.child(i) {
                if child.kind() == "package_declaration" {
                    // Find the scoped_identifier or identifier within package declaration
                    for j in 0..child.child_count() {
                        if let Some(id_node) = child.child(j) {
                            if id_node.kind() == "scoped_identifier" || id_node.kind() == "identifier" {
                                return Some(self.node_text(&id_node, source));
                            }
                        }
                    }
                }
            }
        }
        None
    }

    /// Extract class/interface information
    fn extract_class_info<'a>(
        &self,
        root: &'a Node<'a>,
        source: &str,
    ) -> Result<Option<(String, String, Option<String>, Vec<String>, Node<'a>)>, CraftError> {
        // Look for class or interface declaration
        for i in 0..root.child_count() {
            if let Some(child) = root.child(i) {
                match child.kind() {
                    "class_declaration" => {
                        let name = self.find_child_text(&child, "identifier", source);
                        let parent = self.extract_superclass(&child, source);
                        let interfaces = self.extract_interfaces(&child, source);
                        let class_type = if self.has_modifier(&child, "abstract", source) {
                            "abstract_class"
                        } else {
                            "class"
                        };
                        if let Some(name) = name {
                            return Ok(Some((name, class_type.to_string(), parent, interfaces, child)));
                        }
                    }
                    "interface_declaration" => {
                        let name = self.find_child_text(&child, "identifier", source);
                        let interfaces = self.extract_extended_interfaces(&child, source);
                        if let Some(name) = name {
                            return Ok(Some((name, "interface".to_string(), None, interfaces, child)));
                        }
                    }
                    "enum_declaration" => {
                        let name = self.find_child_text(&child, "identifier", source);
                        let interfaces = self.extract_interfaces(&child, source);
                        if let Some(name) = name {
                            return Ok(Some((name, "enum".to_string(), None, interfaces, child)));
                        }
                    }
                    _ => {}
                }
            }
        }
        Ok(None)
    }

    /// Extract superclass from class declaration
    fn extract_superclass(&self, class_node: &Node, source: &str) -> Option<String> {
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "superclass" {
                    // Find the type_identifier within superclass
                    for j in 0..child.child_count() {
                        if let Some(type_node) = child.child(j) {
                            if type_node.kind() == "type_identifier" || type_node.kind() == "scoped_type_identifier" {
                                return Some(self.node_text(&type_node, source));
                            }
                        }
                    }
                }
            }
        }
        None
    }

    /// Extract implemented interfaces from class declaration
    fn extract_interfaces(&self, class_node: &Node, source: &str) -> Vec<String> {
        let mut interfaces = Vec::new();
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "super_interfaces" || child.kind() == "interfaces" {
                    self.collect_type_names(&child, source, &mut interfaces);
                }
            }
        }
        interfaces
    }

    /// Extract extended interfaces from interface declaration
    fn extract_extended_interfaces(&self, interface_node: &Node, source: &str) -> Vec<String> {
        let mut interfaces = Vec::new();
        for i in 0..interface_node.child_count() {
            if let Some(child) = interface_node.child(i) {
                if child.kind() == "extends_interfaces" {
                    self.collect_type_names(&child, source, &mut interfaces);
                }
            }
        }
        interfaces
    }

    /// Collect type names from a node tree
    fn collect_type_names(&self, node: &Node, source: &str, result: &mut Vec<String>) {
        for i in 0..node.child_count() {
            if let Some(child) = node.child(i) {
                match child.kind() {
                    "type_identifier" | "scoped_type_identifier" => {
                        result.push(self.node_text(&child, source));
                    }
                    "type_list" | "interface_type_list" => {
                        self.collect_type_names(&child, source, result);
                    }
                    _ => {}
                }
            }
        }
    }

    /// Check if class has a specific modifier
    fn has_modifier(&self, class_node: &Node, modifier: &str, source: &str) -> bool {
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "modifiers" {
                    for j in 0..child.child_count() {
                        if let Some(mod_node) = child.child(j) {
                            if self.node_text(&mod_node, source) == modifier {
                                return true;
                            }
                        }
                    }
                }
            }
        }
        false
    }

    /// Extract all methods from a class/interface body
    fn extract_methods(&self, class_node: &Node, source: &str) -> Vec<MethodSpec> {
        let mut methods = Vec::new();

        // Find the class body
        for i in 0..class_node.child_count() {
            if let Some(child) = class_node.child(i) {
                if child.kind() == "class_body" || child.kind() == "interface_body" || child.kind() == "enum_body" {
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
                if child.kind() == "method_declaration" {
                    if let Some(method) = self.parse_method(&child, source) {
                        methods.push(method);
                    }
                }
            }
        }
    }

    /// Parse a single method declaration
    fn parse_method(&self, method_node: &Node, source: &str) -> Option<MethodSpec> {
        let mut method_name = None;
        let mut return_type = "void".to_string();
        let mut parameters = Vec::new();
        let mut modifiers = Vec::new();

        for i in 0..method_node.child_count() {
            if let Some(child) = method_node.child(i) {
                match child.kind() {
                    "modifiers" => {
                        modifiers = self.extract_modifiers(&child, source);
                    }
                    "type_identifier" | "void_type" | "primitive_type" | "generic_type" | "array_type" | "scoped_type_identifier" => {
                        return_type = self.node_text(&child, source);
                    }
                    "identifier" => {
                        method_name = Some(self.node_text(&child, source));
                    }
                    "formal_parameters" => {
                        parameters = self.extract_parameters(&child, source);
                    }
                    _ => {}
                }
            }
        }

        let name = method_name?;

        // Build signature
        let param_types: Vec<String> = parameters.iter().map(|p| p.param_type.clone()).collect();
        let signature = format!("{}({})", name, param_types.join(", "));

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

    /// Extract modifiers from a modifiers node
    fn extract_modifiers(&self, modifiers_node: &Node, source: &str) -> Vec<String> {
        let mut modifiers = Vec::new();
        for i in 0..modifiers_node.child_count() {
            if let Some(child) = modifiers_node.child(i) {
                let text = self.node_text(&child, source);
                // Skip annotations
                if !text.starts_with('@') {
                    modifiers.push(text);
                }
            }
        }
        modifiers
    }

    /// Extract parameters from formal_parameters node
    fn extract_parameters(&self, params_node: &Node, source: &str) -> Vec<ParameterSpec> {
        let mut parameters = Vec::new();

        for i in 0..params_node.child_count() {
            if let Some(child) = params_node.child(i) {
                if child.kind() == "formal_parameter" || child.kind() == "spread_parameter" {
                    if let Some(param) = self.parse_parameter(&child, source) {
                        parameters.push(param);
                    }
                }
            }
        }

        parameters
    }

    /// Parse a single parameter
    fn parse_parameter(&self, param_node: &Node, source: &str) -> Option<ParameterSpec> {
        let mut param_type = None;
        let mut param_name = None;
        let mut nullable = false;

        for i in 0..param_node.child_count() {
            if let Some(child) = param_node.child(i) {
                match child.kind() {
                    "type_identifier" | "primitive_type" | "generic_type" | "array_type" | "scoped_type_identifier" => {
                        param_type = Some(self.node_text(&child, source));
                    }
                    "identifier" => {
                        param_name = Some(self.node_text(&child, source));
                    }
                    "modifiers" => {
                        // Check for @Nullable annotation
                        for j in 0..child.child_count() {
                            if let Some(mod_child) = child.child(j) {
                                if mod_child.kind() == "marker_annotation" || mod_child.kind() == "annotation" {
                                    let text = self.node_text(&mod_child, source);
                                    if text.contains("Nullable") {
                                        nullable = true;
                                    }
                                }
                            }
                        }
                    }
                    "spread_parameter" => {
                        // Varargs: type... name
                        param_type = Some(format!("{}...", self.node_text(&child, source)));
                    }
                    _ => {}
                }
            }
        }

        Some(ParameterSpec {
            name: param_name.unwrap_or_else(|| "arg".to_string()),
            param_type: param_type.unwrap_or_else(|| "Object".to_string()),
            nullable,
            default_value: None,
        })
    }

    /// Extract documentation comment before a node
    fn extract_doc_comment(&self, node: &Node, source: &str) -> Option<String> {
        // Look for a preceding comment
        if let Some(prev) = node.prev_sibling() {
            if prev.kind() == "block_comment" {
                let comment = self.node_text(&prev, source);
                if comment.starts_with("/**") {
                    // Clean up the doc comment
                    return Some(self.clean_doc_comment(&comment));
                }
            }
        }
        None
    }

    /// Clean up a doc comment, removing /** */ and * prefixes
    fn clean_doc_comment(&self, comment: &str) -> String {
        comment
            .trim_start_matches("/**")
            .trim_end_matches("*/")
            .lines()
            .map(|line| line.trim().trim_start_matches('*').trim())
            .filter(|line| !line.is_empty())
            .collect::<Vec<_>>()
            .join(" ")
    }

    /// Generate semantic tags for a class
    fn generate_semantic_tags(&self, spec: &ApiSpec) -> Vec<String> {
        let mut tags = Vec::new();

        // Add class type tag
        tags.push(format!("type:{}", spec.class_type));

        // Add package hierarchy tags
        let parts: Vec<&str> = spec.package.split('.').collect();
        if parts.len() >= 2 {
            tags.push(format!("domain:{}", parts[1]));
        }

        // Add parent class tag
        if let Some(ref parent) = spec.parent_class {
            tags.push(format!("extends:{}", parent));
        }

        // Add interface tags
        for iface in &spec.interfaces {
            tags.push(format!("implements:{}", iface));
        }

        // Infer component type from class name
        let class_lower = spec.class_name.to_lowercase();
        if class_lower.contains("activity") {
            tags.push("component:activity".to_string());
        } else if class_lower.contains("fragment") {
            tags.push("component:fragment".to_string());
        } else if class_lower.contains("service") {
            tags.push("component:service".to_string());
        } else if class_lower.contains("receiver") {
            tags.push("component:receiver".to_string());
        } else if class_lower.contains("provider") {
            tags.push("component:provider".to_string());
        } else if class_lower.contains("view") {
            tags.push("component:view".to_string());
        } else if class_lower.contains("adapter") {
            tags.push("component:adapter".to_string());
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

        // Lifecycle method detection
        let lifecycle_methods = [
            "onCreate", "onStart", "onResume", "onPause", "onStop", "onDestroy",
            "onSaveInstanceState", "onRestoreInstanceState", "onAttach", "onDetach",
            "onCreateView", "onDestroyView", "onBind", "onUnbind"
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

    /// Truncate documentation to a reasonable length for tags
    fn truncate_doc(doc: &str) -> String {
        if doc.len() > 100 {
            format!("{}...", &doc[..100])
        } else {
            doc.to_string()
        }
    }
}

impl Default for JavaParser {
    fn default() -> Self {
        Self::new()
    }
}

// JavaParser needs to be thread-safe for rayon
// We'll create a new parser instance per thread
unsafe impl Send for JavaParser {}
unsafe impl Sync for JavaParser {}

impl SdkParser for JavaParser {
    fn parse_file(&self, path: &Path) -> Result<Option<ApiSpec>, CraftError> {
        if !path.extension().map_or(false, |ext| ext == "java") {
            return Ok(None);
        }

        let content = fs::read_to_string(path).map_err(CraftError::Io)?;

        // Create a new parser for this thread
        let mut parser = JavaParser::new();
        parser.parse_content(&content, path)
    }

    fn parse_directory(&self, path: &Path) -> Result<Vec<ApiSpec>, CraftError> {
        info!("Scanning directory: {:?}", path);

        if !path.is_dir() {
            return Err(CraftError::Parse(format!(
                "Path is not a directory: {:?}",
                path
            )));
        }

        // Collect all Java files
        let java_files: Vec<_> = walkdir::WalkDir::new(path)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| {
                e.path().extension().map_or(false, |ext| ext == "java")
                    && !e.path().to_string_lossy().contains("/test/")
                    && !e.path().to_string_lossy().contains("/tests/")
            })
            .map(|e| e.path().to_path_buf())
            .collect();

        info!("Found {} Java files", java_files.len());

        // Parse files in parallel
        let specs: Vec<ApiSpec> = java_files
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

        info!("Successfully parsed {} API specs", specs.len());
        Ok(specs)
    }

    fn platform(&self) -> Platform {
        Platform::Android
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_java_parser_creation() {
        let parser = JavaParser::new();
        assert_eq!(parser.platform(), Platform::Android);
    }

    #[test]
    fn test_parse_simple_class() {
        let mut parser = JavaParser::new();
        let source = r#"
package com.example.app;

/**
 * A simple test class.
 */
public class TestClass extends BaseClass implements Runnable {
    /**
     * Get the name.
     * @return the name
     */
    public String getName() {
        return "test";
    }

    public void setName(String name) {
        this.name = name;
    }

    protected int calculate(int a, int b) {
        return a + b;
    }
}
"#;
        let path = Path::new("TestClass.java");
        let result = parser.parse_content(source, path).unwrap();

        assert!(result.is_some());
        let spec = result.unwrap();

        assert_eq!(spec.package, "com.example.app");
        assert_eq!(spec.class_name, "TestClass");
        assert_eq!(spec.class_type, "class");
        assert_eq!(spec.parent_class, Some("BaseClass".to_string()));
        assert!(spec.interfaces.contains(&"Runnable".to_string()));
        assert_eq!(spec.methods.len(), 3);

        // Check getName method
        let get_name = spec.get_method("getName").unwrap();
        assert_eq!(get_name.return_type, "String");
        assert!(get_name.modifiers.contains(&"public".to_string()));
        assert!(get_name.semantic_tags.contains(&"category:getter".to_string()));

        // Check setName method
        let set_name = spec.get_method("setName").unwrap();
        assert_eq!(set_name.return_type, "void");
        assert_eq!(set_name.parameters.len(), 1);
        assert_eq!(set_name.parameters[0].name, "name");
        assert_eq!(set_name.parameters[0].param_type, "String");
    }

    #[test]
    fn test_parse_interface() {
        let mut parser = JavaParser::new();
        let source = r#"
package com.example.api;

public interface DataProvider extends BaseProvider, Serializable {
    String getData();
    void setData(String data);
}
"#;
        let path = Path::new("DataProvider.java");
        let result = parser.parse_content(source, path).unwrap();

        assert!(result.is_some());
        let spec = result.unwrap();

        assert_eq!(spec.class_name, "DataProvider");
        assert_eq!(spec.class_type, "interface");
        assert!(spec.interfaces.contains(&"BaseProvider".to_string()));
        assert!(spec.interfaces.contains(&"Serializable".to_string()));
        assert_eq!(spec.methods.len(), 2);
    }

    #[test]
    fn test_parse_activity() {
        let mut parser = JavaParser::new();
        let source = r#"
package android.app;

public class Activity extends ContextThemeWrapper {
    protected void onCreate(Bundle savedInstanceState) {
    }

    protected void onStart() {
    }

    protected void onResume() {
    }

    protected void onPause() {
    }

    protected void onStop() {
    }

    protected void onDestroy() {
    }
}
"#;
        let path = Path::new("Activity.java");
        let result = parser.parse_content(source, path).unwrap();

        assert!(result.is_some());
        let spec = result.unwrap();

        assert_eq!(spec.class_name, "Activity");
        assert!(spec.semantic_tags.contains(&"component:activity".to_string()));
        assert_eq!(spec.methods.len(), 6);

        // Check lifecycle methods have correct tags
        let on_create = spec.get_method("onCreate").unwrap();
        assert!(on_create.semantic_tags.contains(&"lifecycle:true".to_string()));
        assert!(on_create.semantic_tags.contains(&"lifecycle:onCreate".to_string()));
    }

    #[test]
    fn test_parse_abstract_class() {
        let mut parser = JavaParser::new();
        let source = r#"
package com.example;

public abstract class AbstractManager {
    public abstract void manage();
    public void init() {}
}
"#;
        let path = Path::new("AbstractManager.java");
        let result = parser.parse_content(source, path).unwrap();

        assert!(result.is_some());
        let spec = result.unwrap();

        assert_eq!(spec.class_type, "abstract_class");
        assert!(spec.semantic_tags.contains(&"component:manager".to_string()));
    }
}
