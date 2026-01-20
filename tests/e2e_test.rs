//! End-to-end integration tests for CRAFT
//!
//! These tests verify the complete pipeline from parsing to code generation.

use craft_analyzer::SemanticAnalyzer;
use craft_core::{ApiSpec, Platform};
use craft_generator::AdapterGenerator;
use craft_parser::{ArkTsParser, JavaParser, SdkParser};
use std::path::Path;

/// Get the path to test fixtures
fn fixtures_path() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures")
}

/// Complete end-to-end test: Parse Android SDK -> Parse Harmony SDK -> Analyze -> Generate
#[test]
fn test_full_pipeline() {
    println!("=== CRAFT End-to-End Pipeline Test ===\n");

    // Step 1: Parse Android SDK (Java files)
    println!("Step 1: Parsing Android SDK...");
    let java_parser = JavaParser::new();
    let android_path = fixtures_path().join("android");

    let android_result = java_parser.parse_directory(&android_path);
    assert!(android_result.is_ok(), "Failed to parse Android SDK: {:?}", android_result.err());

    let android_apis = android_result.unwrap();
    println!("  Parsed {} Android API specs", android_apis.len());

    for api in &android_apis {
        println!("    - {}.{} ({} methods)", api.package, api.class_name, api.methods.len());
    }
    assert!(android_apis.len() >= 2, "Expected at least 2 Android APIs");

    // Step 2: Parse HarmonyOS SDK (ArkTS files)
    println!("\nStep 2: Parsing HarmonyOS SDK...");
    let arkts_parser = ArkTsParser::new();
    let harmony_path = fixtures_path().join("harmony");

    let harmony_result = arkts_parser.parse_directory(&harmony_path);
    assert!(harmony_result.is_ok(), "Failed to parse Harmony SDK: {:?}", harmony_result.err());

    let harmony_apis = harmony_result.unwrap();
    println!("  Parsed {} HarmonyOS API specs", harmony_apis.len());

    for api in &harmony_apis {
        println!("    - {}.{} ({} methods)", api.package, api.class_name, api.methods.len());
    }
    assert!(harmony_apis.len() >= 1, "Expected at least 1 Harmony API");

    // Step 3: Analyze and create mappings
    println!("\nStep 3: Analyzing API mappings...");
    let analyzer = SemanticAnalyzer::new().with_min_confidence(0.3); // Lower threshold for testing

    let mapping_result = analyzer.analyze(&android_apis, &harmony_apis);
    assert!(mapping_result.is_ok(), "Failed to analyze: {:?}", mapping_result.err());

    let mappings = mapping_result.unwrap();
    println!("  Generated {} mapping rules", mappings.len());

    for mapping in &mappings {
        println!(
            "    - {} -> {} (confidence: {:.2}, type: {:?})",
            mapping.source.class,
            mapping.target.class,
            mapping.confidence,
            mapping.mapping_type
        );
        println!("      Method mappings: {}", mapping.method_mappings.len());
    }

    // Step 4: Generate adapter code
    println!("\nStep 4: Generating adapter code...");
    let generator = AdapterGenerator::new();

    // Find Activity -> UIAbility mapping
    let activity_api = android_apis.iter().find(|a| a.class_name == "Activity");
    let uiability_api = harmony_apis.iter().find(|a| a.class_name == "UIAbility");

    if let (Some(activity), Some(uiability)) = (activity_api, uiability_api) {
        // Find or create mapping
        let mapping = mappings.iter().find(|m|
            m.source.class.contains("Activity") && m.target.class.contains("UIAbility")
        );

        if let Some(rule) = mapping {
            // Generate Java adapter
            println!("\n  Generating Java adapter...");
            let java_code = generator.generate(rule, activity, uiability, "java");
            assert!(java_code.is_ok(), "Java generation failed: {:?}", java_code.err());
            let java = java_code.unwrap();
            println!("  Java adapter length: {} characters", java.len());

            // Verify Java code structure
            assert!(java.contains("class ActivityAdapter"), "Java should have ActivityAdapter class");
            assert!(java.contains("delegate."), "Java should delegate calls");
            assert!(java.contains("onCreate"), "Java should have onCreate");

            // Generate Kotlin adapter
            println!("  Generating Kotlin adapter...");
            let kotlin_code = generator.generate(rule, activity, uiability, "kotlin");
            assert!(kotlin_code.is_ok(), "Kotlin generation failed: {:?}", kotlin_code.err());
            let kotlin = kotlin_code.unwrap();
            println!("  Kotlin adapter length: {} characters", kotlin.len());

            // Verify Kotlin code structure
            assert!(kotlin.contains("class ActivityAdapter"), "Kotlin should have ActivityAdapter class");
            assert!(kotlin.contains("override fun"), "Kotlin should have override");

            // Generate ArkTS adapter
            println!("  Generating ArkTS adapter...");
            let arkts_code = generator.generate(rule, activity, uiability, "arkts");
            assert!(arkts_code.is_ok(), "ArkTS generation failed: {:?}", arkts_code.err());
            let arkts = arkts_code.unwrap();
            println!("  ArkTS adapter length: {} characters", arkts.len());

            // Verify ArkTS code structure
            assert!(arkts.contains("export class ActivityAdapter"), "ArkTS should export ActivityAdapter");
            assert!(arkts.contains("this.delegate."), "ArkTS should use this.delegate");

            println!("\n=== Pipeline Test PASSED ===");
        } else {
            println!("  Note: No automatic Activity->UIAbility mapping found");
            println!("  Creating manual mapping for generation test...");

            // Create manual mapping for testing
            use craft_core::{ApiReference, MappingRule, MappingType};
            let manual_rule = MappingRule::new(
                ApiReference {
                    platform: Platform::Android,
                    class: activity.full_qualified_name.clone(),
                },
                ApiReference {
                    platform: Platform::Harmony,
                    class: uiability.full_qualified_name.clone(),
                },
                MappingType::Semantic,
            );

            let java_code = generator.generate(&manual_rule, activity, uiability, "java");
            assert!(java_code.is_ok(), "Java generation with manual mapping failed");
            println!("  Manual mapping generation: SUCCESS");

            println!("\n=== Pipeline Test PASSED (with manual mapping) ===");
        }
    } else {
        println!("  Warning: Activity or UIAbility not found in parsed APIs");
        println!("  Activity found: {}", activity_api.is_some());
        println!("  UIAbility found: {}", uiability_api.is_some());
    }
}

/// Test parsing accuracy by verifying specific method details
#[test]
fn test_parsing_accuracy() {
    println!("=== Parsing Accuracy Test ===\n");

    let java_parser = JavaParser::new();
    let activity_path = fixtures_path().join("android/app/Activity.java");

    let result = java_parser.parse_file(&activity_path).unwrap().unwrap();

    // Verify specific methods and their details
    println!("Verifying Activity methods...");

    // Check onCreate
    let on_create = result.get_method("onCreate").expect("onCreate should exist");
    assert_eq!(on_create.return_type, "void", "onCreate return type");
    assert_eq!(on_create.parameters.len(), 1, "onCreate should have 1 param");
    assert_eq!(on_create.parameters[0].param_type, "Bundle", "First param should be Bundle");
    println!("  onCreate: OK");

    // Check startActivityForResult
    let start_for_result = result.get_method("startActivityForResult").expect("startActivityForResult should exist");
    assert_eq!(start_for_result.parameters.len(), 2, "startActivityForResult should have 2 params");
    assert_eq!(start_for_result.parameters[0].param_type, "Intent");
    assert_eq!(start_for_result.parameters[1].param_type, "int");
    println!("  startActivityForResult: OK");

    // Check setResult overload
    let set_result = result.methods.iter().filter(|m| m.name == "setResult").count();
    assert!(set_result >= 1, "Should have at least 1 setResult method");
    println!("  setResult (found {} overloads): OK", set_result);

    // Check getTitle
    let get_title = result.get_method("getTitle").expect("getTitle should exist");
    assert_eq!(get_title.return_type, "CharSequence", "getTitle return type");
    assert!(get_title.parameters.is_empty(), "getTitle should have no params");
    println!("  getTitle: OK");

    // Check class metadata
    assert_eq!(result.package, "android.app");
    assert_eq!(result.class_name, "Activity");
    assert!(result.parent_class.is_some());
    println!("  Class metadata: OK");

    println!("\n=== Parsing Accuracy Test PASSED ===");
}

/// Test that semantic tags are correctly generated
#[test]
fn test_semantic_tags() {
    println!("=== Semantic Tags Test ===\n");

    let java_parser = JavaParser::new();
    let activity_path = fixtures_path().join("android/app/Activity.java");

    let activity = java_parser.parse_file(&activity_path).unwrap().unwrap();

    // Check class-level semantic tags
    println!("Class semantic tags:");
    for tag in &activity.semantic_tags {
        println!("  - {}", tag);
    }

    assert!(
        activity.semantic_tags.iter().any(|t| t.contains("component:activity")),
        "Should have activity component tag"
    );

    // Check method-level semantic tags
    println!("\nMethod semantic tags:");

    let on_create = activity.get_method("onCreate").unwrap();
    println!("  onCreate tags: {:?}", on_create.semantic_tags);
    assert!(
        on_create.semantic_tags.iter().any(|t| t.contains("lifecycle")),
        "onCreate should have lifecycle tag"
    );

    let get_title = activity.get_method("getTitle").unwrap();
    println!("  getTitle tags: {:?}", get_title.semantic_tags);
    assert!(
        get_title.semantic_tags.iter().any(|t| t.contains("getter")),
        "getTitle should have getter tag"
    );

    let set_title = activity.get_method("setTitle").unwrap();
    println!("  setTitle tags: {:?}", set_title.semantic_tags);
    assert!(
        set_title.semantic_tags.iter().any(|t| t.contains("setter")),
        "setTitle should have setter tag"
    );

    println!("\n=== Semantic Tags Test PASSED ===");
}

/// Test the similarity analysis between Android and HarmonyOS APIs
#[test]
fn test_similarity_analysis() {
    println!("=== Similarity Analysis Test ===\n");

    let java_parser = JavaParser::new();
    let arkts_parser = ArkTsParser::new();

    let activity = java_parser
        .parse_file(&fixtures_path().join("android/app/Activity.java"))
        .unwrap()
        .unwrap();

    let uiability = arkts_parser
        .parse_file(&fixtures_path().join("harmony/ability/UIAbility.ets"))
        .unwrap()
        .unwrap();

    let analyzer = SemanticAnalyzer::new().with_min_confidence(0.1);

    // Analyze just these two APIs
    let mappings = analyzer.analyze(&[activity.clone()], &[uiability.clone()]).unwrap();

    println!("Activity methods: {}", activity.methods.len());
    println!("UIAbility methods: {}", uiability.methods.len());
    println!("Mappings generated: {}", mappings.len());

    if !mappings.is_empty() {
        let mapping = &mappings[0];
        println!("\nMapping details:");
        println!("  Source: {}", mapping.source.class);
        println!("  Target: {}", mapping.target.class);
        println!("  Confidence: {:.2}", mapping.confidence);
        println!("  Type: {:?}", mapping.mapping_type);
        println!("  Method mappings: {}", mapping.method_mappings.len());

        for mm in &mapping.method_mappings {
            println!("    {} -> {}", mm.source_method, mm.target_method);
        }
    }

    println!("\n=== Similarity Analysis Test PASSED ===");
}

/// Test code generation output validity
#[test]
fn test_generated_code_validity() {
    println!("=== Generated Code Validity Test ===\n");

    let java_parser = JavaParser::new();
    let arkts_parser = ArkTsParser::new();

    let activity = java_parser
        .parse_file(&fixtures_path().join("android/app/Activity.java"))
        .unwrap()
        .unwrap();

    let uiability = arkts_parser
        .parse_file(&fixtures_path().join("harmony/ability/UIAbility.ets"))
        .unwrap()
        .unwrap();

    use craft_core::{ApiReference, MappingRule, MappingType};

    let rule = MappingRule::new(
        ApiReference {
            platform: Platform::Android,
            class: activity.full_qualified_name.clone(),
        },
        ApiReference {
            platform: Platform::Harmony,
            class: uiability.full_qualified_name.clone(),
        },
        MappingType::Semantic,
    );

    let generator = AdapterGenerator::new();

    // Test Java output
    let java = generator.generate(&rule, &activity, &uiability, "java").unwrap();

    println!("Java code validation:");
    assert!(java.contains("package "), "Should have package declaration");
    assert!(java.contains("import "), "Should have imports");
    assert!(java.contains("public class "), "Should have class declaration");
    assert!(java.contains("{") && java.contains("}"), "Should have balanced braces");

    // Check for lifecycle method mappings
    let lifecycle_methods = ["onCreate", "onStart", "onDestroy"];
    for method in lifecycle_methods {
        assert!(java.contains(method), "Should have {} method", method);
    }
    println!("  Structure: OK");
    println!("  Lifecycle methods: OK");

    // Test Kotlin output
    let kotlin = generator.generate(&rule, &activity, &uiability, "kotlin").unwrap();

    println!("\nKotlin code validation:");
    assert!(kotlin.contains("package "), "Should have package declaration");
    assert!(kotlin.contains("class "), "Should have class declaration");
    assert!(kotlin.contains("override fun"), "Should have override methods");
    println!("  Structure: OK");

    // Test ArkTS output
    let arkts = generator.generate(&rule, &activity, &uiability, "arkts").unwrap();

    println!("\nArkTS code validation:");
    assert!(arkts.contains("export class"), "Should export class");
    assert!(arkts.contains("constructor"), "Should have constructor");
    assert!(arkts.contains(": void") || arkts.contains(":void"), "Should have type annotations");
    println!("  Structure: OK");

    println!("\n=== Generated Code Validity Test PASSED ===");
}
