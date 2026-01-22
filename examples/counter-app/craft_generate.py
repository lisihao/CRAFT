#!/usr/bin/env python3
"""
CRAFT Framework - Counter App Adapter Generator

This script parses the Android Counter app and generates:
1. Adapter layer (compatibility bridge)
2. HarmonyOS UIAbility implementation
3. ArkUI component for the UI
"""

import os
import re
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class MethodInfo:
    name: str
    return_type: str
    parameters: List[Tuple[str, str]]  # [(type, name), ...]
    is_lifecycle: bool = False
    body: str = ""

@dataclass
class ClassInfo:
    package: str
    name: str
    parent: Optional[str]
    methods: List[MethodInfo] = field(default_factory=list)
    fields: List[Tuple[str, str, str]] = field(default_factory=list)  # [(modifier, type, name), ...]

# ============================================================================
# Java Parser
# ============================================================================

class JavaParser:
    """Parse Java source files to extract class information."""

    def __init__(self):
        self.lifecycle_methods = {
            'onCreate', 'onStart', 'onResume', 'onPause',
            'onStop', 'onDestroy', 'onSaveInstanceState', 'onRestoreInstanceState'
        }

    def parse_file(self, filepath: str) -> ClassInfo:
        """Parse a Java file and extract class information."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract package
        package_match = re.search(r'package\s+([\w.]+);', content)
        package = package_match.group(1) if package_match else ""

        # Extract class declaration
        class_match = re.search(
            r'public\s+class\s+(\w+)(?:\s+extends\s+(\w+))?',
            content
        )
        class_name = class_match.group(1) if class_match else "Unknown"
        parent_class = class_match.group(2) if class_match and class_match.group(2) else None

        # Extract fields
        fields = self._extract_fields(content)

        # Extract methods
        methods = self._extract_methods(content)

        return ClassInfo(
            package=package,
            name=class_name,
            parent=parent_class,
            methods=methods,
            fields=fields
        )

    def _extract_fields(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract field declarations."""
        fields = []
        field_pattern = r'(private|protected|public)\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[\w<>,\s]+>)?)\s+(\w+)\s*[;=]'
        for match in re.finditer(field_pattern, content):
            fields.append((match.group(1), match.group(2), match.group(3)))
        return fields

    def _extract_methods(self, content: str) -> List[MethodInfo]:
        """Extract method declarations with their bodies."""
        methods = []

        # Pattern to match method declarations
        method_pattern = r'(?:@\w+\s+)*(?:public|protected|private)\s+(?:static\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'

        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3).strip()

            # Parse parameters
            parameters = []
            if params_str:
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        parts = param.rsplit(' ', 1)
                        if len(parts) == 2:
                            parameters.append((parts[0], parts[1]))

            # Extract method body (find matching braces)
            start_pos = match.end() - 1
            body = self._extract_body(content, start_pos)

            methods.append(MethodInfo(
                name=method_name,
                return_type=return_type,
                parameters=parameters,
                is_lifecycle=method_name in self.lifecycle_methods,
                body=body
            ))

        return methods

    def _extract_body(self, content: str, start_pos: int) -> str:
        """Extract method body by matching braces."""
        brace_count = 0
        body_start = start_pos + 1
        i = start_pos

        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[body_start:i].strip()
            i += 1

        return ""

# ============================================================================
# Lifecycle Mapping
# ============================================================================

LIFECYCLE_MAPPING = {
    'onCreate': {
        'target': 'onCreate',
        'param_transform': 'want: Want, launchParam: AbilityConstant.LaunchParam',
        'note': 'Bundle data should be passed via Want.parameters'
    },
    'onStart': {
        'target': 'onForeground',
        'param_transform': '',
        'note': 'Android onStart maps to HarmonyOS onForeground'
    },
    'onResume': {
        'target': 'onForeground',
        'param_transform': '',
        'note': 'Android onResume also maps to onForeground (combined state)'
    },
    'onPause': {
        'target': 'onBackground',
        'param_transform': '',
        'note': 'Android onPause maps to HarmonyOS onBackground'
    },
    'onStop': {
        'target': 'onBackground',
        'param_transform': '',
        'note': 'Android onStop also maps to onBackground (combined state)'
    },
    'onDestroy': {
        'target': 'onDestroy',
        'param_transform': '',
        'note': 'Direct mapping'
    },
    'onSaveInstanceState': {
        'target': 'onSaveState',
        'param_transform': 'reason: AbilityConstant.StateType',
        'note': 'Use AppStorage or PersistentStorage for state'
    },
    'onRestoreInstanceState': {
        'target': 'onCreate',
        'param_transform': '',
        'note': 'Restore from Want.parameters or storage'
    }
}

# ============================================================================
# Code Generators
# ============================================================================

class AdapterGenerator:
    """Generate adapter layer code."""

    def generate_adapter(self, class_info: ClassInfo) -> str:
        """Generate TypeScript/ArkTS adapter class."""

        adapter_code = f'''/**
 * CRAFT Auto-Generated Adapter
 * Source: {class_info.package}.{class_info.name}
 *
 * This adapter provides Android Activity API compatibility over HarmonyOS UIAbility.
 */

import {{ UIAbility, AbilityConstant, Want }} from '@kit.AbilityKit';
import {{ hilog }} from '@kit.PerformanceAnalysisKit';
import {{ window }} from '@kit.ArkUI';

const TAG = '{class_info.name}Adapter';
const DOMAIN = 0x0000;

/**
 * Adapter providing Android {class_info.name} API compatibility.
 * Delegates lifecycle and state management to UIAbility.
 */
export class {class_info.name}Adapter {{
    private context: UIAbility;
    private windowStage: window.WindowStage | null = null;

    // State fields adapted from Android
'''

        # Add state fields
        for modifier, field_type, field_name in class_info.fields:
            ts_type = self._java_to_ts_type(field_type)
            adapter_code += f'    private {field_name}: {ts_type};\n'

        adapter_code += f'''
    constructor(context: UIAbility) {{
        this.context = context;
'''

        # Initialize fields
        for modifier, field_type, field_name in class_info.fields:
            default_value = self._get_default_value(field_type)
            adapter_code += f'        this.{field_name} = {default_value};\n'

        adapter_code += '''    }

    /**
     * Get the UIAbility context
     */
    getContext(): UIAbility {
        return this.context;
    }

    /**
     * Set the WindowStage for UI operations
     */
    setWindowStage(windowStage: window.WindowStage): void {
        this.windowStage = windowStage;
    }
'''

        # Generate lifecycle method adapters
        for method in class_info.methods:
            if method.is_lifecycle:
                adapter_code += self._generate_lifecycle_adapter(method)
            elif method.name not in ['updateDisplay']:  # Skip internal methods
                adapter_code += self._generate_method_adapter(method)

        adapter_code += '}\n'

        return adapter_code

    def _generate_lifecycle_adapter(self, method: MethodInfo) -> str:
        """Generate lifecycle method adapter."""
        mapping = LIFECYCLE_MAPPING.get(method.name, {})
        target = mapping.get('target', method.name)
        note = mapping.get('note', '')

        return f'''
    /**
     * Lifecycle: {method.name} -> {target}
     * {note}
     */
    {method.name}(): void {{
        hilog.info(DOMAIN, TAG, '{method.name} called (maps to {target})');
    }}
'''

    def _generate_method_adapter(self, method: MethodInfo) -> str:
        """Generate regular method adapter."""
        ts_params = ', '.join([
            f'{name}: {self._java_to_ts_type(ptype)}'
            for ptype, name in method.parameters
        ])
        ts_return = self._java_to_ts_type(method.return_type)

        return f'''
    /**
     * Adapted method: {method.name}
     */
    {method.name}({ts_params}): {ts_return} {{
        hilog.info(DOMAIN, TAG, '{method.name} called');
'''  + self._generate_method_body(method) + '''    }
'''

    def _generate_method_body(self, method: MethodInfo) -> str:
        """Generate method body based on return type."""
        if method.return_type == 'void':
            return ''
        elif method.return_type == 'int':
            return '        return 0;\n'
        elif method.return_type == 'boolean':
            return '        return false;\n'
        elif method.return_type == 'String':
            return '        return "";\n'
        else:
            return '        return null;\n'

    def _java_to_ts_type(self, java_type: str) -> str:
        """Convert Java type to TypeScript type."""
        type_map = {
            'void': 'void',
            'int': 'number',
            'long': 'number',
            'float': 'number',
            'double': 'number',
            'boolean': 'boolean',
            'String': 'string',
            'CharSequence': 'string',
            'Bundle': 'Record<string, Object>',
            'View': 'Object',
            'Button': 'Object',
            'TextView': 'Object'
        }
        return type_map.get(java_type, 'Object')

    def _get_default_value(self, java_type: str) -> str:
        """Get default value for a Java type."""
        defaults = {
            'int': '0',
            'long': '0',
            'float': '0',
            'double': '0',
            'boolean': 'false',
            'String': '""',
        }
        return defaults.get(java_type, 'null')


class HarmonyGenerator:
    """Generate HarmonyOS UIAbility and UI code."""

    def generate_ability(self, class_info: ClassInfo) -> str:
        """Generate HarmonyOS UIAbility class."""

        return f'''/**
 * CRAFT Auto-Generated UIAbility
 * Adapted from: {class_info.package}.{class_info.name}
 */

import {{ UIAbility, AbilityConstant, Want }} from '@kit.AbilityKit';
import {{ hilog }} from '@kit.PerformanceAnalysisKit';
import {{ window }} from '@kit.ArkUI';
import {{ {class_info.name}Adapter }} from '../adapters/{class_info.name}Adapter';

const TAG = 'EntryAbility';
const DOMAIN = 0x0000;

export default class EntryAbility extends UIAbility {{
    private adapter: {class_info.name}Adapter;
    private counter: number = 0;

    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {{
        hilog.info(DOMAIN, TAG, 'onCreate');

        // Initialize the Android compatibility adapter
        this.adapter = new {class_info.name}Adapter(this);

        // Restore state from Want if available
        if (want.parameters && want.parameters['counter_value']) {{
            this.counter = want.parameters['counter_value'] as number;
        }}

        // Call Android-style onCreate via adapter
        this.adapter.onCreate();
    }}

    onDestroy(): void {{
        hilog.info(DOMAIN, TAG, 'onDestroy');
        this.adapter.onDestroy();
    }}

    onWindowStageCreate(windowStage: window.WindowStage): void {{
        hilog.info(DOMAIN, TAG, 'onWindowStageCreate');

        this.adapter.setWindowStage(windowStage);

        // Load the main page
        windowStage.loadContent('pages/Index', (err) => {{
            if (err.code) {{
                hilog.error(DOMAIN, TAG, 'Failed to load content: %{{public}}s', JSON.stringify(err));
                return;
            }}
            hilog.info(DOMAIN, TAG, 'Content loaded successfully');
        }});
    }}

    onWindowStageDestroy(): void {{
        hilog.info(DOMAIN, TAG, 'onWindowStageDestroy');
    }}

    onForeground(): void {{
        hilog.info(DOMAIN, TAG, 'onForeground');
        // Maps to Android onStart + onResume
        this.adapter.onStart();
        this.adapter.onResume();
    }}

    onBackground(): void {{
        hilog.info(DOMAIN, TAG, 'onBackground');
        // Maps to Android onPause + onStop
        this.adapter.onPause();
        this.adapter.onStop();
    }}

    onSaveState(reason: AbilityConstant.StateType): AbilityConstant.OnSaveResult {{
        hilog.info(DOMAIN, TAG, 'onSaveState, reason: %{{public}}d', reason);
        // Corresponds to Android onSaveInstanceState
        this.adapter.onSaveInstanceState();
        return AbilityConstant.OnSaveResult.ALL_AGREE;
    }}

    // Expose counter operations for the UI
    getCounter(): number {{
        return this.counter;
    }}

    setCounter(value: number): void {{
        this.counter = value;
    }}
}}
'''

    def generate_ui_page(self, class_info: ClassInfo) -> str:
        """Generate ArkUI page component."""

        return '''/**
 * CRAFT Auto-Generated ArkUI Page
 * Counter App - Adapted from Android Layout
 */

import { router } from '@kit.ArkUI';

// Application state using AppStorage for persistence
const counterKey = 'counter_value';

@Entry
@Component
struct Index {
    @State counter: number = 0;

    aboutToAppear(): void {
        // Restore state from AppStorage (equivalent to onRestoreInstanceState)
        const savedCounter = AppStorage.get<number>(counterKey);
        if (savedCounter !== undefined) {
            this.counter = savedCounter;
        }
    }

    aboutToDisappear(): void {
        // Save state to AppStorage (equivalent to onSaveInstanceState)
        AppStorage.setOrCreate(counterKey, this.counter);
    }

    build() {
        Column() {
            // Title
            Text('Counter App')
                .fontSize(28)
                .fontWeight(FontWeight.Bold)
                .fontColor('#333333')
                .margin({ bottom: 40 })

            // Counter Display
            Text(this.counter.toString())
                .fontSize(80)
                .fontWeight(FontWeight.Bold)
                .fontColor('#007AFF')
                .margin({ bottom: 60 })

            // Button Row
            Row() {
                // Decrement Button
                Button('-')
                    .width(90)
                    .height(90)
                    .fontSize(40)
                    .fontColor(Color.White)
                    .backgroundColor('#FF3B30')
                    .borderRadius(45)
                    .onClick(() => {
                        this.decrement();
                    })

                // Reset Button
                Button('0')
                    .width(90)
                    .height(90)
                    .fontSize(32)
                    .fontColor(Color.White)
                    .backgroundColor('#8E8E93')
                    .borderRadius(45)
                    .margin({ left: 20, right: 20 })
                    .onClick(() => {
                        this.reset();
                    })

                // Increment Button
                Button('+')
                    .width(90)
                    .height(90)
                    .fontSize(40)
                    .fontColor(Color.White)
                    .backgroundColor('#34C759')
                    .borderRadius(45)
                    .onClick(() => {
                        this.increment();
                    })
            }
            .justifyContent(FlexAlign.Center)

            // Footer
            Text('Powered by CRAFT Framework')
                .fontSize(14)
                .fontColor('#999999')
                .margin({ top: 60 })

            Text('Android -> HarmonyOS Adapter')
                .fontSize(12)
                .fontColor('#CCCCCC')
                .margin({ top: 8 })
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#FFFFFF')
    }

    /**
     * Increment counter - adapted from MainActivity.increment()
     */
    increment(): void {
        this.counter++;
        this.saveState();
    }

    /**
     * Decrement counter - adapted from MainActivity.decrement()
     */
    decrement(): void {
        this.counter--;
        this.saveState();
    }

    /**
     * Reset counter - adapted from MainActivity.reset()
     */
    reset(): void {
        this.counter = 0;
        this.saveState();
    }

    /**
     * Save state to persistent storage
     */
    private saveState(): void {
        AppStorage.setOrCreate(counterKey, this.counter);
    }
}
'''


# ============================================================================
# Main Generator Script
# ============================================================================

def main():
    print("=" * 70)
    print("  CRAFT Framework - Counter App Generator")
    print("  Android -> HarmonyOS Adaptation")
    print("=" * 70)
    print()

    # Paths
    script_dir = Path(__file__).parent
    android_src = script_dir / "android/app/src/main/java/com/example/counter/MainActivity.java"
    harmony_dir = script_dir / "harmony/entry/src/main/ets"

    # Step 1: Parse Android source
    print("[1/4] Parsing Android source...")
    parser = JavaParser()
    class_info = parser.parse_file(str(android_src))

    print(f"      Package: {class_info.package}")
    print(f"      Class: {class_info.name}")
    print(f"      Parent: {class_info.parent}")
    print(f"      Methods: {len(class_info.methods)}")
    for m in class_info.methods:
        lifecycle_tag = " [LIFECYCLE]" if m.is_lifecycle else ""
        print(f"        - {m.return_type} {m.name}(){lifecycle_tag}")
    print()

    # Step 2: Generate adapter
    print("[2/4] Generating adapter layer...")
    adapter_gen = AdapterGenerator()
    adapter_code = adapter_gen.generate_adapter(class_info)

    adapter_dir = harmony_dir / "adapters"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    adapter_file = adapter_dir / f"{class_info.name}Adapter.ets"

    with open(adapter_file, 'w', encoding='utf-8') as f:
        f.write(adapter_code)
    print(f"      Generated: {adapter_file}")
    print()

    # Step 3: Generate UIAbility
    print("[3/4] Generating UIAbility...")
    harmony_gen = HarmonyGenerator()
    ability_code = harmony_gen.generate_ability(class_info)

    ability_file = harmony_dir / "EntryAbility.ets"
    with open(ability_file, 'w', encoding='utf-8') as f:
        f.write(ability_code)
    print(f"      Generated: {ability_file}")
    print()

    # Step 4: Generate UI Page
    print("[4/4] Generating ArkUI page...")
    page_code = harmony_gen.generate_ui_page(class_info)

    pages_dir = harmony_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    page_file = pages_dir / "Index.ets"

    with open(page_file, 'w', encoding='utf-8') as f:
        f.write(page_code)
    print(f"      Generated: {page_file}")
    print()

    # Summary
    print("=" * 70)
    print("  Generation Complete!")
    print("=" * 70)
    print()
    print("  Generated files:")
    print(f"    1. Adapter:   {adapter_file.relative_to(script_dir)}")
    print(f"    2. UIAbility: {ability_file.relative_to(script_dir)}")
    print(f"    3. UI Page:   {page_file.relative_to(script_dir)}")
    print()
    print("  Lifecycle Mapping Applied:")
    for android, harmony in LIFECYCLE_MAPPING.items():
        print(f"    {android:25} -> {harmony['target']}")
    print()
    print("  To build HarmonyOS app:")
    print("    1. Open DevEco Studio")
    print("    2. Import harmony/ directory as project")
    print("    3. Build and run on device/emulator")
    print()

if __name__ == '__main__':
    main()
