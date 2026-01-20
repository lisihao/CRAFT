//! Integration tests for craft-parser
//!
//! These tests verify that the Java and ArkTS parsers work correctly
//! with real-world source files.

use craft_core::Platform;
use craft_parser::{JavaParser, ArkTsParser, SdkParser};
use std::path::Path;

/// Test parsing a complete Activity class
#[test]
fn test_parse_activity_class() {
    let parser = JavaParser::new();
    let fixture_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("tests/fixtures/android/app/Activity.java");

    println!("Parsing: {:?}", fixture_path);

    let result = parser.parse_file(&fixture_path);
    assert!(result.is_ok(), "Failed to parse Activity.java: {:?}", result.err());

    let spec = result.unwrap();
    assert!(spec.is_some(), "Expected ApiSpec but got None");

    let api = spec.unwrap();

    // Verify basic class info
    assert_eq!(api.package, "android.app", "Package should be android.app");
    assert_eq!(api.class_name, "Activity", "Class name should be Activity");
    assert_eq!(api.class_type, "class", "Should be a class");
    assert_eq!(api.parent_class, Some("ContextThemeWrapper".to_string()), "Should extend ContextThemeWrapper");
    assert!(api.interfaces.contains(&"Window.Callback".to_string()), "Should implement Window.Callback");

    // Verify methods were extracted
    println!("Found {} methods", api.methods.len());
    assert!(api.methods.len() >= 10, "Expected at least 10 methods, found {}", api.methods.len());

    // Verify lifecycle methods
    let lifecycle_methods = ["onCreate", "onStart", "onResume", "onPause", "onStop", "onDestroy"];
    for method_name in lifecycle_methods {
        let method = api.get_method(method_name);
        assert!(method.is_some(), "Method {} should exist", method_name);

        let m = method.unwrap();
        println!("  {} - params: {}, return: {}", m.name, m.parameters.len(), m.return_type);

        // Verify lifecycle tags
        assert!(
            m.semantic_tags.iter().any(|t| t.contains("lifecycle")),
            "Method {} should have lifecycle tag",
            method_name
        );
    }

    // Verify onCreate has Bundle parameter
    let on_create = api.get_method("onCreate").unwrap();
    assert_eq!(on_create.parameters.len(), 1, "onCreate should have 1 parameter");
    assert_eq!(on_create.parameters[0].name, "savedInstanceState");
    assert_eq!(on_create.parameters[0].param_type, "Bundle");

    // Verify regular methods
    let get_title = api.get_method("getTitle");
    assert!(get_title.is_some(), "getTitle should exist");
    let gt = get_title.unwrap();
    assert_eq!(gt.return_type, "CharSequence");
    assert!(gt.modifiers.contains(&"public".to_string()));

    let set_title = api.get_method("setTitle");
    assert!(set_title.is_some(), "setTitle should exist");
    let st = set_title.unwrap();
    assert_eq!(st.parameters.len(), 1);
    assert_eq!(st.parameters[0].param_type, "CharSequence");

    // Verify semantic tags on class
    assert!(
        api.semantic_tags.iter().any(|t| t.contains("component:activity")),
        "Should have activity component tag"
    );

    println!("Activity.java parsing test passed!");
}

/// Test parsing a Fragment class
#[test]
fn test_parse_fragment_class() {
    let parser = JavaParser::new();
    let fixture_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("tests/fixtures/android/app/Fragment.java");

    println!("Parsing: {:?}", fixture_path);

    let result = parser.parse_file(&fixture_path);
    assert!(result.is_ok(), "Failed to parse Fragment.java: {:?}", result.err());

    let spec = result.unwrap();
    assert!(spec.is_some(), "Expected ApiSpec but got None");

    let api = spec.unwrap();

    // Verify basic class info
    assert_eq!(api.package, "android.app");
    assert_eq!(api.class_name, "Fragment");
    assert_eq!(api.class_type, "class");

    // Verify fragment lifecycle methods
    let fragment_lifecycle = ["onAttach", "onCreate", "onCreateView", "onResume", "onPause", "onDestroyView", "onDestroy", "onDetach"];
    for method_name in fragment_lifecycle {
        assert!(
            api.get_method(method_name).is_some(),
            "Fragment should have {} method",
            method_name
        );
    }

    // Verify onCreateView has correct parameters
    let on_create_view = api.get_method("onCreateView").unwrap();
    assert_eq!(on_create_view.parameters.len(), 3, "onCreateView should have 3 parameters");
    assert_eq!(on_create_view.return_type, "View");

    // Verify semantic tags
    assert!(
        api.semantic_tags.iter().any(|t| t.contains("component:fragment")),
        "Should have fragment component tag"
    );

    println!("Fragment.java parsing test passed!");
}

/// Test parsing a UIAbility class (ArkTS)
#[test]
fn test_parse_uiability_arkts() {
    let parser = ArkTsParser::new();
    let fixture_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("tests/fixtures/harmony/ability/UIAbility.ets");

    println!("Parsing: {:?}", fixture_path);

    let result = parser.parse_file(&fixture_path);
    assert!(result.is_ok(), "Failed to parse UIAbility.ets: {:?}", result.err());

    let spec = result.unwrap();
    assert!(spec.is_some(), "Expected ApiSpec but got None");

    let api = spec.unwrap();

    // Verify basic class info
    assert_eq!(api.class_name, "UIAbility", "Class name should be UIAbility");
    assert_eq!(api.class_type, "class", "Should be a class");
    assert_eq!(api.platform, Platform::Harmony);

    // Verify HarmonyOS lifecycle methods
    let harmony_lifecycle = ["onCreate", "onDestroy", "onWindowStageCreate", "onWindowStageDestroy", "onForeground", "onBackground"];
    for method_name in harmony_lifecycle {
        let method = api.get_method(method_name);
        assert!(method.is_some(), "UIAbility should have {} method", method_name);

        let m = method.unwrap();
        println!("  {} - params: {}, return: {}", m.name, m.parameters.len(), m.return_type);
    }

    // Verify onCreate has Want parameter
    let on_create = api.get_method("onCreate").unwrap();
    assert_eq!(on_create.parameters.len(), 2, "onCreate should have 2 parameters");
    assert_eq!(on_create.parameters[0].name, "want");
    assert_eq!(on_create.parameters[0].param_type, "Want");

    // Verify other methods
    let terminate_self = api.get_method("terminateSelf");
    assert!(terminate_self.is_some(), "terminateSelf should exist");
    let ts = terminate_self.unwrap();
    assert!(ts.return_type.contains("Promise"), "terminateSelf should return Promise");

    // Verify semantic tags
    assert!(
        api.semantic_tags.iter().any(|t| t.contains("uiability")),
        "Should have UIAbility component tag"
    );

    println!("UIAbility.ets parsing test passed!");
}

/// Test parsing a directory of Java files
#[test]
fn test_parse_android_directory() {
    let parser = JavaParser::new();
    let fixture_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("tests/fixtures/android");

    println!("Parsing directory: {:?}", fixture_path);

    let result = parser.parse_directory(&fixture_path);
    assert!(result.is_ok(), "Failed to parse directory: {:?}", result.err());

    let specs = result.unwrap();
    println!("Parsed {} API specs", specs.len());

    assert!(specs.len() >= 2, "Expected at least 2 specs (Activity, Fragment), found {}", specs.len());

    // Verify both classes were parsed
    let class_names: Vec<&str> = specs.iter().map(|s| s.class_name.as_str()).collect();
    assert!(class_names.contains(&"Activity"), "Should contain Activity");
    assert!(class_names.contains(&"Fragment"), "Should contain Fragment");

    println!("Android directory parsing test passed!");
}

/// Test parsing a directory of ArkTS files
#[test]
fn test_parse_harmony_directory() {
    let parser = ArkTsParser::new();
    let fixture_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("tests/fixtures/harmony");

    println!("Parsing directory: {:?}", fixture_path);

    let result = parser.parse_directory(&fixture_path);
    assert!(result.is_ok(), "Failed to parse directory: {:?}", result.err());

    let specs = result.unwrap();
    println!("Parsed {} API specs", specs.len());

    assert!(specs.len() >= 1, "Expected at least 1 spec (UIAbility), found {}", specs.len());

    // Verify UIAbility was parsed
    let class_names: Vec<&str> = specs.iter().map(|s| s.class_name.as_str()).collect();
    assert!(class_names.contains(&"UIAbility"), "Should contain UIAbility");

    println!("Harmony directory parsing test passed!");
}

/// Test that parser correctly extracts method documentation
#[test]
fn test_parse_documentation() {
    let parser = JavaParser::new();
    let fixture_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("tests/fixtures/android/app/Activity.java");

    let result = parser.parse_file(&fixture_path).unwrap().unwrap();

    // Check that onCreate has documentation
    let on_create = result.get_method("onCreate").unwrap();
    assert!(
        on_create.doc_comment.is_some(),
        "onCreate should have documentation"
    );

    let doc = on_create.doc_comment.as_ref().unwrap();
    assert!(
        doc.contains("activity is starting"),
        "Documentation should mention activity starting"
    );

    println!("Documentation extraction test passed!");
}

/// Test that parser handles edge cases
#[test]
fn test_parser_edge_cases() {
    let parser = JavaParser::new();

    // Test parsing non-existent file
    let result = parser.parse_file(Path::new("/non/existent/file.java"));
    assert!(result.is_err(), "Should fail on non-existent file");

    // Test parsing non-Java file
    let result = parser.parse_file(Path::new("/some/file.txt"));
    assert!(result.unwrap().is_none(), "Should return None for non-Java file");

    println!("Edge cases test passed!");
}
