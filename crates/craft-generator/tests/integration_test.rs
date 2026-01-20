//! Integration tests for craft-generator
//!
//! These tests verify that the code generator produces correct,
//! compilable adapter code with proper method implementations.

use craft_core::{ApiReference, ApiSpec, MappingRule, MappingType, MethodSpec, ParameterSpec, Platform};
use craft_generator::{AdapterGenerator, LifecycleMapping};

/// Create a realistic Activity ApiSpec for testing
fn create_activity_spec() -> ApiSpec {
    let mut spec = ApiSpec::new(Platform::Android, "android.app", "Activity");
    spec.class_type = "class".to_string();
    spec.parent_class = Some("ContextThemeWrapper".to_string());
    spec.interfaces = vec!["Window.Callback".to_string()];

    spec.methods = vec![
        MethodSpec {
            name: "onCreate".to_string(),
            signature: "onCreate(Bundle)".to_string(),
            return_type: "void".to_string(),
            parameters: vec![ParameterSpec {
                name: "savedInstanceState".to_string(),
                param_type: "Bundle".to_string(),
                nullable: true,
                default_value: None,
            }],
            modifiers: vec!["protected".to_string()],
            semantic_tags: vec!["lifecycle:onCreate".to_string()],
            doc_comment: Some("Called when the activity is starting.".to_string()),
        },
        MethodSpec {
            name: "onStart".to_string(),
            signature: "onStart()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["protected".to_string()],
            semantic_tags: vec!["lifecycle:onStart".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "onResume".to_string(),
            signature: "onResume()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["protected".to_string()],
            semantic_tags: vec!["lifecycle:onResume".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "onPause".to_string(),
            signature: "onPause()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["protected".to_string()],
            semantic_tags: vec!["lifecycle:onPause".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "onStop".to_string(),
            signature: "onStop()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["protected".to_string()],
            semantic_tags: vec!["lifecycle:onStop".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "onDestroy".to_string(),
            signature: "onDestroy()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["protected".to_string()],
            semantic_tags: vec!["lifecycle:onDestroy".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "getTitle".to_string(),
            signature: "getTitle()".to_string(),
            return_type: "CharSequence".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec!["category:getter".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "setTitle".to_string(),
            signature: "setTitle(CharSequence)".to_string(),
            return_type: "void".to_string(),
            parameters: vec![ParameterSpec {
                name: "title".to_string(),
                param_type: "CharSequence".to_string(),
                nullable: false,
                default_value: None,
            }],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec!["category:setter".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "finish".to_string(),
            signature: "finish()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
        MethodSpec {
            name: "startActivity".to_string(),
            signature: "startActivity(Intent)".to_string(),
            return_type: "void".to_string(),
            parameters: vec![ParameterSpec {
                name: "intent".to_string(),
                param_type: "Intent".to_string(),
                nullable: false,
                default_value: None,
            }],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
    ];

    spec
}

/// Create a realistic UIAbility ApiSpec for testing
fn create_uiability_spec() -> ApiSpec {
    let mut spec = ApiSpec::new(Platform::Harmony, "ohos.app.ability", "UIAbility");
    spec.class_type = "class".to_string();

    spec.methods = vec![
        MethodSpec {
            name: "onCreate".to_string(),
            signature: "onCreate(Want, AbilityConstant.LaunchParam)".to_string(),
            return_type: "void".to_string(),
            parameters: vec![
                ParameterSpec {
                    name: "want".to_string(),
                    param_type: "Want".to_string(),
                    nullable: false,
                    default_value: None,
                },
                ParameterSpec {
                    name: "launchParam".to_string(),
                    param_type: "AbilityConstant.LaunchParam".to_string(),
                    nullable: false,
                    default_value: None,
                },
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
            name: "onForeground".to_string(),
            signature: "onForeground()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec!["lifecycle:onForeground".to_string()],
            doc_comment: None,
        },
        MethodSpec {
            name: "onBackground".to_string(),
            signature: "onBackground()".to_string(),
            return_type: "void".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec!["lifecycle:onBackground".to_string()],
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
        MethodSpec {
            name: "setTitle".to_string(),
            signature: "setTitle(string)".to_string(),
            return_type: "void".to_string(),
            parameters: vec![ParameterSpec {
                name: "title".to_string(),
                param_type: "string".to_string(),
                nullable: false,
                default_value: None,
            }],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
        MethodSpec {
            name: "terminateSelf".to_string(),
            signature: "terminateSelf()".to_string(),
            return_type: "Promise<void>".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
        MethodSpec {
            name: "startAbility".to_string(),
            signature: "startAbility(Want)".to_string(),
            return_type: "Promise<void>".to_string(),
            parameters: vec![ParameterSpec {
                name: "want".to_string(),
                param_type: "Want".to_string(),
                nullable: false,
                default_value: None,
            }],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
    ];

    spec
}

fn create_mapping_rule() -> MappingRule {
    let mut rule = MappingRule::new(
        ApiReference {
            platform: Platform::Android,
            class: "android.app.Activity".to_string(),
        },
        ApiReference {
            platform: Platform::Harmony,
            class: "ohos.app.ability.UIAbility".to_string(),
        },
        MappingType::Semantic,
    );
    rule.confidence = 0.85;
    rule
}

/// Test Java adapter generation
#[test]
fn test_generate_java_adapter() {
    let generator = AdapterGenerator::new();
    let source = create_activity_spec();
    let target = create_uiability_spec();
    let rule = create_mapping_rule();

    let result = generator.generate(&rule, &source, &target, "java");
    assert!(result.is_ok(), "Java generation should succeed: {:?}", result.err());

    let code = result.unwrap();
    println!("Generated Java code:\n{}", code);

    // Verify class structure
    assert!(code.contains("package craft.adapters.android.app;"), "Should have correct package");
    assert!(code.contains("public class ActivityAdapter extends Activity"), "Should extend Activity");
    assert!(code.contains("private final UIAbility delegate"), "Should have delegate field");
    assert!(code.contains("public ActivityAdapter(UIAbility delegate)"), "Should have constructor");

    // Verify lifecycle method mappings
    assert!(code.contains("onCreate") && code.contains("delegate.onCreate"), "onCreate should delegate");
    assert!(code.contains("onDestroy") && code.contains("delegate.onDestroy"), "onDestroy should delegate");

    // Verify onStart/onResume map to onForeground
    assert!(
        code.contains("onForeground"),
        "Should map to onForeground"
    );

    // Verify onPause/onStop map to onBackground
    assert!(
        code.contains("onBackground"),
        "Should map to onBackground"
    );

    // Verify regular method delegation
    assert!(code.contains("public CharSequence getTitle()"), "Should have getTitle method");
    assert!(code.contains("delegate.getTitle()"), "getTitle should delegate");

    // Verify documentation
    assert!(code.contains("Auto-generated by CRAFT"), "Should have generation header");
    assert!(code.contains("Lifecycle adapter:"), "Should have lifecycle documentation");

    println!("Java adapter generation test passed!");
}

/// Test Kotlin adapter generation
#[test]
fn test_generate_kotlin_adapter() {
    let generator = AdapterGenerator::new();
    let source = create_activity_spec();
    let target = create_uiability_spec();
    let rule = create_mapping_rule();

    let result = generator.generate(&rule, &source, &target, "kotlin");
    assert!(result.is_ok(), "Kotlin generation should succeed: {:?}", result.err());

    let code = result.unwrap();
    println!("Generated Kotlin code:\n{}", code);

    // Verify Kotlin syntax
    assert!(code.contains("package craft.adapters.android.app"), "Should have correct package");
    assert!(code.contains("class ActivityAdapter("), "Should be a class");
    assert!(code.contains("private val delegate: UIAbility"), "Should have delegate");
    assert!(code.contains(") : Activity()"), "Should extend Activity");

    // Verify method syntax
    assert!(code.contains("override fun onCreate"), "Should have override");
    assert!(code.contains("delegate."), "Should delegate calls");

    // Verify Kotlin type conversions
    assert!(!code.contains("void"), "Should not have Java void type");

    println!("Kotlin adapter generation test passed!");
}

/// Test ArkTS adapter generation
#[test]
fn test_generate_arkts_adapter() {
    let generator = AdapterGenerator::new();
    let source = create_activity_spec();
    let target = create_uiability_spec();
    let rule = create_mapping_rule();

    let result = generator.generate(&rule, &source, &target, "arkts");
    assert!(result.is_ok(), "ArkTS generation should succeed: {:?}", result.err());

    let code = result.unwrap();
    println!("Generated ArkTS code:\n{}", code);

    // Verify ArkTS/TypeScript syntax
    assert!(code.contains("export class ActivityAdapter"), "Should export class");
    assert!(code.contains("private delegate: UIAbility"), "Should have delegate");
    assert!(code.contains("constructor(delegate: UIAbility)"), "Should have constructor");

    // Verify TypeScript type annotations
    assert!(code.contains("): void"), "Should have void return type annotation");
    assert!(code.contains("this.delegate."), "Should use this.delegate");

    // Verify import statement
    assert!(code.contains("import {"), "Should have import statement");

    println!("ArkTS adapter generation test passed!");
}

/// Test lifecycle mapping correctness
#[test]
fn test_lifecycle_mapping() {
    let mapping = LifecycleMapping::activity_to_uiability();

    // Test Activity lifecycle mappings
    let mappings = [
        ("onCreate", "onCreate"),
        ("onStart", "onForeground"),
        ("onResume", "onForeground"),
        ("onPause", "onBackground"),
        ("onStop", "onBackground"),
        ("onDestroy", "onDestroy"),
    ];

    for (source, expected_target) in mappings {
        let target = mapping.get_target(source);
        assert!(target.is_some(), "{} should have a mapping", source);
        assert_eq!(
            target.unwrap().method,
            expected_target,
            "{} should map to {}",
            source,
            expected_target
        );
    }

    // Test Fragment lifecycle mappings
    let fragment_mappings = [
        ("onAttach", "aboutToAppear"),
        ("onDetach", "aboutToDisappear"),
        ("onCreateView", "build"),
    ];

    for (source, expected_target) in fragment_mappings {
        let target = mapping.get_target(source);
        assert!(target.is_some(), "{} should have a mapping", source);
        assert_eq!(
            target.unwrap().method,
            expected_target,
            "{} should map to {}",
            source,
            expected_target
        );
    }

    // Test non-lifecycle method
    assert!(
        mapping.get_target("getTitle").is_none(),
        "getTitle should not be a lifecycle method"
    );

    println!("Lifecycle mapping test passed!");
}

/// Test that generated Java code has all necessary imports
#[test]
fn test_generated_imports() {
    let generator = AdapterGenerator::new();
    let source = create_activity_spec();
    let target = create_uiability_spec();
    let rule = create_mapping_rule();

    let code = generator.generate(&rule, &source, &target, "java").unwrap();

    assert!(code.contains("import android.app.Activity;"), "Should import source class");
    assert!(code.contains("import ohos.app.ability.UIAbility;"), "Should import target class");

    println!("Import generation test passed!");
}

/// Test that generator handles edge cases
#[test]
fn test_generator_edge_cases() {
    let generator = AdapterGenerator::new();

    // Test with empty methods
    let mut source = ApiSpec::new(Platform::Android, "com.example", "EmptyClass");
    source.methods = vec![];

    let mut target = ApiSpec::new(Platform::Harmony, "ohos.example", "TargetClass");
    target.methods = vec![];

    let rule = MappingRule::new(
        ApiReference {
            platform: Platform::Android,
            class: "com.example.EmptyClass".to_string(),
        },
        ApiReference {
            platform: Platform::Harmony,
            class: "ohos.example.TargetClass".to_string(),
        },
        MappingType::Direct,
    );

    // Should not fail even with empty methods
    let result = generator.generate(&rule, &source, &target, "java");
    assert!(result.is_ok(), "Should handle empty methods");

    // Test unsupported format
    let result = generator.generate(&rule, &source, &target, "unknown");
    assert!(result.is_err(), "Should fail for unsupported format");

    println!("Edge cases test passed!");
}

/// Test type conversion between Java and TypeScript
#[test]
fn test_type_conversion() {
    let generator = AdapterGenerator::new();

    // Create specs with various types
    let mut source = ApiSpec::new(Platform::Android, "android.test", "TypeTest");
    source.methods = vec![
        MethodSpec {
            name: "getNumber".to_string(),
            signature: "getNumber()".to_string(),
            return_type: "int".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
        MethodSpec {
            name: "getText".to_string(),
            signature: "getText()".to_string(),
            return_type: "String".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
        MethodSpec {
            name: "isEnabled".to_string(),
            signature: "isEnabled()".to_string(),
            return_type: "boolean".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
    ];

    let mut target = ApiSpec::new(Platform::Harmony, "ohos.test", "TypeTest");
    target.methods = vec![
        MethodSpec {
            name: "getNumber".to_string(),
            signature: "getNumber()".to_string(),
            return_type: "number".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
        MethodSpec {
            name: "getText".to_string(),
            signature: "getText()".to_string(),
            return_type: "string".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
        MethodSpec {
            name: "isEnabled".to_string(),
            signature: "isEnabled()".to_string(),
            return_type: "boolean".to_string(),
            parameters: vec![],
            modifiers: vec!["public".to_string()],
            semantic_tags: vec![],
            doc_comment: None,
        },
    ];

    let rule = MappingRule::new(
        ApiReference {
            platform: Platform::Android,
            class: "android.test.TypeTest".to_string(),
        },
        ApiReference {
            platform: Platform::Harmony,
            class: "ohos.test.TypeTest".to_string(),
        },
        MappingType::Direct,
    );

    // Generate ArkTS code and verify type conversion
    let code = generator.generate(&rule, &source, &target, "arkts").unwrap();

    // In ArkTS output, Java int should become number
    assert!(code.contains("): number") || code.contains(": number"), "int should convert to number in ArkTS");
    assert!(code.contains("): string") || code.contains(": string"), "String should convert to string in ArkTS");
    assert!(code.contains("): boolean") || code.contains(": boolean"), "boolean should stay boolean in ArkTS");

    println!("Type conversion test passed!");
}
