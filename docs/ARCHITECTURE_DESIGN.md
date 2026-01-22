# CRAFT 架构设计文档

> **CRAFT Runs Any Framework Technology**
> 版本: 2.1.0 | 日期: 2026-01-21

---

## 一、项目概述

### 1.1 项目定位

CRAFT 是一个 **AI 驱动的跨平台 API 适配层自动生成系统**，专注于将 Android 应用的 API 调用自动转换为 HarmonyOS 兼容代码。

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRAFT 核心价值                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Android App  ───[CRAFT]───>  HarmonyOS App                   │
│                                                                 │
│   • 自动解析 Android API 调用                                   │
│   • 智能映射到 HarmonyOS 等价 API                               │
│   • 生成类型安全的适配器代码                                    │
│   • 支持 Java/Kotlin → ArkTS 转换                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心目标

| 目标 | 描述 | 衡量标准 |
|------|------|---------|
| **自动化** | AI 驱动的 API 映射与代码生成 | 人工介入 < 10% |
| **准确性** | 语义正确的 API 转换 | 映射准确率 > 95% |
| **高性能** | Rust 实现，零成本抽象 | 性能损耗 < 5% |
| **内存安全** | 编译时内存安全保证 | 零内存泄漏 |
| **可扩展** | 支持多平台适配 | 模块化架构 |

### 1.3 技术选型：为什么用 Rust

```
┌─────────────────────────────────────────────────────────────────┐
│                      Rust 技术优势                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔒 内存安全                                                     │
│  ├── 所有权系统：编译时防止内存泄漏                              │
│  ├── 借用检查器：防止悬垂指针和数据竞争                          │
│  └── 无需 GC：确定性内存管理                                     │
│                                                                 │
│  ⚡ 极致性能                                                     │
│  ├── 零成本抽象：与 C/C++ 同级性能                               │
│  ├── tree-sitter 集成：增量解析，毫秒级响应                      │
│  └── Rayon 并行：多核心充分利用                                  │
│                                                                 │
│  ✅ 可验证性                                                     │
│  ├── 强类型：编译时捕获类型错误                                  │
│  ├── Result/Option：强制错误处理                                 │
│  └── 模式匹配：穷尽性检查                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、系统总体架构

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       CRAFT System Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   Layer 1: Input Sources                         │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Android SDK  │  │ HarmonyOS SDK│  │ User Applications    │   │    │
│  │  │ (Java/Kotlin)│  │ (ArkTS)      │  │ (待转换应用)         │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                Layer 2: Parser (craft-parser)                    │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │  tree-sitter 增量解析                                      │   │    │
│  │  │  ├── Java Parser      → AST → ApiSpec                     │   │    │
│  │  │  ├── Kotlin Parser    → AST → ApiSpec                     │   │    │
│  │  │  └── ArkTS Parser     → AST → ApiSpec                     │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                Layer 3: Analyzer (craft-analyzer)                │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │  SemanticAnalyzer                                          │   │    │
│  │  │  ├── calculate_similarity()    # 相似度计算               │   │    │
│  │  │  ├── find_best_mapping()       # 最佳匹配查找             │   │    │
│  │  │  └── generate_method_mappings()# 方法级映射生成           │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │               Layer 4: Generator (craft-generator)               │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │  LifecycleMapping + AdapterGenerator                       │   │    │
│  │  │  ├── activity_to_uiability()   # 生命周期映射             │   │    │
│  │  │  ├── generate_java()           # Java 适配器生成          │   │    │
│  │  │  ├── generate_kotlin()         # Kotlin 适配器生成        │   │    │
│  │  │  └── generate_arkts()          # ArkTS 适配器生成         │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Layer 5: Output                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Adapter Code │  │ Bridge Code  │  │ Documentation        │   │    │
│  │  │ (.java/.ets) │  │ (Shim Layer) │  │ (API Mapping Report) │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
┌────────────────┐          ┌────────────────┐          ┌────────────────┐
│  MainActivity  │          │   ApiSpec      │          │ MappingRule    │
│  .java         │────▶     │  (Rust Struct) │────▶     │ (Rust Struct)  │
│                │  parse   │                │  analyze │                │
└────────────────┘          └────────────────┘          └────────────────┘
                                                               │
                                                               ▼ generate
                            ┌────────────────────────────────────────────┐
                            │                                            │
                 ┌──────────┴──────────┐   ┌──────────┴──────────┐      │
                 │  ActivityAdapter    │   │  Index.ets          │      │
                 │  .java              │   │  (ArkUI Page)       │      │
                 └─────────────────────┘   └─────────────────────┘      │
```

---

## 三、核心组件详细设计

### 3.1 核心数据结构 (craft-core)

#### 3.1.1 API 规格定义

```rust
// crates/craft-core/src/lib.rs

/// 支持的平台
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Platform {
    Android,
    Harmony,
}

/// API 规格定义
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiSpec {
    pub id: Uuid,
    pub platform: Platform,
    pub version: String,
    pub package: String,
    pub class_name: String,
    pub full_qualified_name: String,
    pub class_type: String,            // class, interface, abstract
    pub parent_class: Option<String>,
    pub interfaces: Vec<String>,
    pub methods: Vec<MethodSpec>,
    pub semantic_tags: Vec<String>,
    pub created_at: DateTime<Utc>,
}

/// 方法规格
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MethodSpec {
    pub name: String,
    pub signature: String,
    pub return_type: String,
    pub parameters: Vec<ParameterSpec>,
    pub modifiers: Vec<String>,        // public, static, etc.
    pub semantic_tags: Vec<String>,
    pub doc_comment: Option<String>,
}

/// 参数规格
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParameterSpec {
    pub name: String,
    pub param_type: String,
    pub nullable: bool,
    pub default_value: Option<String>,
}
```

#### 3.1.2 映射规则定义

```rust
/// 映射类型
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MappingType {
    Direct,    // 直接 1:1 映射 (相似度 > 90%)
    Semantic,  // 语义映射 (相似度 70-90%)
    Bridge,    // 桥接映射 (需要额外代码)
    Shim,      // 垫片层 (完全模拟)
}

/// API 映射规则
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingRule {
    pub id: Uuid,
    pub source: ApiReference,          // 源 API (Android)
    pub target: ApiReference,          // 目标 API (HarmonyOS)
    pub mapping_type: MappingType,
    pub confidence: f64,               // 置信度 0.0 - 1.0
    pub method_mappings: Vec<MethodMapping>,
    pub requires_imports: Vec<String>,
    pub bridge_code: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 方法级映射
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MethodMapping {
    pub source_method: String,         // 源方法名
    pub target_method: String,         // 目标方法名
    pub param_mappings: Vec<(String, String)>,  // 参数映射
    pub pre_call_code: Option<String>, // 调用前代码
    pub post_call_code: Option<String>,// 调用后代码
}
```

### 3.2 语义分析器 (craft-analyzer)

#### 3.2.1 SemanticAnalyzer 核心实现

```rust
// crates/craft-analyzer/src/lib.rs

/// 语义分析器
pub struct SemanticAnalyzer {
    min_confidence: f64,  // 最小置信度阈值 (默认 0.7)
}

impl SemanticAnalyzer {
    /// 分析源 API 与目标 API，生成映射规则
    pub fn analyze(
        &self,
        source_apis: &[ApiSpec],
        target_apis: &[ApiSpec],
    ) -> Result<Vec<MappingRule>, CraftError> {
        // 使用 Rayon 并行处理
        let mappings: Vec<MappingRule> = source_apis
            .par_iter()
            .filter_map(|source| self.find_best_mapping(source, target_apis))
            .collect();

        Ok(mappings)
    }

    /// 计算两个 API 的相似度
    fn calculate_similarity(&self, source: &ApiSpec, target: &ApiSpec) -> f64 {
        let mut score = 0.0;

        // 类名相似度 (权重 30%)
        let name_sim = self.string_similarity(&source.class_name, &target.class_name);
        score += name_sim * 0.3;

        // 语义标签重叠 (权重 30%)
        let tag_sim = self.tag_similarity(&source.semantic_tags, &target.semantic_tags);
        score += tag_sim * 0.3;

        // 方法重叠 (权重 40%)
        let method_sim = self.method_similarity(&source.methods, &target.methods);
        score += method_sim * 0.4;

        score
    }

    /// 确定映射类型
    fn determine_mapping_type(&self, source: &ApiSpec, target: &ApiSpec) -> MappingType {
        let similarity = self.calculate_similarity(source, target);

        if similarity > 0.9 {
            MappingType::Direct      // 直接映射
        } else if similarity > 0.7 {
            MappingType::Semantic    // 语义映射
        } else {
            MappingType::Bridge      // 桥接映射
        }
    }
}
```

### 3.3 代码生成器 (craft-generator)

#### 3.3.1 生命周期映射

这是 CRAFT 最核心的组件之一，负责将 Android Activity 生命周期映射到 HarmonyOS UIAbility。

```rust
// crates/craft-generator/src/lib.rs

/// 生命周期目标
pub struct LifecycleTarget {
    pub method: String,                  // 目标方法名
    pub pre_call: Option<String>,        // 调用前代码
    pub post_call: Option<String>,       // 调用后代码
    pub param_transform: Option<String>, // 参数转换
}

/// 生命周期映射器
pub struct LifecycleMapping {
    mappings: HashMap<String, LifecycleTarget>,
}

impl LifecycleMapping {
    /// 创建 Activity -> UIAbility 生命周期映射
    pub fn activity_to_uiability() -> Self {
        let mut mappings = HashMap::new();

        // onCreate -> onCreate (参数 Bundle -> Want)
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

        // onResume -> onForeground (合并)
        mappings.insert("onResume".to_string(), LifecycleTarget {
            method: "onForeground".to_string(),
            pre_call: Some("// Note: onResume maps to onForeground".to_string()),
            ..Default::default()
        });

        // onPause -> onBackground
        mappings.insert("onPause".to_string(), LifecycleTarget {
            method: "onBackground".to_string(),
            ..Default::default()
        });

        // onStop -> onBackground (合并)
        mappings.insert("onStop".to_string(), LifecycleTarget {
            method: "onBackground".to_string(),
            ..Default::default()
        });

        // onDestroy -> onDestroy
        mappings.insert("onDestroy".to_string(), LifecycleTarget {
            method: "onDestroy".to_string(),
            ..Default::default()
        });

        Self { mappings }
    }

    /// 获取目标方法
    pub fn get_target(&self, source_method: &str) -> Option<&LifecycleTarget> {
        self.mappings.get(source_method)
    }

    /// 检查是否为生命周期方法
    pub fn is_lifecycle_method(&self, method_name: &str) -> bool {
        self.mappings.contains_key(method_name)
    }
}
```

#### 3.3.2 AdapterGenerator 代码生成

```rust
/// 适配器代码生成器
pub struct AdapterGenerator {
    tera: Option<Tera>,                    // 模板引擎
    version: String,                       // 生成器版本
    lifecycle_mapping: LifecycleMapping,   // 生命周期映射
}

impl AdapterGenerator {
    /// 生成适配器代码
    pub fn generate(
        &self,
        mapping_rule: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
        output_format: &str,
    ) -> Result<String, CraftError> {
        match output_format {
            "java"   => self.generate_java(mapping_rule, source_api, target_api),
            "kotlin" => self.generate_kotlin(mapping_rule, source_api, target_api),
            "arkts"  => self.generate_arkts(mapping_rule, source_api, target_api),
            _ => Err(CraftError::Generation("Unsupported format".into())),
        }
    }

    /// Java 类型 -> TypeScript 类型转换
    fn java_to_ts_type(&self, java_type: &str) -> String {
        match java_type {
            "void" => "void".to_string(),
            "int" | "long" | "float" | "double" => "number".to_string(),
            "boolean" | "Boolean" => "boolean".to_string(),
            "String" => "string".to_string(),
            "Object" => "any".to_string(),
            other if other.starts_with("List<") => {
                let inner = &other[5..other.len()-1];
                format!("{}[]", self.java_to_ts_type(inner))
            }
            other => other.to_string(),
        }
    }

    /// Java 类型 -> Kotlin 类型转换
    fn java_to_kotlin_type(&self, java_type: &str) -> String {
        match java_type {
            "void" => "Unit".to_string(),
            "int" => "Int".to_string(),
            "boolean" => "Boolean".to_string(),
            other => other.to_string(),
        }
    }
}
```

---

## 四、API 映射流程

### 4.1 完整映射流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         API 映射完整流程                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Step 1: 解析源代码                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  MainActivity.java  ───[tree-sitter]───>  ApiSpec {              │   │
│  │                                             platform: Android,   │   │
│  │                                             class_name: "MainActivity",│
│  │                                             methods: [onCreate, ...]│   │
│  │                                           }                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                     │                                    │
│                                     ▼                                    │
│  Step 2: 语义分析                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SemanticAnalyzer.analyze()                                       │   │
│  │  ├── calculate_similarity(Activity, UIAbility) = 0.85             │   │
│  │  ├── determine_mapping_type() = Semantic                          │   │
│  │  └── generate_method_mappings()                                   │   │
│  │        ├── onCreate -> onCreate                                   │   │
│  │        ├── finish -> terminateSelf                                │   │
│  │        └── onDestroy -> onDestroy                                 │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                     │                                    │
│                                     ▼                                    │
│  Step 3: 生命周期映射                                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  LifecycleMapping.activity_to_uiability()                         │   │
│  │                                                                   │   │
│  │  ┌─────────────────────┬────────────────────────────────────┐    │   │
│  │  │ Android Activity    │ HarmonyOS UIAbility                 │    │   │
│  │  ├─────────────────────┼────────────────────────────────────┤    │   │
│  │  │ onCreate(Bundle)    │ onCreate(Want, LaunchParam)        │    │   │
│  │  │ onStart()           │ onForeground()                     │    │   │
│  │  │ onResume()          │ onForeground()                     │    │   │
│  │  │ onPause()           │ onBackground()                     │    │   │
│  │  │ onStop()            │ onBackground()                     │    │   │
│  │  │ onDestroy()         │ onDestroy()                        │    │   │
│  │  │ finish()            │ terminateSelf()                    │    │   │
│  │  └─────────────────────┴────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                     │                                    │
│                                     ▼                                    │
│  Step 4: 代码生成                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  AdapterGenerator.generate()                                      │   │
│  │  ├── generate_java()   → ActivityAdapter.java                     │   │
│  │  ├── generate_kotlin() → ActivityAdapter.kt                       │   │
│  │  └── generate_arkts()  → Index.ets (ArkUI Page)                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 核心 API 映射表

| Android API | HarmonyOS API | 映射类型 | Rust 函数 |
|-------------|---------------|----------|-----------|
| `Activity.onCreate(Bundle)` | `UIAbility.onCreate(Want, LaunchParam)` | Semantic | `LifecycleMapping.get_target()` |
| `Activity.finish()` | `UIAbilityContext.terminateSelf()` | Bridge | `generate_java_delegation_method()` |
| `Activity.onDestroy()` | `UIAbility.onDestroy()` | Direct | `LifecycleMapping.get_target()` |
| `Activity.setContentView(int)` | `windowStage.loadContent(string)` | Transform | `generate_type_conversion()` |
| `View.setOnClickListener()` | `Button.onClick()` | Semantic | `generate_arkts_method_implementations()` |
| `TextView` | `Text()` | Direct | - |
| `Button` | `Button()` | Direct | - |

---

## 五、实际示例：Hello World 应用

### 5.1 源代码 (Android)

```java
// android/app/src/main/java/com/example/counter/MainActivity.java
package com.example.counter;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Button;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button closeButton = findViewById(R.id.btn_close);
        closeButton.setOnClickListener(v -> finish());
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("MainActivity: Window closed");
    }
}
```

### 5.2 生成代码 (HarmonyOS)

#### 5.2.1 UIAbility

```typescript
// harmony/entry/src/main/ets/EntryAbility.ets
import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';

export default class EntryAbility extends UIAbility {

    /**
     * 对应 Android: Activity.onCreate(Bundle)
     */
    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        hilog.info(0x0000, 'EntryAbility', 'onCreate - 窗口创建');
    }

    /**
     * 对应 Android: Activity.setContentView()
     */
    onWindowStageCreate(windowStage: window.WindowStage): void {
        windowStage.loadContent('pages/Index', (err) => {
            if (err.code) {
                hilog.error(0x0000, 'EntryAbility', '页面加载失败');
                return;
            }
        });
    }

    /**
     * 对应 Android: Activity.onDestroy()
     */
    onDestroy(): void {
        hilog.info(0x0000, 'EntryAbility', 'onDestroy - 窗口关闭');
    }
}
```

#### 5.2.2 ArkUI 页面

```typescript
// harmony/entry/src/main/ets/pages/Index.ets
import { common } from '@kit.AbilityKit';

@Entry
@Component
struct Index {
    private context = getContext(this) as common.UIAbilityContext;

    build() {
        Column() {
            // 对应 Android TextView
            Text('Hello World')
                .fontSize(32)
                .fontWeight(FontWeight.Bold)
                .margin({ bottom: 48 })

            // 对应 Android Button + setOnClickListener
            Button('关闭窗口')
                .width(200)
                .height(60)
                .onClick(() => {
                    this.closeWindow();
                })
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
    }

    /**
     * 对应 Android: Activity.finish()
     * 映射为: UIAbilityContext.terminateSelf()
     */
    closeWindow(): void {
        this.context.terminateSelf();
    }
}
```

#### 5.2.3 适配器层

```typescript
// harmony/entry/src/main/ets/adapters/MainActivityAdapter.ets
import { common } from '@kit.AbilityKit';

/**
 * CRAFT 自动生成 - Android API 适配器
 * 提供 Android Activity API 兼容层
 */
export class MainActivityAdapter {
    private context: common.UIAbilityContext;

    constructor(context: common.UIAbilityContext) {
        this.context = context;
    }

    /**
     * 对应 Android: Activity.finish()
     * 映射为: UIAbilityContext.terminateSelf()
     */
    finish(): void {
        this.context.terminateSelf();
    }

    onCreate(): void {
        // Lifecycle handled by UIAbility
    }

    onDestroy(): void {
        // Lifecycle handled by UIAbility
    }
}
```

---

## 六、项目目录结构

```
CRAFT/
├── Cargo.toml                      # Workspace 配置
├── Cargo.lock                      # 依赖锁定
├── README.md                       # 项目说明
├── CLAUDE.md                       # Claude Code 开发规范
│
├── crates/                         # Rust Crates
│   ├── craft-core/                 # 核心数据结构
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs              # ApiSpec, MappingRule, ...
│   │       └── error.rs            # CraftError
│   │
│   ├── craft-parser/               # 代码解析器
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs              # JavaParser, ArkTSParser
│   │       ├── java.rs             # Java 解析
│   │       └── arkts.rs            # ArkTS 解析
│   │
│   ├── craft-analyzer/             # 语义分析器
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs              # SemanticAnalyzer
│   │
│   ├── craft-generator/            # 代码生成器
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── lib.rs              # LifecycleMapping, AdapterGenerator
│   │
│   ├── craft-ai/                   # AI 集成
│   │   └── src/
│   │       └── lib.rs              # ClaudeClient
│   │
│   ├── craft-pipeline/             # 自动化流水线
│   │   └── src/
│   │       └── lib.rs              # BatchProcessor
│   │
│   └── craft-cli/                  # 命令行工具
│       └── src/
│           └── main.rs             # CLI 入口
│
├── docs/                           # 设计文档
│   ├── ARCHITECTURE_DESIGN.md      # 本文档
│   ├── COUNTER_APP_DESIGN.md       # Hello World 示例设计
│   ├── FEASIBILITY_ANALYSIS.md     # 可行性分析
│   └── CODE_RUNNABLE_ANALYSIS.md   # 代码可运行性分析
│
├── examples/                       # 示例应用
│   └── counter-app/                # Hello World 示例
│       ├── android/                # Android 源码
│       │   └── app/src/main/
│       │       ├── java/           # Java 代码
│       │       └── res/            # 资源文件
│       ├── harmony/                # HarmonyOS 生成代码
│       │   └── entry/src/main/ets/
│       │       ├── EntryAbility.ets
│       │       ├── pages/Index.ets
│       │       └── adapters/
│       ├── craft_generate.py       # Python 生成脚本
│       └── verify_code.py          # 代码验证脚本
│
├── templates/                      # 代码模板 (Tera)
│   ├── adapter_java.tera
│   ├── adapter_kotlin.tera
│   └── prompts/
│       └── generate_adapter.md
│
├── specs/                          # API 规格 (YAML)
│   ├── android/
│   └── harmony/
│
└── configs/                        # 配置文件
    └── craft_config.toml
```

---

## 七、技术栈

| 层次 | 技术 | 用途 |
|------|------|------|
| **语言** | Rust 1.75+ | 内存安全、高性能 |
| **异步** | Tokio | 异步 IO 处理 |
| **并行** | Rayon | CPU 密集型并行计算 |
| **解析** | tree-sitter | 增量代码解析 |
| **序列化** | serde | JSON/YAML 序列化 |
| **模板** | Tera | 代码模板生成 |
| **HTTP** | reqwest | Claude API 调用 |
| **CLI** | clap | 命令行解析 |
| **日志** | tracing | 结构化日志 |
| **错误** | thiserror | 错误类型定义 |

### 7.1 Cargo.toml 工作空间配置

```toml
[workspace]
resolver = "2"
members = [
    "crates/craft-core",
    "crates/craft-parser",
    "crates/craft-analyzer",
    "crates/craft-generator",
    "crates/craft-ai",
    "crates/craft-pipeline",
    "crates/craft-cli",
]

[workspace.dependencies]
tokio = { version = "1.35", features = ["full"] }
rayon = "1.8"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tree-sitter = "0.20"
tree-sitter-java = "0.20"
tera = "1.19"
reqwest = { version = "0.11", features = ["json"] }
clap = { version = "4.4", features = ["derive"] }
tracing = "0.1"
thiserror = "1.0"
chrono = { version = "0.4", features = ["serde"] }
uuid = { version = "1.6", features = ["v4", "serde"] }
```

---

## 八、Rust 核心函数索引

| 模块 | 函数/结构 | 功能 |
|------|----------|------|
| **craft-core** | `ApiSpec::new()` | 创建 API 规格 |
| | `MappingRule::new()` | 创建映射规则 |
| | `MappingType` | 映射类型枚举 |
| **craft-analyzer** | `SemanticAnalyzer::analyze()` | 分析并生成映射 |
| | `calculate_similarity()` | 计算 API 相似度 |
| | `find_best_mapping()` | 查找最佳匹配 |
| | `generate_method_mappings()` | 生成方法映射 |
| | `determine_mapping_type()` | 确定映射类型 |
| **craft-generator** | `LifecycleMapping::activity_to_uiability()` | 生命周期映射 |
| | `LifecycleMapping::get_target()` | 获取目标方法 |
| | `AdapterGenerator::generate()` | 生成适配器代码 |
| | `generate_java()` | 生成 Java 适配器 |
| | `generate_kotlin()` | 生成 Kotlin 适配器 |
| | `generate_arkts()` | 生成 ArkTS 适配器 |
| | `java_to_ts_type()` | Java→TypeScript 类型转换 |
| | `java_to_kotlin_type()` | Java→Kotlin 类型转换 |
| | `generate_type_conversion()` | 生成类型转换代码 |

---

## 九、测试验证

### 9.1 单元测试

```bash
# 运行所有测试
cargo test --all

# 运行特定 crate 测试
cargo test -p craft-generator
```

### 9.2 集成测试

```bash
# Hello World 示例验证
cd examples/counter-app
python3 craft_generate.py
python3 verify_code.py
```

### 9.3 测试覆盖

| 测试类型 | 覆盖范围 |
|----------|----------|
| 生命周期映射 | `test_lifecycle_mapping()` |
| 适配器生成 | `test_generate_java_adapter()` |
| 类型转换 | `test_java_to_ts_type_conversion()` |
| 相似度计算 | `test_string_similarity()` |

---

*文档版本: 2.1.0*
*技术栈: Rust + Python*
*最后更新: 2026-01-21*
*作者: CRAFT Team (AI-assisted)*
