//! CRAFT Analyzer - Semantic analysis for API mapping
//!
//! This crate provides semantic analysis capabilities:
//! - Similarity scoring between APIs
//! - Automatic mapping rule generation
//! - Semantic tag extraction
//! - Confidence calculation

use craft_core::{ApiReference, ApiSpec, CraftError, MappingRule, MappingType, MethodMapping, Platform};
use rayon::prelude::*;
use std::collections::HashMap;
use tracing::{debug, info};

/// Semantic analyzer for API mapping
pub struct SemanticAnalyzer {
    /// Minimum confidence threshold for automatic mapping
    min_confidence: f64,
}

impl SemanticAnalyzer {
    /// Create a new semantic analyzer
    pub fn new() -> Self {
        Self {
            min_confidence: 0.7,
        }
    }

    /// Set minimum confidence threshold
    pub fn with_min_confidence(mut self, threshold: f64) -> Self {
        self.min_confidence = threshold;
        self
    }

    /// Analyze and generate mappings between source and target APIs
    pub fn analyze(
        &self,
        source_apis: &[ApiSpec],
        target_apis: &[ApiSpec],
    ) -> Result<Vec<MappingRule>, CraftError> {
        info!(
            "Analyzing {} source APIs against {} target APIs",
            source_apis.len(),
            target_apis.len()
        );

        let mappings: Vec<MappingRule> = source_apis
            .par_iter()
            .filter_map(|source| self.find_best_mapping(source, target_apis))
            .collect();

        info!("Generated {} mapping rules", mappings.len());
        Ok(mappings)
    }

    /// Find the best mapping for a source API
    fn find_best_mapping(&self, source: &ApiSpec, targets: &[ApiSpec]) -> Option<MappingRule> {
        let mut best_match: Option<(&ApiSpec, f64)> = None;

        for target in targets {
            let score = self.calculate_similarity(source, target);
            if score >= self.min_confidence {
                if best_match.is_none() || score > best_match.unwrap().1 {
                    best_match = Some((target, score));
                }
            }
        }

        best_match.map(|(target, confidence)| {
            let mut rule = MappingRule::new(
                ApiReference {
                    platform: source.platform,
                    class: source.full_qualified_name.clone(),
                },
                ApiReference {
                    platform: target.platform,
                    class: target.full_qualified_name.clone(),
                },
                self.determine_mapping_type(source, target),
            );
            rule.confidence = confidence;
            rule.method_mappings = self.generate_method_mappings(source, target);
            rule
        })
    }

    /// Calculate similarity score between two APIs
    fn calculate_similarity(&self, source: &ApiSpec, target: &ApiSpec) -> f64 {
        let mut score = 0.0;
        let mut weight_sum = 0.0;

        // Class name similarity (weight: 0.3)
        let name_sim = self.string_similarity(&source.class_name, &target.class_name);
        score += name_sim * 0.3;
        weight_sum += 0.3;

        // Semantic tags overlap (weight: 0.3)
        let tag_sim = self.tag_similarity(&source.semantic_tags, &target.semantic_tags);
        score += tag_sim * 0.3;
        weight_sum += 0.3;

        // Method overlap (weight: 0.4)
        let method_sim = self.method_similarity(&source.methods, &target.methods);
        score += method_sim * 0.4;
        weight_sum += 0.4;

        if weight_sum > 0.0 {
            score / weight_sum
        } else {
            0.0
        }
    }

    /// Calculate string similarity using Levenshtein distance
    fn string_similarity(&self, a: &str, b: &str) -> f64 {
        if a == b {
            return 1.0;
        }
        if a.is_empty() || b.is_empty() {
            return 0.0;
        }

        // Simple similarity based on common substrings
        let a_lower = a.to_lowercase();
        let b_lower = b.to_lowercase();

        if a_lower.contains(&b_lower) || b_lower.contains(&a_lower) {
            return 0.8;
        }

        // Count common characters
        let a_chars: std::collections::HashSet<char> = a_lower.chars().collect();
        let b_chars: std::collections::HashSet<char> = b_lower.chars().collect();
        let common = a_chars.intersection(&b_chars).count();
        let total = a_chars.len().max(b_chars.len());

        common as f64 / total as f64
    }

    /// Calculate tag similarity
    fn tag_similarity(&self, a: &[String], b: &[String]) -> f64 {
        if a.is_empty() && b.is_empty() {
            return 1.0;
        }
        if a.is_empty() || b.is_empty() {
            return 0.0;
        }

        let a_set: std::collections::HashSet<&str> = a.iter().map(|s| s.as_str()).collect();
        let b_set: std::collections::HashSet<&str> = b.iter().map(|s| s.as_str()).collect();
        let common = a_set.intersection(&b_set).count();
        let total = a_set.union(&b_set).count();

        common as f64 / total as f64
    }

    /// Calculate method similarity
    fn method_similarity(
        &self,
        source_methods: &[craft_core::MethodSpec],
        target_methods: &[craft_core::MethodSpec],
    ) -> f64 {
        if source_methods.is_empty() && target_methods.is_empty() {
            return 1.0;
        }
        if source_methods.is_empty() || target_methods.is_empty() {
            return 0.0;
        }

        let mut matched = 0;
        for source in source_methods {
            if target_methods
                .iter()
                .any(|target| self.string_similarity(&source.name, &target.name) > 0.7)
            {
                matched += 1;
            }
        }

        matched as f64 / source_methods.len() as f64
    }

    /// Determine the mapping type based on API comparison
    fn determine_mapping_type(&self, source: &ApiSpec, target: &ApiSpec) -> MappingType {
        let similarity = self.calculate_similarity(source, target);

        if similarity > 0.9 {
            MappingType::Direct
        } else if similarity > 0.7 {
            MappingType::Semantic
        } else {
            MappingType::Bridge
        }
    }

    /// Generate method-level mappings
    fn generate_method_mappings(&self, source: &ApiSpec, target: &ApiSpec) -> Vec<MethodMapping> {
        let mut mappings = Vec::new();

        for source_method in &source.methods {
            // Find best matching target method
            let best_match = target
                .methods
                .iter()
                .max_by(|a, b| {
                    let sim_a = self.string_similarity(&source_method.name, &a.name);
                    let sim_b = self.string_similarity(&source_method.name, &b.name);
                    sim_a.partial_cmp(&sim_b).unwrap_or(std::cmp::Ordering::Equal)
                });

            if let Some(target_method) = best_match {
                if self.string_similarity(&source_method.name, &target_method.name) > 0.5 {
                    mappings.push(MethodMapping {
                        source_method: source_method.name.clone(),
                        target_method: target_method.name.clone(),
                        param_mappings: Vec::new(),
                        pre_call_code: None,
                        post_call_code: None,
                    });
                }
            }
        }

        mappings
    }
}

impl Default for SemanticAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_analyzer_creation() {
        let analyzer = SemanticAnalyzer::new();
        assert_eq!(analyzer.min_confidence, 0.7);
    }

    #[test]
    fn test_string_similarity() {
        let analyzer = SemanticAnalyzer::new();
        assert_eq!(analyzer.string_similarity("Activity", "Activity"), 1.0);
        assert!(analyzer.string_similarity("Activity", "UIAbility") > 0.0);
    }
}
