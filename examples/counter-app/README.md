# Counter App - CRAFT Framework Example

This example demonstrates the CRAFT framework's ability to adapt an Android application to HarmonyOS.

## Overview

A simple Counter application that demonstrates:
- Activity lifecycle management (onCreate, onStart, onResume, onPause, onStop, onDestroy)
- State persistence (onSaveInstanceState, onRestoreInstanceState)
- UI components (Button, TextView)
- Event handling (onClick)

## Project Structure

```
counter-app/
├── android/                          # Android Source Application
│   └── app/
│       ├── build.gradle
│       └── src/main/
│           ├── AndroidManifest.xml
│           ├── java/com/example/counter/
│           │   └── MainActivity.java      # Android Activity
│           └── res/layout/
│               └── activity_main.xml       # Android Layout
│
├── harmony/                          # HarmonyOS Generated Application
│   ├── build-profile.json5
│   ├── oh-package.json5
│   ├── hvigorfile.ts
│   ├── AppScope/
│   │   └── app.json5
│   └── entry/
│       ├── hvigorfile.ts
│       └── src/main/
│           ├── module.json5
│           ├── ets/
│           │   ├── EntryAbility.ets           # Generated UIAbility
│           │   ├── adapters/
│           │   │   └── MainActivityAdapter.ets # Generated Adapter Layer
│           │   └── pages/
│           │       └── Index.ets              # Generated ArkUI Page
│           └── resources/
│
├── craft_generate.py                 # CRAFT Generator Script
├── verify_code.py                    # Code Verification Script
└── README.md                         # This file
```

## How It Works

### 1. Android Source (Input)

The Android app (`MainActivity.java`) uses standard Activity lifecycle:

```java
public class MainActivity extends Activity {
    private int counter = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Initialize UI and restore state
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        outState.putInt("counter_value", counter);
    }

    public void increment() { counter++; }
    public void decrement() { counter--; }
    public void reset() { counter = 0; }
}
```

### 2. CRAFT Transformation

The CRAFT framework:
1. **Parses** the Android Java source code
2. **Analyzes** the Activity lifecycle methods
3. **Maps** Android lifecycle to HarmonyOS lifecycle
4. **Generates** UIAbility, Adapter, and ArkUI components

### 3. Generated HarmonyOS Code (Output)

**Adapter Layer** (`MainActivityAdapter.ets`):
- Provides Android Activity API compatibility
- Bridges Android method calls to HarmonyOS equivalents
- Logs lifecycle transitions for debugging

**UIAbility** (`EntryAbility.ets`):
- Extends HarmonyOS UIAbility
- Uses the adapter for Android API compatibility
- Manages the HarmonyOS window lifecycle

**ArkUI Page** (`Index.ets`):
- Declarative UI matching Android layout
- Uses @State for reactive counter display
- Uses AppStorage for state persistence

## Lifecycle Mapping

| Android Activity | HarmonyOS UIAbility | Notes |
|-----------------|---------------------|-------|
| `onCreate(Bundle)` | `onCreate(Want)` | Bundle → Want.parameters |
| `onStart()` | `onForeground()` | Combined with onResume |
| `onResume()` | `onForeground()` | Combined with onStart |
| `onPause()` | `onBackground()` | Combined with onStop |
| `onStop()` | `onBackground()` | Combined with onPause |
| `onDestroy()` | `onDestroy()` | Direct mapping |
| `onSaveInstanceState()` | `AppStorage.setOrCreate()` | Persistent storage |
| `onRestoreInstanceState()` | `AppStorage.get()` | Persistent storage |

## Running the Example

### Generate HarmonyOS Code

```bash
cd examples/counter-app
python3 craft_generate.py
```

### Verify Generated Code

```bash
python3 verify_code.py
```

### Build Android App

```bash
cd android
./gradlew assembleDebug
```

### Build HarmonyOS App

1. Open DevEco Studio
2. File → Open → Select `harmony/` directory
3. Build → Build Hap(s)
4. Run on device/emulator

## Features Demonstrated

- **Lifecycle Adaptation**: Android Activity → HarmonyOS UIAbility
- **State Persistence**: Bundle → AppStorage
- **UI Transformation**: XML Layout → ArkUI Components
- **Event Handling**: onClick → onClick closure
- **Type Conversion**: Java types → TypeScript types

## Verification Results

```
Verification Summary
═══════════════════
  Passed: 30
  Errors: 0
  Warnings: 0

  Result: ALL CHECKS PASSED
```

All generated code passes structural and syntactic validation.
