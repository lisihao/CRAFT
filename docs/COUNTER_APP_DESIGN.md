# Counter App 示例应用设计文档

> 版本: 1.0.0 | 日期: 2026-01-21
> 路径: examples/counter-app/

---

## 一、应用概述

### 1.1 功能描述

Counter App 是一个简单的计数器应用，用于演示 CRAFT 框架如何将 Android 应用适配到 HarmonyOS 平台。

**核心功能:**
| 功能 | 描述 | Android 实现 | HarmonyOS 实现 |
|------|------|-------------|---------------|
| 计数显示 | 显示当前计数值 | TextView | Text 组件 |
| 递增 | 点击 + 按钮，计数 +1 | Button.onClick | Button.onClick |
| 递减 | 点击 - 按钮，计数 -1 | Button.onClick | Button.onClick |
| 重置 | 点击 0 按钮，计数归零 | Button.onClick | Button.onClick |
| 状态保存 | 屏幕旋转时保存状态 | onSaveInstanceState | AppStorage |
| 状态恢复 | 重建时恢复状态 | onRestoreInstanceState | AppStorage.get |

### 1.2 项目结构

```
examples/counter-app/
├── android/                              # Android 源项目
│   ├── app/
│   │   ├── build.gradle                  # Gradle 构建配置
│   │   └── src/main/
│   │       ├── AndroidManifest.xml       # 应用清单
│   │       ├── java/com/example/counter/
│   │       │   └── MainActivity.java     # 主 Activity (148 行)
│   │       └── res/
│   │           ├── layout/
│   │           │   └── activity_main.xml # 布局文件
│   │           ├── drawable/
│   │           │   ├── button_red.xml    # 减号按钮样式
│   │           │   ├── button_green.xml  # 加号按钮样式
│   │           │   └── button_gray.xml   # 重置按钮样式
│   │           └── values/
│   │               ├── colors.xml        # 颜色定义
│   │               └── themes.xml        # 主题定义
│   ├── build.gradle                      # 根构建文件
│   ├── settings.gradle                   # Gradle 设置
│   └── gradle/wrapper/                   # Gradle Wrapper
│
├── harmony/                              # HarmonyOS 生成项目
│   ├── AppScope/
│   │   └── app.json5                     # 应用配置
│   ├── entry/
│   │   ├── src/main/
│   │   │   ├── ets/
│   │   │   │   ├── EntryAbility.ets      # UIAbility (86 行)
│   │   │   │   ├── adapters/
│   │   │   │   │   └── MainActivityAdapter.ets  # 适配器 (168 行)
│   │   │   │   └── pages/
│   │   │   │       └── Index.ets         # ArkUI 页面 (133 行)
│   │   │   ├── module.json5              # 模块配置
│   │   │   └── resources/                # 资源文件
│   │   └── hvigorfile.ts
│   ├── build-profile.json5               # 构建配置
│   ├── oh-package.json5                  # 包配置
│   └── hvigorfile.ts
│
├── craft_generate.py                     # CRAFT 生成器脚本
├── verify_code.py                        # 代码验证脚本
└── README.md                             # 项目说明
```

---

## 二、Android API 调用详解

### 2.1 Activity 生命周期 API

```java
// 文件: MainActivity.java

public class MainActivity extends Activity {

    // ═══════════════════════════════════════════════════════════════════
    // Android Activity 生命周期方法
    // ═══════════════════════════════════════════════════════════════════

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // API: Activity.onCreate(Bundle)
        // 功能: Activity 创建时调用，初始化 UI 和状态
        // 包: android.app.Activity
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);  // 加载布局
    }

    @Override
    protected void onStart() {
        // API: Activity.onStart()
        // 功能: Activity 即将可见时调用
        super.onStart();
    }

    @Override
    protected void onResume() {
        // API: Activity.onResume()
        // 功能: Activity 进入前台，可交互
        super.onResume();
    }

    @Override
    protected void onPause() {
        // API: Activity.onPause()
        // 功能: Activity 失去焦点，部分可见
        super.onPause();
    }

    @Override
    protected void onStop() {
        // API: Activity.onStop()
        // 功能: Activity 完全不可见
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        // API: Activity.onDestroy()
        // 功能: Activity 销毁前调用
        super.onDestroy();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        // API: Activity.onSaveInstanceState(Bundle)
        // 功能: 保存实例状态（屏幕旋转、内存回收前）
        super.onSaveInstanceState(outState);
        outState.putInt(KEY_COUNT, counter);  // 保存计数值
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        // API: Activity.onRestoreInstanceState(Bundle)
        // 功能: 恢复实例状态
        super.onRestoreInstanceState(savedInstanceState);
        counter = savedInstanceState.getInt(KEY_COUNT, 0);
    }
}
```

### 2.2 View 系统 API

```java
// ═══════════════════════════════════════════════════════════════════
// Android View 系统 API
// ═══════════════════════════════════════════════════════════════════

// 1. findViewById - 查找视图
// API: Activity.findViewById(int id)
// 包: android.app.Activity
counterText = findViewById(R.id.counter_text);
incrementButton = findViewById(R.id.btn_increment);
decrementButton = findViewById(R.id.btn_decrement);
resetButton = findViewById(R.id.btn_reset);

// 2. setOnClickListener - 设置点击监听
// API: View.setOnClickListener(View.OnClickListener)
// 包: android.view.View
incrementButton.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        increment();
    }
});

// 3. setText - 设置文本内容
// API: TextView.setText(CharSequence)
// 包: android.widget.TextView
counterText.setText(String.valueOf(counter));

// 4. setContentView - 设置内容视图
// API: Activity.setContentView(int layoutResID)
// 包: android.app.Activity
setContentView(R.layout.activity_main);
```

### 2.3 Bundle API

```java
// ═══════════════════════════════════════════════════════════════════
// Android Bundle API - 键值对数据存储
// ═══════════════════════════════════════════════════════════════════

// 包: android.os.Bundle

// 1. putInt - 存储整数
// API: Bundle.putInt(String key, int value)
outState.putInt("counter_value", counter);

// 2. getInt - 读取整数
// API: Bundle.getInt(String key, int defaultValue)
counter = savedInstanceState.getInt("counter_value", 0);

// 3. 空值检查
if (savedInstanceState != null) {
    // Bundle 非空时才读取
}
```

### 2.4 完整 Android API 清单

| API 类 | 方法 | 包路径 | 用途 |
|--------|------|--------|------|
| `Activity` | `onCreate(Bundle)` | `android.app` | 创建初始化 |
| `Activity` | `onStart()` | `android.app` | 即将可见 |
| `Activity` | `onResume()` | `android.app` | 进入前台 |
| `Activity` | `onPause()` | `android.app` | 失去焦点 |
| `Activity` | `onStop()` | `android.app` | 不可见 |
| `Activity` | `onDestroy()` | `android.app` | 销毁 |
| `Activity` | `onSaveInstanceState(Bundle)` | `android.app` | 保存状态 |
| `Activity` | `onRestoreInstanceState(Bundle)` | `android.app` | 恢复状态 |
| `Activity` | `setContentView(int)` | `android.app` | 设置布局 |
| `Activity` | `findViewById(int)` | `android.app` | 查找视图 |
| `View` | `setOnClickListener(OnClickListener)` | `android.view` | 点击事件 |
| `View.OnClickListener` | `onClick(View)` | `android.view` | 点击回调 |
| `TextView` | `setText(CharSequence)` | `android.widget` | 设置文本 |
| `Button` | (继承 TextView) | `android.widget` | 按钮组件 |
| `Bundle` | `putInt(String, int)` | `android.os` | 存储整数 |
| `Bundle` | `getInt(String, int)` | `android.os` | 读取整数 |

---

## 三、CRAFT 框架 API 映射

### 3.1 生命周期映射表

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        生命周期映射对照表                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Android Activity              CRAFT 框架               HarmonyOS UIAbility │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  onCreate(Bundle)      ──────►  LifecycleMapping     ──────►  onCreate(Want)│
│       │                         .activity_to_uiability()        │           │
│       │                              │                          │           │
│       ▼                              ▼                          ▼           │
│  Bundle.getInt()       ──────►  param_transform:     ──────►  Want.parameters│
│                                 "want"                                       │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  onStart()             ──────►  LifecycleMapping     ──────►  onForeground()│
│                                 target: "onForeground"                       │
│                                                                              │
│  onResume()            ──────►  LifecycleMapping     ──────►  onForeground()│
│                                 (合并到 onForeground)                        │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  onPause()             ──────►  LifecycleMapping     ──────►  onBackground()│
│                                 target: "onBackground"                       │
│                                                                              │
│  onStop()              ──────►  LifecycleMapping     ──────►  onBackground()│
│                                 (合并到 onBackground)                        │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  onDestroy()           ──────►  LifecycleMapping     ──────►  onDestroy()   │
│                                 target: "onDestroy"                          │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  onSaveInstanceState() ──────►  LifecycleMapping     ──────►  onSaveState() │
│       │                         + StateAdapter               + AppStorage   │
│       │                              │                          │           │
│       ▼                              ▼                          ▼           │
│  Bundle.putInt()       ──────►  StateTransform       ──────►  AppStorage    │
│                                                              .setOrCreate() │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 CRAFT 框架核心组件调用

```rust
// ═══════════════════════════════════════════════════════════════════
// CRAFT 框架 Rust 组件
// ═══════════════════════════════════════════════════════════════════

// 1. craft-core: 核心数据结构
// 文件: crates/craft-core/src/lib.rs

/// API 规格定义
pub struct ApiSpec {
    pub id: Uuid,                    // 唯一标识
    pub platform: Platform,          // Android / Harmony
    pub package: String,             // 包名: "android.app"
    pub class_name: String,          // 类名: "Activity"
    pub class_type: String,          // 类型: "class" / "interface"
    pub parent_class: Option<String>,// 父类: "ContextThemeWrapper"
    pub interfaces: Vec<String>,     // 接口列表
    pub methods: Vec<MethodSpec>,    // 方法列表
    pub semantic_tags: Vec<String>,  // 语义标签
}

/// 方法规格定义
pub struct MethodSpec {
    pub name: String,                // 方法名: "onCreate"
    pub return_type: String,         // 返回类型: "void"
    pub parameters: Vec<ParameterSpec>, // 参数列表
    pub modifiers: Vec<String>,      // 修饰符: ["public", "protected"]
    pub is_static: bool,             // 是否静态
    pub documentation: Option<String>,// 文档注释
    pub semantic_tags: Vec<String>,  // 语义标签: ["lifecycle:create"]
}

/// 映射规则定义
pub struct MappingRule {
    pub id: Uuid,
    pub source: ApiReference,        // 源 API 引用
    pub target: ApiReference,        // 目标 API 引用
    pub mapping_type: MappingType,   // 映射类型
    pub confidence: f64,             // 置信度
    pub method_mappings: Vec<MethodMapping>, // 方法级映射
}

// ───────────────────────────────────────────────────────────────────
// 2. craft-parser: 解析引擎
// 文件: crates/craft-parser/src/java_parser.rs

/// Java 解析器 (使用 tree-sitter)
pub struct JavaParser {
    parser: Parser,                  // tree-sitter 解析器
    language: Language,              // Java 语言定义
}

impl SdkParser for JavaParser {
    /// 解析单个文件
    fn parse_file(&mut self, path: &Path) -> Result<Option<ApiSpec>, CraftError>;

    /// 解析整个目录 (并行)
    fn parse_directory(&self, path: &Path) -> Result<Vec<ApiSpec>, CraftError>;
}

// 内部方法
impl JavaParser {
    fn extract_package(&self, node: &Node, source: &str) -> String;
    fn extract_class_info(&self, node: &Node, source: &str) -> ClassInfo;
    fn extract_methods(&self, node: &Node, source: &str) -> Vec<MethodSpec>;
    fn generate_semantic_tags(&self, spec: &ApiSpec) -> Vec<String>;
}

// ───────────────────────────────────────────────────────────────────
// 3. craft-generator: 代码生成引擎
// 文件: crates/craft-generator/src/lib.rs

/// 生命周期映射定义
pub struct LifecycleMapping {
    mappings: HashMap<String, LifecycleTarget>,
}

/// 生命周期目标
pub struct LifecycleTarget {
    pub method: String,              // 目标方法名
    pub pre_call: Option<String>,    // 前置调用代码
    pub post_call: Option<String>,   // 后置调用代码
    pub param_transform: Option<String>, // 参数转换
}

impl LifecycleMapping {
    /// 创建 Activity -> UIAbility 映射
    pub fn activity_to_uiability() -> Self {
        let mut mappings = HashMap::new();

        // onCreate -> onCreate
        mappings.insert("onCreate".to_string(), LifecycleTarget {
            method: "onCreate".to_string(),
            pre_call: Some("// Bundle to Want transformation".to_string()),
            param_transform: Some("want".to_string()),
        });

        // onStart -> onForeground
        mappings.insert("onStart".to_string(), LifecycleTarget {
            method: "onForeground".to_string(),
            pre_call: None,
            param_transform: None,
        });

        // ... 其他映射

        Self { mappings }
    }
}

/// 适配器代码生成器
pub struct AdapterGenerator {
    lifecycle_mapping: LifecycleMapping,
}

impl AdapterGenerator {
    /// 生成适配器代码
    pub fn generate(
        &self,
        rule: &MappingRule,
        source: &ApiSpec,
        target: &ApiSpec,
        lang: &str,           // "java" / "kotlin" / "arkts"
    ) -> Result<String, CraftError>;

    /// 生成 Java 适配器
    fn generate_java(&self, ...) -> String;

    /// 生成 Kotlin 适配器
    fn generate_kotlin(&self, ...) -> String;

    /// 生成 ArkTS 适配器
    fn generate_arkts(&self, ...) -> String;
}

// ───────────────────────────────────────────────────────────────────
// 4. craft-analyzer: 语义分析引擎
// 文件: crates/craft-analyzer/src/lib.rs

/// 语义分析器
pub struct SemanticAnalyzer {
    min_confidence: f64,
}

impl SemanticAnalyzer {
    /// 分析源和目标 API，生成映射规则
    pub fn analyze(
        &self,
        source_apis: &[ApiSpec],
        target_apis: &[ApiSpec],
    ) -> Result<Vec<MappingRule>, CraftError>;

    /// 计算 API 相似度
    fn calculate_similarity(&self, source: &ApiSpec, target: &ApiSpec) -> f64;

    /// 字符串相似度
    fn string_similarity(&self, a: &str, b: &str) -> f64;

    /// 语义标签相似度 (Jaccard)
    fn tag_similarity(&self, a: &[String], b: &[String]) -> f64;
}
```

### 3.3 类型转换映射

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           类型转换映射表                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Java 类型              CRAFT TypeConverter          ArkTS/TypeScript 类型  │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  int                   ──────────────────────────►  number                  │
│  long                  ──────────────────────────►  number                  │
│  float                 ──────────────────────────►  number                  │
│  double                ──────────────────────────►  number                  │
│  boolean               ──────────────────────────►  boolean                 │
│  String                ──────────────────────────►  string                  │
│  CharSequence          ──────────────────────────►  string                  │
│  void                  ──────────────────────────►  void                    │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Bundle                ──────────────────────────►  Record<string, Object>  │
│  Intent                ──────────────────────────►  Want                    │
│  Context               ──────────────────────────►  Context (UIAbility)     │
│  View                  ──────────────────────────►  Component               │
│  TextView              ──────────────────────────►  Text                    │
│  Button                ──────────────────────────►  Button                  │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  View.OnClickListener  ──────────────────────────►  () => void              │
│  Runnable              ──────────────────────────►  () => void              │
│  Callback<T>           ──────────────────────────►  (result: T) => void     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 四、Rust 特性使用

### 4.1 使用的 Rust 语言特性

```rust
// ═══════════════════════════════════════════════════════════════════
// 1. 派生宏 (Derive Macros)
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiSpec { ... }

// - Debug: 格式化输出，便于调试
// - Clone: 允许深拷贝
// - Serialize/Deserialize: JSON/YAML 序列化 (serde)

// ═══════════════════════════════════════════════════════════════════
// 2. 错误处理 (thiserror)
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, thiserror::Error)]
pub enum CraftError {
    #[error("Parse error: {0}")]
    ParseError(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Analysis error: {0}")]
    AnalysisError(String),
}

// ═══════════════════════════════════════════════════════════════════
// 3. 并行处理 (Rayon)
// ═══════════════════════════════════════════════════════════════════

use rayon::prelude::*;

// 并行解析目录中的所有文件
let api_specs: Vec<ApiSpec> = files
    .par_iter()                    // 并行迭代器
    .filter_map(|path| {
        let mut parser = JavaParser::new();
        parser.parse_file(path).ok().flatten()
    })
    .collect();

// ═══════════════════════════════════════════════════════════════════
// 4. 外部函数接口 (FFI) - tree-sitter
// ═══════════════════════════════════════════════════════════════════

extern "C" {
    fn tree_sitter_java() -> Language;
    fn tree_sitter_typescript() -> Language;
}

// ═══════════════════════════════════════════════════════════════════
// 5. 生命周期和借用
// ═══════════════════════════════════════════════════════════════════

impl<'a> SdkParser for JavaParser {
    fn parse_file(&mut self, path: &Path) -> Result<Option<ApiSpec>, CraftError> {
        let content = fs::read_to_string(path)?;  // 所有权转移
        self.parse_content(&content, path)        // 借用 content
    }
}

// ═══════════════════════════════════════════════════════════════════
// 6. Option 和 Result 处理
// ═══════════════════════════════════════════════════════════════════

// Option: 可能缺失的值
pub parent_class: Option<String>,

// 使用 ? 操作符传播错误
let tree = self.parser.parse(content, None)
    .ok_or_else(|| CraftError::ParseError("Failed to parse".into()))?;

// filter_map: 过滤并转换
let methods: Vec<MethodSpec> = nodes
    .filter_map(|node| self.parse_method(node, source))
    .collect();

// ═══════════════════════════════════════════════════════════════════
// 7. 迭代器适配器
// ═══════════════════════════════════════════════════════════════════

// 链式调用
let public_methods: Vec<&MethodSpec> = spec.methods
    .iter()
    .filter(|m| m.modifiers.contains(&"public".to_string()))
    .collect();

// ═══════════════════════════════════════════════════════════════════
// 8. HashMap 和 HashSet
// ═══════════════════════════════════════════════════════════════════

use std::collections::{HashMap, HashSet};

// 生命周期映射表
let mut mappings: HashMap<String, LifecycleTarget> = HashMap::new();
mappings.insert("onCreate".to_string(), LifecycleTarget { ... });

// 语义标签集合 (用于 Jaccard 相似度)
let tags_a: HashSet<&String> = a.iter().collect();
let tags_b: HashSet<&String> = b.iter().collect();
let intersection = tags_a.intersection(&tags_b).count();

// ═══════════════════════════════════════════════════════════════════
// 9. Trait 定义和实现
// ═══════════════════════════════════════════════════════════════════

/// SDK 解析器 trait
pub trait SdkParser: Send + Sync {
    fn parse_file(&mut self, path: &Path) -> Result<Option<ApiSpec>, CraftError>;
    fn parse_directory(&self, path: &Path) -> Result<Vec<ApiSpec>, CraftError>;
}

// 为 JavaParser 实现 trait
impl SdkParser for JavaParser {
    fn parse_file(&mut self, path: &Path) -> Result<Option<ApiSpec>, CraftError> {
        // 具体实现
    }
}

// ═══════════════════════════════════════════════════════════════════
// 10. 异步支持 (Tokio)
// ═══════════════════════════════════════════════════════════════════

// craft-ai 模块使用异步 HTTP 客户端
pub async fn send_message(&self, content: &str) -> Result<String, CraftError> {
    let response = self.client
        .post(&self.api_url)
        .headers(self.headers.clone())
        .json(&request_body)
        .send()
        .await?;

    // ...
}
```

### 4.2 使用的 Rust Crate 依赖

| Crate | 版本 | 用途 | 使用位置 |
|-------|------|------|----------|
| `tokio` | 1.35 | 异步运行时 | craft-ai, craft-pipeline |
| `rayon` | 1.8 | 数据并行 | craft-parser, craft-analyzer |
| `serde` | 1.0 | 序列化框架 | 所有模块 |
| `serde_json` | 1.0 | JSON 序列化 | 配置、API 响应 |
| `serde_yaml` | 0.9 | YAML 序列化 | 映射规则文件 |
| `tree-sitter` | 0.20 | 增量解析器 | craft-parser |
| `tree-sitter-java` | 0.20 | Java 语法 | craft-parser |
| `tree-sitter-typescript` | 0.20 | TS/ArkTS 语法 | craft-parser |
| `thiserror` | 1.0 | 错误定义 | craft-core |
| `anyhow` | 1.0 | 错误传播 | craft-cli |
| `reqwest` | 0.11 | HTTP 客户端 | craft-ai |
| `clap` | 4.4 | CLI 参数解析 | craft-cli |
| `walkdir` | 2.4 | 目录遍历 | craft-parser |
| `uuid` | 1.6 | 唯一标识符 | craft-core |
| `chrono` | 0.4 | 日期时间 | craft-core |
| `tracing` | 0.1 | 日志追踪 | 所有模块 |
| `tera` | 1.19 | 模板引擎 | craft-generator (计划) |

---

## 五、Java 特性使用

### 5.1 使用的 Java 语言特性

```java
// ═══════════════════════════════════════════════════════════════════
// 1. 继承 (Inheritance)
// ═══════════════════════════════════════════════════════════════════

public class MainActivity extends Activity {
    // 继承 android.app.Activity
    // 获得生命周期方法、UI 管理等能力
}

// ═══════════════════════════════════════════════════════════════════
// 2. 方法重写 (Override)
// ═══════════════════════════════════════════════════════════════════

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);  // 调用父类实现
    // 子类扩展逻辑
}

// ═══════════════════════════════════════════════════════════════════
// 3. 匿名内部类 (Anonymous Inner Class)
// ═══════════════════════════════════════════════════════════════════

incrementButton.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        increment();  // 访问外部类方法
    }
});

// ═══════════════════════════════════════════════════════════════════
// 4. 访问修饰符
// ═══════════════════════════════════════════════════════════════════

public class MainActivity {           // 公开类
    private int counter = 0;          // 私有字段
    private TextView counterText;     // 私有引用

    protected void onCreate(...) {}   // 受保护方法 (允许子类重写)
    public void increment() {}        // 公开方法
    private void updateDisplay() {}   // 私有辅助方法
}

// ═══════════════════════════════════════════════════════════════════
// 5. 静态常量
// ═══════════════════════════════════════════════════════════════════

private static final String KEY_COUNT = "counter_value";
// static: 类级别，所有实例共享
// final: 不可修改

// ═══════════════════════════════════════════════════════════════════
// 6. 空值检查
// ═══════════════════════════════════════════════════════════════════

if (savedInstanceState != null) {
    counter = savedInstanceState.getInt(KEY_COUNT, 0);
}

if (counterText != null) {
    counterText.setText(String.valueOf(counter));
}

// ═══════════════════════════════════════════════════════════════════
// 7. 字符串转换
// ═══════════════════════════════════════════════════════════════════

String.valueOf(counter)  // int -> String

// ═══════════════════════════════════════════════════════════════════
// 8. 资源引用 (R 类)
// ═══════════════════════════════════════════════════════════════════

R.layout.activity_main   // 布局资源 ID
R.id.counter_text        // 视图 ID
R.id.btn_increment       // 按钮 ID
```

### 5.2 使用的 Android 框架特性

```java
// ═══════════════════════════════════════════════════════════════════
// 1. Activity 组件模型
// ═══════════════════════════════════════════════════════════════════

// Activity 是 Android 四大组件之一
// 代表一个用户交互界面
public class MainActivity extends Activity { }

// 生命周期状态机:
// Created -> Started -> Resumed (活动状态)
//                    <- Paused <- Stopped <- Destroyed

// ═══════════════════════════════════════════════════════════════════
// 2. 视图层次结构 (View Hierarchy)
// ═══════════════════════════════════════════════════════════════════

// XML 布局定义视图树
// LinearLayout (根)
//   └── TextView (标题)
//   └── TextView (计数显示)
//   └── LinearLayout (按钮容器)
//       └── Button (减)
//       └── Button (重置)
//       └── Button (加)

// ═══════════════════════════════════════════════════════════════════
// 3. 资源系统 (Resources)
// ═══════════════════════════════════════════════════════════════════

// res/layout/: 布局 XML
// res/values/: 字符串、颜色、主题
// res/drawable/: 图形资源

// 编译时生成 R.java 提供资源 ID

// ═══════════════════════════════════════════════════════════════════
// 4. Intent 系统 (本示例未使用，但框架支持)
// ═══════════════════════════════════════════════════════════════════

// Intent 用于组件间通信
// 转换为 HarmonyOS Want

// ═══════════════════════════════════════════════════════════════════
// 5. Bundle 状态保存机制
// ═══════════════════════════════════════════════════════════════════

// 系统在以下情况调用 onSaveInstanceState:
// - 屏幕旋转 (Configuration Change)
// - 内存不足被回收
// - 用户按 Home 键

// Bundle 是 Parcelable 的键值对容器
// 转换为 HarmonyOS AppStorage
```

---

## 六、HarmonyOS API 对应

### 6.1 UIAbility 生命周期

```typescript
// ═══════════════════════════════════════════════════════════════════
// HarmonyOS UIAbility 生命周期
// 文件: harmony/entry/src/main/ets/EntryAbility.ets
// ═══════════════════════════════════════════════════════════════════

import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';

export default class EntryAbility extends UIAbility {

    // 对应 Android onCreate
    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
        // want.parameters 对应 Bundle
        if (want.parameters && want.parameters['counter_value']) {
            this.counter = want.parameters['counter_value'] as number;
        }
    }

    // HarmonyOS 特有: 窗口创建
    onWindowStageCreate(windowStage: window.WindowStage): void {
        // 加载页面，对应 setContentView
        windowStage.loadContent('pages/Index', (err) => { });
    }

    // 对应 Android onStart + onResume
    onForeground(): void {
        // 应用进入前台
    }

    // 对应 Android onPause + onStop
    onBackground(): void {
        // 应用进入后台
    }

    // 对应 Android onDestroy
    onDestroy(): void {
        // 释放资源
    }

    // 对应 Android onSaveInstanceState
    onSaveState(reason: AbilityConstant.StateType): AbilityConstant.OnSaveResult {
        return AbilityConstant.OnSaveResult.ALL_AGREE;
    }
}
```

### 6.2 ArkUI 声明式组件

```typescript
// ═══════════════════════════════════════════════════════════════════
// ArkUI 声明式 UI
// 文件: harmony/entry/src/main/ets/pages/Index.ets
// ═══════════════════════════════════════════════════════════════════

@Entry                              // 入口组件 (对应 Activity)
@Component                          // 组件装饰器
struct Index {
    @State counter: number = 0;     // 响应式状态 (对应 private int counter)

    // 对应 Android onRestoreInstanceState
    aboutToAppear(): void {
        const saved = AppStorage.get<number>('counter_value');
        if (saved !== undefined) {
            this.counter = saved;
        }
    }

    // 对应 Android onSaveInstanceState
    aboutToDisappear(): void {
        AppStorage.setOrCreate('counter_value', this.counter);
    }

    // 对应 Android XML 布局
    build() {
        Column() {                   // 对应 LinearLayout (vertical)
            Text('Counter App')      // 对应 TextView
                .fontSize(28)

            Text(this.counter.toString())  // 对应 counterText
                .fontSize(80)

            Row() {                  // 对应 LinearLayout (horizontal)
                Button('-')          // 对应 btn_decrement
                    .onClick(() => this.decrement())

                Button('0')          // 对应 btn_reset
                    .onClick(() => this.reset())

                Button('+')          // 对应 btn_increment
                    .onClick(() => this.increment())
            }
        }
    }

    // 对应 MainActivity.increment()
    increment(): void {
        this.counter++;
        this.saveState();
    }

    // 对应 MainActivity.decrement()
    decrement(): void {
        this.counter--;
        this.saveState();
    }

    // 对应 MainActivity.reset()
    reset(): void {
        this.counter = 0;
        this.saveState();
    }

    // 状态持久化
    private saveState(): void {
        AppStorage.setOrCreate('counter_value', this.counter);
    }
}
```

### 6.3 完整 API 对照表

| 功能 | Android API | HarmonyOS API |
|------|-------------|---------------|
| **组件模型** | `Activity` | `UIAbility` |
| **页面容器** | `Activity` | `@Entry @Component struct` |
| **创建** | `onCreate(Bundle)` | `onCreate(Want)` |
| **窗口创建** | `setContentView()` | `onWindowStageCreate()` |
| **前台** | `onStart()` + `onResume()` | `onForeground()` |
| **后台** | `onPause()` + `onStop()` | `onBackground()` |
| **销毁** | `onDestroy()` | `onDestroy()` |
| **状态保存** | `onSaveInstanceState(Bundle)` | `AppStorage.setOrCreate()` |
| **状态恢复** | `onRestoreInstanceState(Bundle)` | `AppStorage.get()` |
| **组件出现** | `onAttachedToWindow()` | `aboutToAppear()` |
| **组件消失** | `onDetachedFromWindow()` | `aboutToDisappear()` |
| **垂直布局** | `LinearLayout (vertical)` | `Column()` |
| **水平布局** | `LinearLayout (horizontal)` | `Row()` |
| **文本** | `TextView` | `Text()` |
| **按钮** | `Button` | `Button()` |
| **点击事件** | `setOnClickListener()` | `.onClick()` |
| **状态管理** | 成员变量 | `@State` 装饰器 |
| **数据传递** | `Bundle` | `Want.parameters` |
| **持久存储** | `SharedPreferences` | `AppStorage` / `PersistentStorage` |

---

## 七、转换流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Counter App 转换流程                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     输入: Android 源代码                              │    │
│  │                                                                      │    │
│  │   MainActivity.java                   activity_main.xml             │    │
│  │   ┌──────────────────────┐           ┌──────────────────────┐      │    │
│  │   │ class MainActivity   │           │ <LinearLayout>       │      │    │
│  │   │   extends Activity   │           │   <TextView/>        │      │    │
│  │   │                      │           │   <TextView/>        │      │    │
│  │   │ onCreate(Bundle)     │           │   <LinearLayout>     │      │    │
│  │   │ onSaveInstanceState()│           │     <Button/>        │      │    │
│  │   │ increment()          │           │     <Button/>        │      │    │
│  │   │ decrement()          │           │     <Button/>        │      │    │
│  │   └──────────────────────┘           └──────────────────────┘      │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                     │                                        │
│                                     ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CRAFT 框架处理                                     │    │
│  │                                                                      │    │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐ │    │
│  │  │ JavaParser │──►│ Semantic   │──►│ Lifecycle  │──►│ Adapter    │ │    │
│  │  │            │   │ Analyzer   │   │ Mapping    │   │ Generator  │ │    │
│  │  │ tree-sitter│   │            │   │            │   │            │ │    │
│  │  │ 解析 AST   │   │ 提取语义   │   │ Activity   │   │ 生成代码   │ │    │
│  │  │ 提取方法   │   │ 标签       │   │ → UIAbility│   │ Java/ArkTS │ │    │
│  │  └────────────┘   └────────────┘   └────────────┘   └────────────┘ │    │
│  │                                                                      │    │
│  │  处理步骤:                                                            │    │
│  │  1. 解析 MainActivity.java → ApiSpec { methods: [...] }             │    │
│  │  2. 识别生命周期方法 → semantic_tags: ["lifecycle:create", ...]      │    │
│  │  3. 应用映射规则 → onCreate → onCreate, onStart → onForeground      │    │
│  │  4. 生成 ArkTS 代码 → EntryAbility.ets, Index.ets                   │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                     │                                        │
│                                     ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     输出: HarmonyOS 代码                              │    │
│  │                                                                      │    │
│  │   EntryAbility.ets              Index.ets                           │    │
│  │   ┌──────────────────────┐     ┌──────────────────────┐            │    │
│  │   │ class EntryAbility   │     │ @Entry @Component    │            │    │
│  │   │   extends UIAbility  │     │ struct Index {       │            │    │
│  │   │                      │     │                      │            │    │
│  │   │ onCreate(Want)       │     │ @State counter       │            │    │
│  │   │ onForeground()       │     │ aboutToAppear()      │            │    │
│  │   │ onBackground()       │     │ build() { Column() } │            │    │
│  │   │ onDestroy()          │     │ increment()          │            │    │
│  │   └──────────────────────┘     └──────────────────────┘            │    │
│  │                                                                      │    │
│  │   MainActivityAdapter.ets                                           │    │
│  │   ┌──────────────────────┐                                          │    │
│  │   │ class MainActivityAdapter                                       │    │
│  │   │   provides Android API compatibility                            │    │
│  │   │                      │                                          │    │
│  │   │ onCreate() → logs    │                                          │    │
│  │   │ onStart() → logs     │                                          │    │
│  │   │ increment() → logs   │                                          │    │
│  │   └──────────────────────┘                                          │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 八、验证结果

### 8.1 代码验证

运行 `verify_code.py` 脚本验证生成代码的正确性：

```
======================================================================
  CRAFT Code Verification
======================================================================

[1/3] Verifying Android Code...
  ✅ MainActivity.java: Package, Class, onCreate, Braces - ALL PASS
  ✅ AndroidManifest.xml: XML structure - PASS
  ✅ activity_main.xml: Layout structure - PASS

[2/3] Verifying HarmonyOS Code...
  ✅ Index.ets: @Entry, @Component, struct, build() - ALL PASS
  ✅ EntryAbility.ets: UIAbility, lifecycle methods - ALL PASS
  ✅ MainActivityAdapter.ets: export class, constructor - ALL PASS

[3/3] Verifying Configuration Files...
  ✅ module.json5: Valid JSON structure
  ✅ build-profile.json5: Valid JSON structure
  ✅ main_pages.json: Valid JSON structure

══════════════════════════════════════════════════════════════════════
  Verification Summary: 30/30 PASSED
══════════════════════════════════════════════════════════════════════
```

### 8.2 功能对照验证

| 功能 | Android 实现 | HarmonyOS 实现 | 验证状态 |
|------|-------------|---------------|----------|
| 显示计数 | `TextView.setText()` | `Text(counter.toString())` | ✅ |
| 递增 | `counter++; updateDisplay()` | `this.counter++; @State 自动刷新` | ✅ |
| 递减 | `counter--; updateDisplay()` | `this.counter--; @State 自动刷新` | ✅ |
| 重置 | `counter = 0; updateDisplay()` | `this.counter = 0; @State 自动刷新` | ✅ |
| 状态保存 | `Bundle.putInt()` | `AppStorage.setOrCreate()` | ✅ |
| 状态恢复 | `Bundle.getInt()` | `AppStorage.get()` | ✅ |
| 生命周期日志 | `System.out.println()` | `hilog.info()` | ✅ |

---

*文档版本: 1.0.0*
*创建日期: 2026-01-21*
*项目路径: examples/counter-app/*
