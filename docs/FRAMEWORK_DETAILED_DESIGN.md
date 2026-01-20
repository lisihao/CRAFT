# CRAFT 框架详细设计文档

> 以百度贴吧 App 为案例的完整框架设计
> 版本: 1.0.0 | 日期: 2026-01-20

---

## 一、框架总体架构

### 1.1 架构全景图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            CRAFT Framework Architecture                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         Layer 1: 输入层 (Input Layer)                    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │    │
│  │  │ Android SDK │  │ HarmonyOS   │  │ 映射规则库  │  │ 配置文件    │     │    │
│  │  │ 源码/JAR    │  │ SDK/d.ts    │  │ (YAML)      │  │ (YAML)      │     │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │    │
│  └─────────┼────────────────┼────────────────┼────────────────┼────────────┘    │
│            │                │                │                │                  │
│            ▼                ▼                ▼                ▼                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                     Layer 2: 解析层 (Parsing Layer)                      │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │    │
│  │  │                    craft-parser (解析引擎)                       │    │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │    │    │
│  │  │  │ Java Parser │  │ ArkTS Parser│  │ Rule Parser             │  │    │    │
│  │  │  │(tree-sitter)│  │(tree-sitter)│  │ (serde_yaml)            │  │    │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │    │    │
│  │  └─────────────────────────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────┬──────────────────────────────────────┘    │
│                                     │                                            │
│                                     ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Layer 3: 分析层 (Analysis Layer)                      │    │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │    │
│  │  │                  craft-analyzer (语义分析引擎)                     │  │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │    │
│  │  │  │语义相似度   │  │ API 签名    │  │ 类型推断    │               │  │    │
│  │  │  │计算器       │  │ 匹配器      │  │ 引擎        │               │  │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘               │  │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │    │
│  │  │  │生命周期     │  │ 参数转换    │  │ 回调映射    │               │  │    │
│  │  │  │映射器       │  │ 分析器      │  │ 分析器      │               │  │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘               │  │    │
│  │  └───────────────────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────┬──────────────────────────────────────┘    │
│                                     │                                            │
│                                     ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                      Layer 4: AI 层 (AI Layer)                           │    │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │    │
│  │  │                     craft-ai (AI 生成引擎)                         │  │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │    │
│  │  │  │ Claude API  │  │ Prompt      │  │ 代码验证    │               │  │    │
│  │  │  │ Client      │  │ Engineering │  │ 器          │               │  │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘               │  │    │
│  │  │  ┌─────────────┐  ┌─────────────┐                                │  │    │
│  │  │  │ 复杂桥接    │  │ 测试用例    │                                │  │    │
│  │  │  │ 生成器      │  │ 生成器      │                                │  │    │
│  │  │  └─────────────┘  └─────────────┘                                │  │    │
│  │  └───────────────────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────┬──────────────────────────────────────┘    │
│                                     │                                            │
│                                     ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                   Layer 5: 生成层 (Generation Layer)                     │    │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │    │
│  │  │                 craft-generator (代码生成引擎)                     │  │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │    │
│  │  │  │ Java 适配器 │  │ Kotlin      │  │ ArkTS       │               │  │    │
│  │  │  │ 生成器      │  │ 适配器生成器│  │ 类型定义    │               │  │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘               │  │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │    │
│  │  │  │ 测试代码    │  │ 文档        │  │ Gradle      │               │  │    │
│  │  │  │ 生成器      │  │ 生成器      │  │ 配置生成器  │               │  │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘               │  │    │
│  │  └───────────────────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────┬──────────────────────────────────────┘    │
│                                     │                                            │
│                                     ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                   Layer 6: 输出层 (Output Layer)                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │    │
│  │  │ 适配器代码  │  │ 测试代码    │  │ 映射报告    │  │ API 文档    │     │    │
│  │  │ (Java/Kt)   │  │ (JUnit)     │  │ (HTML/MD)   │  │ (Markdown)  │     │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    横向: 流水线编排 (craft-pipeline)                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │    │
│  │  │ 任务调度器  │  │ 并行处理器  │  │ 速率限制器  │  │ 进度追踪器  │     │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                   横向: 命令行界面 (craft-cli)                            │    │
│  │  parse │ analyze │ generate │ pipeline │ validate │ report              │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则 | 说明 | 实现方式 |
|------|------|---------|
| **分层解耦** | 每层职责单一，接口清晰 | Rust trait 定义接口 |
| **可扩展性** | 支持新平台、新语言 | 插件化解析器/生成器 |
| **高性能** | 处理大规模 SDK | Rayon 并行 + Tokio 异步 |
| **可验证性** | 生成代码正确性 | 类型系统 + 自动测试 |
| **AI 增强** | 复杂场景智能处理 | Claude API 集成 |

---

## 二、模块详细设计

### 2.1 模块总览

```
CRAFT Framework
├── craft-core          # 核心数据结构 (约 2,000 行)
├── craft-parser        # SDK 解析器 (约 5,000 行)
├── craft-analyzer      # 语义分析器 (约 4,000 行)
├── craft-generator     # 代码生成器 (约 6,000 行)
├── craft-ai            # AI 集成 (约 2,500 行)
├── craft-pipeline      # 流水线编排 (约 3,000 行)
├── craft-cli           # 命令行工具 (约 1,500 行)
├── craft-shim          # 运行时垫片库 (约 10,000 行) [新增]
└── craft-validator     # 验证工具 (约 2,000 行) [新增]
```

---

## 三、craft-core: 核心数据结构

### 3.1 模块职责

定义整个框架共享的核心数据类型，确保类型安全和跨模块一致性。

### 3.2 核心类型定义

```rust
// ============================================================
// 文件: crates/craft-core/src/lib.rs
// ============================================================

/// 支持的平台枚举
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Platform {
    Android,
    Harmony,
    // 预留扩展
    IOS,
    Web,
}

/// API 可见性
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Visibility {
    Public,
    Protected,
    PackagePrivate,
    Private,
}

/// 类型种类
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum TypeKind {
    Primitive(PrimitiveType),
    Class(String),           // 全限定类名
    Interface(String),
    Array(Box<TypeKind>),
    Generic(String, Vec<TypeKind>),  // 泛型类型
    Void,
    Unknown,
}

/// 基本类型
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum PrimitiveType {
    Boolean,
    Byte,
    Char,
    Short,
    Int,
    Long,
    Float,
    Double,
}

/// 参数信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParameterInfo {
    pub name: String,
    pub param_type: TypeKind,
    pub nullable: bool,
    pub default_value: Option<String>,
    pub annotations: Vec<AnnotationInfo>,
}

/// 注解信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnnotationInfo {
    pub name: String,
    pub attributes: HashMap<String, String>,
}

/// 方法信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MethodInfo {
    pub name: String,
    pub signature: String,
    pub return_type: TypeKind,
    pub parameters: Vec<ParameterInfo>,
    pub visibility: Visibility,
    pub is_static: bool,
    pub is_final: bool,
    pub is_abstract: bool,
    pub is_synchronized: bool,
    pub throws: Vec<String>,
    pub annotations: Vec<AnnotationInfo>,
    pub doc_comment: Option<String>,
    pub semantic_tags: Vec<String>,
}

/// 字段信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldInfo {
    pub name: String,
    pub field_type: TypeKind,
    pub visibility: Visibility,
    pub is_static: bool,
    pub is_final: bool,
    pub initial_value: Option<String>,
    pub annotations: Vec<AnnotationInfo>,
}

/// 类/接口信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClassInfo {
    pub id: Uuid,
    pub platform: Platform,
    pub package: String,
    pub name: String,
    pub full_name: String,
    pub kind: ClassKind,
    pub visibility: Visibility,
    pub is_final: bool,
    pub is_abstract: bool,
    pub parent_class: Option<String>,
    pub interfaces: Vec<String>,
    pub type_parameters: Vec<String>,
    pub fields: Vec<FieldInfo>,
    pub methods: Vec<MethodInfo>,
    pub inner_classes: Vec<ClassInfo>,
    pub annotations: Vec<AnnotationInfo>,
    pub doc_comment: Option<String>,
    pub semantic_tags: Vec<String>,
    pub api_level: Option<u32>,       // Android API level
    pub deprecated_since: Option<u32>,
}

/// 类种类
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ClassKind {
    Class,
    Interface,
    Enum,
    Annotation,
    Record,
}

/// 映射类型
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MappingType {
    /// 直接映射: API 签名基本一致
    Direct,
    /// 语义映射: 功能相同但签名不同
    Semantic,
    /// 桥接映射: 需要额外转换逻辑
    Bridge,
    /// 垫片映射: 目标平台无对应，需要模拟实现
    Shim,
    /// 不支持: 无法映射
    Unsupported,
}

/// 映射置信度
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Confidence(pub f64);

impl Confidence {
    pub fn high() -> Self { Self(0.9) }
    pub fn medium() -> Self { Self(0.7) }
    pub fn low() -> Self { Self(0.5) }
    pub fn value(&self) -> f64 { self.0 }
}

/// 方法级映射规则
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MethodMapping {
    pub source_method: String,
    pub target_method: String,
    pub mapping_type: MappingType,
    pub confidence: Confidence,
    pub param_mappings: Vec<ParamMapping>,
    pub return_mapping: Option<ReturnMapping>,
    pub pre_call: Option<String>,      // 调用前代码
    pub post_call: Option<String>,     // 调用后代码
    pub exception_mapping: Vec<ExceptionMapping>,
}

/// 参数映射
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParamMapping {
    pub source_index: usize,
    pub target_index: usize,
    pub converter: Option<String>,  // 转换函数名
}

/// 返回值映射
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReturnMapping {
    pub converter: Option<String>,
    pub null_handling: NullHandling,
}

/// 空值处理策略
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum NullHandling {
    PassThrough,
    ThrowException,
    ReturnDefault,
    Unwrap,
}

/// 异常映射
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExceptionMapping {
    pub source_exception: String,
    pub target_exception: String,
    pub converter: Option<String>,
}

/// 类级映射规则
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClassMapping {
    pub id: Uuid,
    pub source: ClassReference,
    pub target: ClassReference,
    pub mapping_type: MappingType,
    pub confidence: Confidence,
    pub method_mappings: Vec<MethodMapping>,
    pub field_mappings: Vec<FieldMapping>,
    pub lifecycle_mapping: Option<LifecycleMapping>,
    pub requires_imports: Vec<String>,
    pub bridge_code: Option<String>,
    pub notes: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 类引用
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClassReference {
    pub platform: Platform,
    pub full_name: String,
}

/// 生命周期映射 (针对 Activity/UIAbility 等)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LifecycleMapping {
    pub source_callbacks: Vec<String>,
    pub target_callbacks: Vec<String>,
    pub mapping_rules: Vec<LifecycleRule>,
}

/// 生命周期映射规则
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LifecycleRule {
    pub source_callback: String,
    pub target_callback: String,
    pub transformation: Option<String>,
}
```

### 3.3 以百度贴吧为例的数据模型

```rust
// 示例: Activity 类的 ClassInfo 表示
let activity_info = ClassInfo {
    id: Uuid::new_v4(),
    platform: Platform::Android,
    package: "android.app".to_string(),
    name: "Activity".to_string(),
    full_name: "android.app.Activity".to_string(),
    kind: ClassKind::Class,
    visibility: Visibility::Public,
    is_final: false,
    is_abstract: false,
    parent_class: Some("android.content.ContextThemeWrapper".to_string()),
    interfaces: vec![
        "android.view.LayoutInflater.Factory2".to_string(),
        "android.view.Window.Callback".to_string(),
        "android.view.KeyEvent.Callback".to_string(),
    ],
    methods: vec![
        MethodInfo {
            name: "onCreate".to_string(),
            signature: "void onCreate(Bundle)".to_string(),
            return_type: TypeKind::Void,
            parameters: vec![
                ParameterInfo {
                    name: "savedInstanceState".to_string(),
                    param_type: TypeKind::Class("android.os.Bundle".to_string()),
                    nullable: true,
                    default_value: None,
                    annotations: vec![],
                }
            ],
            visibility: Visibility::Protected,
            is_static: false,
            is_final: false,
            is_abstract: false,
            is_synchronized: false,
            throws: vec![],
            annotations: vec![
                AnnotationInfo {
                    name: "Override".to_string(),
                    attributes: HashMap::new(),
                }
            ],
            doc_comment: Some("Called when the activity is starting.".to_string()),
            semantic_tags: vec!["lifecycle".to_string(), "initialization".to_string()],
        },
        // ... 更多方法
    ],
    // ...
};
```

---

## 四、craft-parser: SDK 解析器

### 4.1 模块职责

解析 Android SDK 和 HarmonyOS SDK 的源代码/声明文件，提取 API 元数据。

### 4.2 解析器架构

```
craft-parser/
├── src/
│   ├── lib.rs              # 模块入口
│   ├── traits.rs           # 解析器 trait 定义
│   ├── java/               # Java 解析器
│   │   ├── mod.rs
│   │   ├── lexer.rs        # 词法分析
│   │   ├── parser.rs       # 语法分析 (tree-sitter)
│   │   ├── visitor.rs      # AST 访问者
│   │   └── extractor.rs    # 信息提取器
│   ├── arkts/              # ArkTS 解析器
│   │   ├── mod.rs
│   │   ├── parser.rs
│   │   └── extractor.rs
│   ├── dts/                # TypeScript 声明文件解析器
│   │   ├── mod.rs
│   │   └── parser.rs
│   └── jar/                # JAR 文件解析器 (字节码)
│       ├── mod.rs
│       └── class_reader.rs
```

### 4.3 核心接口设计

```rust
// ============================================================
// 文件: crates/craft-parser/src/traits.rs
// ============================================================

use craft_core::{ClassInfo, Platform};
use std::path::Path;

/// SDK 解析器 trait
pub trait SdkParser: Send + Sync {
    /// 获取解析器支持的平台
    fn platform(&self) -> Platform;

    /// 解析单个文件
    fn parse_file(&self, path: &Path) -> Result<Vec<ClassInfo>, ParseError>;

    /// 解析目录 (支持并行)
    fn parse_directory(&self, path: &Path) -> Result<Vec<ClassInfo>, ParseError>;

    /// 解析 JAR/HAP 包
    fn parse_archive(&self, path: &Path) -> Result<Vec<ClassInfo>, ParseError>;

    /// 获取支持的文件扩展名
    fn supported_extensions(&self) -> &[&str];
}

/// 解析错误
#[derive(Debug, Error)]
pub enum ParseError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Syntax error at {file}:{line}:{column}: {message}")]
    Syntax {
        file: String,
        line: usize,
        column: usize,
        message: String,
    },

    #[error("Unsupported file format: {0}")]
    UnsupportedFormat(String),

    #[error("Parse error: {0}")]
    Other(String),
}

/// 解析配置
#[derive(Debug, Clone)]
pub struct ParseConfig {
    /// 是否包含私有成员
    pub include_private: bool,
    /// 是否包含已废弃 API
    pub include_deprecated: bool,
    /// 最小 API 级别
    pub min_api_level: Option<u32>,
    /// 最大 API 级别
    pub max_api_level: Option<u32>,
    /// 包名过滤 (正则表达式)
    pub package_filter: Option<String>,
    /// 并行线程数
    pub parallelism: usize,
}

impl Default for ParseConfig {
    fn default() -> Self {
        Self {
            include_private: false,
            include_deprecated: true,
            min_api_level: None,
            max_api_level: None,
            package_filter: None,
            parallelism: num_cpus::get(),
        }
    }
}
```

### 4.4 Java 解析器实现

```rust
// ============================================================
// 文件: crates/craft-parser/src/java/parser.rs
// ============================================================

use tree_sitter::{Language, Parser, Tree, Node};
use craft_core::*;

extern "C" { fn tree_sitter_java() -> Language; }

/// Java 源代码解析器
pub struct JavaParser {
    parser: Parser,
    config: ParseConfig,
}

impl JavaParser {
    pub fn new(config: ParseConfig) -> Result<Self, ParseError> {
        let mut parser = Parser::new();
        let language = unsafe { tree_sitter_java() };
        parser.set_language(language)
            .map_err(|e| ParseError::Other(e.to_string()))?;

        Ok(Self { parser, config })
    }

    /// 解析 Java 源代码
    pub fn parse_source(&mut self, source: &str, file_path: &str) -> Result<Vec<ClassInfo>, ParseError> {
        let tree = self.parser.parse(source, None)
            .ok_or_else(|| ParseError::Other("Failed to parse".to_string()))?;

        let root = tree.root_node();
        let mut extractor = JavaExtractor::new(source, file_path, &self.config);
        extractor.extract_classes(root)
    }
}

/// Java AST 信息提取器
struct JavaExtractor<'a> {
    source: &'a str,
    file_path: &'a str,
    config: &'a ParseConfig,
    current_package: String,
    imports: Vec<String>,
}

impl<'a> JavaExtractor<'a> {
    fn new(source: &'a str, file_path: &'a str, config: &'a ParseConfig) -> Self {
        Self {
            source,
            file_path,
            config,
            current_package: String::new(),
            imports: Vec::new(),
        }
    }

    /// 从根节点提取所有类
    fn extract_classes(&mut self, root: Node) -> Result<Vec<ClassInfo>, ParseError> {
        let mut classes = Vec::new();

        // 遍历顶层声明
        for child in root.children(&mut root.walk()) {
            match child.kind() {
                "package_declaration" => {
                    self.current_package = self.extract_package_name(child);
                }
                "import_declaration" => {
                    self.imports.push(self.extract_import(child));
                }
                "class_declaration" | "interface_declaration" | "enum_declaration" => {
                    if let Some(class_info) = self.extract_class(child)? {
                        classes.push(class_info);
                    }
                }
                _ => {}
            }
        }

        Ok(classes)
    }

    /// 提取类信息
    fn extract_class(&self, node: Node) -> Result<Option<ClassInfo>, ParseError> {
        let name = self.find_child_text(node, "identifier")
            .ok_or_else(|| ParseError::Other("Class name not found".to_string()))?;

        let visibility = self.extract_visibility(node);

        // 根据配置过滤
        if !self.config.include_private && visibility == Visibility::Private {
            return Ok(None);
        }

        let kind = match node.kind() {
            "class_declaration" => ClassKind::Class,
            "interface_declaration" => ClassKind::Interface,
            "enum_declaration" => ClassKind::Enum,
            _ => ClassKind::Class,
        };

        let mut class_info = ClassInfo {
            id: Uuid::new_v4(),
            platform: Platform::Android,
            package: self.current_package.clone(),
            name: name.clone(),
            full_name: format!("{}.{}", self.current_package, name),
            kind,
            visibility,
            is_final: self.has_modifier(node, "final"),
            is_abstract: self.has_modifier(node, "abstract"),
            parent_class: self.extract_parent_class(node),
            interfaces: self.extract_interfaces(node),
            type_parameters: self.extract_type_parameters(node),
            fields: Vec::new(),
            methods: Vec::new(),
            inner_classes: Vec::new(),
            annotations: self.extract_annotations(node),
            doc_comment: self.extract_doc_comment(node),
            semantic_tags: Vec::new(),
            api_level: None,
            deprecated_since: None,
        };

        // 提取类体成员
        if let Some(body) = self.find_child(node, "class_body")
            .or_else(|| self.find_child(node, "interface_body"))
            .or_else(|| self.find_child(node, "enum_body"))
        {
            for member in body.children(&mut body.walk()) {
                match member.kind() {
                    "field_declaration" => {
                        class_info.fields.extend(self.extract_fields(member));
                    }
                    "method_declaration" | "constructor_declaration" => {
                        if let Some(method) = self.extract_method(member)? {
                            class_info.methods.push(method);
                        }
                    }
                    "class_declaration" | "interface_declaration" => {
                        if let Some(inner) = self.extract_class(member)? {
                            class_info.inner_classes.push(inner);
                        }
                    }
                    _ => {}
                }
            }
        }

        // 推断语义标签
        class_info.semantic_tags = self.infer_semantic_tags(&class_info);

        Ok(Some(class_info))
    }

    /// 提取方法信息
    fn extract_method(&self, node: Node) -> Result<Option<MethodInfo>, ParseError> {
        let name = self.find_child_text(node, "identifier")
            .ok_or_else(|| ParseError::Other("Method name not found".to_string()))?;

        let visibility = self.extract_visibility(node);

        if !self.config.include_private && visibility == Visibility::Private {
            return Ok(None);
        }

        let return_type = self.extract_return_type(node);
        let parameters = self.extract_parameters(node);

        let method_info = MethodInfo {
            name: name.clone(),
            signature: self.build_signature(&name, &return_type, &parameters),
            return_type,
            parameters,
            visibility,
            is_static: self.has_modifier(node, "static"),
            is_final: self.has_modifier(node, "final"),
            is_abstract: self.has_modifier(node, "abstract"),
            is_synchronized: self.has_modifier(node, "synchronized"),
            throws: self.extract_throws(node),
            annotations: self.extract_annotations(node),
            doc_comment: self.extract_doc_comment(node),
            semantic_tags: Vec::new(),
        };

        Ok(Some(method_info))
    }

    /// 推断语义标签
    fn infer_semantic_tags(&self, class_info: &ClassInfo) -> Vec<String> {
        let mut tags = Vec::new();

        // 根据类名推断
        let name_lower = class_info.name.to_lowercase();
        if name_lower.contains("activity") {
            tags.push("ui".to_string());
            tags.push("lifecycle".to_string());
        }
        if name_lower.contains("fragment") {
            tags.push("ui".to_string());
            tags.push("component".to_string());
        }
        if name_lower.contains("adapter") {
            tags.push("data-binding".to_string());
        }
        if name_lower.contains("service") {
            tags.push("background".to_string());
        }
        if name_lower.contains("receiver") {
            tags.push("event".to_string());
        }
        if name_lower.contains("provider") {
            tags.push("data".to_string());
        }

        // 根据父类推断
        if let Some(ref parent) = class_info.parent_class {
            if parent.contains("Activity") {
                tags.push("activity".to_string());
            }
            if parent.contains("Service") {
                tags.push("service".to_string());
            }
        }

        tags
    }

    // ... 更多辅助方法
}
```

### 4.5 百度贴吧涉及的 Android API 解析示例

需要解析的核心包:

```yaml
# 配置文件: configs/android_packages.yaml
packages:
  # UI 相关
  - android.app
  - android.view
  - android.widget
  - androidx.appcompat
  - androidx.recyclerview
  - androidx.swiperefreshlayout
  - androidx.constraintlayout

  # 数据存储
  - android.content
  - android.database.sqlite
  - android.preference

  # 网络
  - java.net
  - javax.net.ssl

  # 多媒体
  - android.graphics
  - android.media
  - android.hardware.camera2
  - android.provider

  # 系统服务
  - android.os
  - android.app (NotificationManager, Service)
  - android.webkit
```

---

## 五、craft-analyzer: 语义分析器

### 5.1 模块职责

分析 Android API 与 HarmonyOS API 的语义相似性，自动生成映射规则。

### 5.2 分析器架构

```
craft-analyzer/
├── src/
│   ├── lib.rs
│   ├── similarity/           # 相似度计算
│   │   ├── mod.rs
│   │   ├── name_sim.rs       # 名称相似度
│   │   ├── signature_sim.rs  # 签名相似度
│   │   ├── semantic_sim.rs   # 语义相似度
│   │   └── embedding_sim.rs  # 向量嵌入相似度
│   ├── matcher/              # 匹配器
│   │   ├── mod.rs
│   │   ├── class_matcher.rs
│   │   ├── method_matcher.rs
│   │   └── param_matcher.rs
│   ├── lifecycle/            # 生命周期分析
│   │   ├── mod.rs
│   │   ├── android.rs
│   │   └── harmony.rs
│   └── rules/                # 规则生成
│       ├── mod.rs
│       ├── generator.rs
│       └── validator.rs
```

### 5.3 核心接口设计

```rust
// ============================================================
// 文件: crates/craft-analyzer/src/lib.rs
// ============================================================

use craft_core::*;

/// 分析器配置
#[derive(Debug, Clone)]
pub struct AnalyzerConfig {
    /// 最小匹配置信度
    pub min_confidence: f64,
    /// 是否使用 AI 增强
    pub use_ai_enhancement: bool,
    /// 相似度算法权重
    pub weights: SimilarityWeights,
}

/// 相似度权重配置
#[derive(Debug, Clone)]
pub struct SimilarityWeights {
    pub name_weight: f64,       // 名称相似度权重
    pub signature_weight: f64,  // 签名相似度权重
    pub semantic_weight: f64,   // 语义相似度权重
    pub structure_weight: f64,  // 结构相似度权重
}

impl Default for SimilarityWeights {
    fn default() -> Self {
        Self {
            name_weight: 0.3,
            signature_weight: 0.3,
            semantic_weight: 0.25,
            structure_weight: 0.15,
        }
    }
}

/// 语义分析器
pub struct SemanticAnalyzer {
    config: AnalyzerConfig,
    similarity_engine: SimilarityEngine,
    lifecycle_analyzer: LifecycleAnalyzer,
}

impl SemanticAnalyzer {
    /// 分析并生成映射规则
    pub fn analyze(
        &self,
        source_classes: &[ClassInfo],
        target_classes: &[ClassInfo],
    ) -> Result<Vec<ClassMapping>, AnalyzeError> {
        let mut mappings = Vec::new();

        // 使用 Rayon 并行处理
        let candidates: Vec<_> = source_classes
            .par_iter()
            .filter_map(|source| {
                self.find_best_match(source, target_classes)
            })
            .collect();

        for (source, target, confidence) in candidates {
            let mapping = self.generate_mapping(source, target, confidence)?;
            if mapping.confidence.value() >= self.config.min_confidence {
                mappings.push(mapping);
            }
        }

        Ok(mappings)
    }

    /// 找到最佳匹配
    fn find_best_match<'a>(
        &self,
        source: &ClassInfo,
        targets: &'a [ClassInfo],
    ) -> Option<(&ClassInfo, &'a ClassInfo, Confidence)> {
        let mut best_match: Option<(&'a ClassInfo, f64)> = None;

        for target in targets {
            let score = self.similarity_engine.calculate(source, target);
            if score >= self.config.min_confidence {
                if best_match.is_none() || score > best_match.unwrap().1 {
                    best_match = Some((target, score));
                }
            }
        }

        best_match.map(|(target, score)| (source, target, Confidence(score)))
    }

    /// 生成映射规则
    fn generate_mapping(
        &self,
        source: &ClassInfo,
        target: &ClassInfo,
        confidence: Confidence,
    ) -> Result<ClassMapping, AnalyzeError> {
        let mapping_type = self.determine_mapping_type(source, target, confidence);

        let method_mappings = self.generate_method_mappings(source, target)?;

        let lifecycle_mapping = if self.is_lifecycle_component(source) {
            Some(self.lifecycle_analyzer.analyze(source, target)?)
        } else {
            None
        };

        Ok(ClassMapping {
            id: Uuid::new_v4(),
            source: ClassReference {
                platform: source.platform,
                full_name: source.full_name.clone(),
            },
            target: ClassReference {
                platform: target.platform,
                full_name: target.full_name.clone(),
            },
            mapping_type,
            confidence,
            method_mappings,
            field_mappings: Vec::new(),
            lifecycle_mapping,
            requires_imports: self.infer_imports(target),
            bridge_code: None,
            notes: Vec::new(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        })
    }

    /// 判断映射类型
    fn determine_mapping_type(
        &self,
        source: &ClassInfo,
        target: &ClassInfo,
        confidence: Confidence,
    ) -> MappingType {
        if confidence.value() > 0.9 {
            // 高置信度: 可能直接映射
            if self.signatures_match(source, target) {
                MappingType::Direct
            } else {
                MappingType::Semantic
            }
        } else if confidence.value() > 0.7 {
            MappingType::Semantic
        } else if confidence.value() > 0.5 {
            MappingType::Bridge
        } else {
            MappingType::Shim
        }
    }
}
```

### 5.4 相似度计算引擎

```rust
// ============================================================
// 文件: crates/craft-analyzer/src/similarity/mod.rs
// ============================================================

/// 相似度计算引擎
pub struct SimilarityEngine {
    weights: SimilarityWeights,
    name_calculator: NameSimilarityCalculator,
    signature_calculator: SignatureSimilarityCalculator,
    semantic_calculator: SemanticSimilarityCalculator,
}

impl SimilarityEngine {
    /// 计算两个类的综合相似度
    pub fn calculate(&self, source: &ClassInfo, target: &ClassInfo) -> f64 {
        let name_sim = self.name_calculator.calculate(
            &source.name, &target.name
        );

        let signature_sim = self.signature_calculator.calculate(
            &source.methods, &target.methods
        );

        let semantic_sim = self.semantic_calculator.calculate(
            &source.semantic_tags, &target.semantic_tags
        );

        let structure_sim = self.calculate_structure_similarity(source, target);

        // 加权平均
        name_sim * self.weights.name_weight
            + signature_sim * self.weights.signature_weight
            + semantic_sim * self.weights.semantic_weight
            + structure_sim * self.weights.structure_weight
    }
}

/// 名称相似度计算器
pub struct NameSimilarityCalculator;

impl NameSimilarityCalculator {
    /// 使用多种算法计算名称相似度
    pub fn calculate(&self, a: &str, b: &str) -> f64 {
        // 1. 精确匹配
        if a == b {
            return 1.0;
        }

        // 2. 忽略大小写匹配
        if a.eq_ignore_ascii_case(b) {
            return 0.95;
        }

        // 3. 前缀/后缀匹配 (处理命名约定差异)
        // Android: Activity, HarmonyOS: UIAbility
        let a_normalized = self.normalize_name(a);
        let b_normalized = self.normalize_name(b);

        // 4. Levenshtein 距离
        let levenshtein_sim = self.levenshtein_similarity(&a_normalized, &b_normalized);

        // 5. Jaccard 相似度 (基于单词拆分)
        let jaccard_sim = self.jaccard_similarity(&a_normalized, &b_normalized);

        // 6. 语义同义词检查
        let synonym_bonus = self.check_synonyms(a, b);

        (levenshtein_sim * 0.4 + jaccard_sim * 0.4 + synonym_bonus * 0.2).min(1.0)
    }

    /// 名称标准化
    fn normalize_name(&self, name: &str) -> String {
        // 移除常见前缀/后缀
        let mut result = name.to_string();

        // Android 特有后缀
        for suffix in &["Activity", "Fragment", "Service", "Receiver", "Provider", "Adapter", "Manager"] {
            if result.ends_with(suffix) && result.len() > suffix.len() {
                result = result[..result.len() - suffix.len()].to_string();
                break;
            }
        }

        // HarmonyOS 特有后缀
        for suffix in &["Ability", "Extension", "Component"] {
            if result.ends_with(suffix) && result.len() > suffix.len() {
                result = result[..result.len() - suffix.len()].to_string();
                break;
            }
        }

        result.to_lowercase()
    }

    /// 同义词检查
    fn check_synonyms(&self, a: &str, b: &str) -> f64 {
        // 已知的同义词映射
        let synonyms: &[(&[&str], &[&str])] = &[
            // Android => HarmonyOS 常见对应
            (&["Activity"], &["UIAbility"]),
            (&["Intent"], &["Want"]),
            (&["Bundle"], &["Record"]),
            (&["SharedPreferences"], &["Preferences"]),
            (&["Bitmap"], &["PixelMap"]),
            (&["MediaPlayer"], &["AVPlayer"]),
            (&["NotificationManager"], &["notificationManager"]),
            (&["Service"], &["ServiceExtensionAbility"]),
        ];

        for (android_terms, harmony_terms) in synonyms {
            let a_matches = android_terms.iter().any(|t| a.contains(t));
            let b_matches = harmony_terms.iter().any(|t| b.contains(t));

            if a_matches && b_matches {
                return 0.8;
            }
        }

        0.0
    }
}
```

### 5.5 生命周期分析器

```rust
// ============================================================
// 文件: crates/craft-analyzer/src/lifecycle/mod.rs
// ============================================================

/// 生命周期分析器
pub struct LifecycleAnalyzer {
    android_lifecycle: AndroidLifecycle,
    harmony_lifecycle: HarmonyLifecycle,
}

/// Android 生命周期定义
#[derive(Debug)]
pub struct AndroidLifecycle {
    /// Activity 生命周期回调顺序
    pub activity_callbacks: Vec<LifecycleCallback>,
    /// Fragment 生命周期回调顺序
    pub fragment_callbacks: Vec<LifecycleCallback>,
    /// Service 生命周期回调顺序
    pub service_callbacks: Vec<LifecycleCallback>,
}

impl Default for AndroidLifecycle {
    fn default() -> Self {
        Self {
            activity_callbacks: vec![
                LifecycleCallback::new("onCreate", LifecycleState::Created),
                LifecycleCallback::new("onStart", LifecycleState::Started),
                LifecycleCallback::new("onResume", LifecycleState::Resumed),
                LifecycleCallback::new("onPause", LifecycleState::Paused),
                LifecycleCallback::new("onStop", LifecycleState::Stopped),
                LifecycleCallback::new("onDestroy", LifecycleState::Destroyed),
                LifecycleCallback::new("onRestart", LifecycleState::Restarting),
                LifecycleCallback::new("onSaveInstanceState", LifecycleState::Saving),
                LifecycleCallback::new("onRestoreInstanceState", LifecycleState::Restoring),
            ],
            // ... fragment, service
            fragment_callbacks: vec![],
            service_callbacks: vec![],
        }
    }
}

/// HarmonyOS 生命周期定义
#[derive(Debug)]
pub struct HarmonyLifecycle {
    pub ability_callbacks: Vec<LifecycleCallback>,
}

impl Default for HarmonyLifecycle {
    fn default() -> Self {
        Self {
            ability_callbacks: vec![
                LifecycleCallback::new("onCreate", LifecycleState::Created),
                LifecycleCallback::new("onWindowStageCreate", LifecycleState::Created),
                LifecycleCallback::new("onForeground", LifecycleState::Resumed),
                LifecycleCallback::new("onBackground", LifecycleState::Paused),
                LifecycleCallback::new("onWindowStageDestroy", LifecycleState::Destroyed),
                LifecycleCallback::new("onDestroy", LifecycleState::Destroyed),
            ],
        }
    }
}

impl LifecycleAnalyzer {
    /// 分析生命周期映射
    pub fn analyze(
        &self,
        source: &ClassInfo,
        target: &ClassInfo,
    ) -> Result<LifecycleMapping, AnalyzeError> {
        // 判断源类类型
        let component_type = self.detect_component_type(source);

        let mapping_rules = match component_type {
            ComponentType::Activity => self.map_activity_lifecycle(),
            ComponentType::Fragment => self.map_fragment_lifecycle(),
            ComponentType::Service => self.map_service_lifecycle(),
            _ => Vec::new(),
        };

        Ok(LifecycleMapping {
            source_callbacks: mapping_rules.iter().map(|r| r.source_callback.clone()).collect(),
            target_callbacks: mapping_rules.iter().map(|r| r.target_callback.clone()).collect(),
            mapping_rules,
        })
    }

    /// Activity 生命周期映射
    fn map_activity_lifecycle(&self) -> Vec<LifecycleRule> {
        vec![
            LifecycleRule {
                source_callback: "onCreate".to_string(),
                target_callback: "onWindowStageCreate".to_string(),
                transformation: Some(r#"
                    // Bundle 转换
                    let want = this.getWant();
                    let savedState = BundleConverter.fromWant(want);
                "#.to_string()),
            },
            LifecycleRule {
                source_callback: "onStart".to_string(),
                target_callback: "onForeground".to_string(),
                transformation: None, // 合并到 onForeground
            },
            LifecycleRule {
                source_callback: "onResume".to_string(),
                target_callback: "onForeground".to_string(),
                transformation: None,
            },
            LifecycleRule {
                source_callback: "onPause".to_string(),
                target_callback: "onBackground".to_string(),
                transformation: None,
            },
            LifecycleRule {
                source_callback: "onStop".to_string(),
                target_callback: "onBackground".to_string(),
                transformation: None, // 合并到 onBackground
            },
            LifecycleRule {
                source_callback: "onDestroy".to_string(),
                target_callback: "onWindowStageDestroy".to_string(),
                transformation: None,
            },
        ]
    }
}
```

---

## 六、craft-generator: 代码生成器

### 6.1 模块职责

根据映射规则生成适配器代码、测试代码和文档。

### 6.2 生成器架构

```
craft-generator/
├── src/
│   ├── lib.rs
│   ├── templates/              # Tera 模板
│   │   ├── java/
│   │   │   ├── adapter.tera    # 适配器模板
│   │   │   ├── test.tera       # 测试模板
│   │   │   └── converter.tera  # 转换器模板
│   │   ├── kotlin/
│   │   └── docs/
│   ├── java/                   # Java 生成器
│   │   ├── mod.rs
│   │   ├── adapter_gen.rs
│   │   ├── test_gen.rs
│   │   └── converter_gen.rs
│   ├── kotlin/                 # Kotlin 生成器
│   ├── arkts/                  # ArkTS 生成器
│   └── docs/                   # 文档生成器
```

### 6.3 核心接口设计

```rust
// ============================================================
// 文件: crates/craft-generator/src/lib.rs
// ============================================================

use craft_core::*;
use tera::Tera;

/// 代码生成器 trait
pub trait CodeGenerator {
    /// 生成适配器代码
    fn generate_adapter(&self, mapping: &ClassMapping) -> Result<GeneratedCode, GenerateError>;

    /// 生成测试代码
    fn generate_tests(&self, mapping: &ClassMapping) -> Result<GeneratedCode, GenerateError>;

    /// 生成转换器代码
    fn generate_converters(&self, mapping: &ClassMapping) -> Result<Vec<GeneratedCode>, GenerateError>;
}

/// 生成的代码
#[derive(Debug, Clone)]
pub struct GeneratedCode {
    /// 文件名
    pub filename: String,
    /// 文件内容
    pub content: String,
    /// 语言类型
    pub language: Language,
    /// 目标路径 (相对)
    pub target_path: String,
}

/// 支持的语言
#[derive(Debug, Clone, Copy)]
pub enum Language {
    Java,
    Kotlin,
    ArkTS,
    TypeScript,
}

/// Java 适配器生成器
pub struct JavaAdapterGenerator {
    tera: Tera,
    config: GeneratorConfig,
}

impl JavaAdapterGenerator {
    pub fn new(templates_dir: &Path) -> Result<Self, GenerateError> {
        let tera = Tera::new(&format!("{}/**/*.tera", templates_dir.display()))
            .map_err(|e| GenerateError::Template(e.to_string()))?;

        Ok(Self {
            tera,
            config: GeneratorConfig::default(),
        })
    }
}

impl CodeGenerator for JavaAdapterGenerator {
    fn generate_adapter(&self, mapping: &ClassMapping) -> Result<GeneratedCode, GenerateError> {
        let context = self.build_context(mapping);

        let content = self.tera.render("java/adapter.tera", &context)
            .map_err(|e| GenerateError::Template(e.to_string()))?;

        let class_name = mapping.source.full_name.split('.').last().unwrap_or("Unknown");
        let package_path = mapping.source.full_name
            .rsplit_once('.')
            .map(|(pkg, _)| pkg.replace('.', "/"))
            .unwrap_or_default();

        Ok(GeneratedCode {
            filename: format!("{}Adapter.java", class_name),
            content,
            language: Language::Java,
            target_path: format!("adapters/{}", package_path),
        })
    }

    // ... 其他方法实现
}
```

### 6.4 Java 适配器模板

```jinja2
{# ============================================================ #}
{# 文件: templates/java/adapter.tera                            #}
{# ============================================================ #}

/**
 * Auto-generated by CRAFT v{{ generator_version }}
 *
 * Source: {{ source.full_name }}
 * Target: {{ target.full_name }}
 * Mapping Type: {{ mapping_type }}
 * Confidence: {{ confidence | round(precision=2) }}
 * Generated: {{ generated_at }}
 *
 * DO NOT EDIT MANUALLY - regenerate using CRAFT pipeline
 */

package {{ adapter_package }};

{% for import in imports %}
import {{ import }};
{% endfor %}

/**
 * Adapter for {{ source.name }}.
 *
 * This adapter bridges Android's {{ source.full_name }}
 * to HarmonyOS's {{ target.full_name }}.
 */
public class {{ adapter_class }} extends {{ source.name }} {

    private final {{ target.name }} delegate;
    private final Context context;

{% if lifecycle_mapping %}
    // Lifecycle state tracking
    private boolean isCreated = false;
    private boolean isForeground = false;
{% endif %}

    /**
     * Constructs a new {{ adapter_class }}.
     *
     * @param delegate The underlying HarmonyOS {{ target.name }}
     * @param context  The HarmonyOS context
     */
    public {{ adapter_class }}({{ target.name }} delegate, Context context) {
        this.delegate = delegate;
        this.context = context;
    }

{% if lifecycle_mapping %}
    // ==================== Lifecycle Methods ====================

{% for rule in lifecycle_mapping.mapping_rules %}
    @Override
    protected void {{ rule.source_callback }}({% if rule.source_callback == "onCreate" %}Bundle savedInstanceState{% endif %}) {
        super.{{ rule.source_callback }}({% if rule.source_callback == "onCreate" %}savedInstanceState{% endif %});
{% if rule.transformation %}
        {{ rule.transformation | indent(width=8) }}
{% endif %}
        // Delegate to HarmonyOS lifecycle
{% if rule.source_callback == "onCreate" %}
        // Note: onWindowStageCreate is called with WindowStage parameter
        // This is handled separately in the ability context
{% else %}
        delegate.{{ rule.target_callback }}();
{% endif %}
{% if rule.source_callback == "onCreate" %}
        isCreated = true;
{% elif rule.source_callback == "onResume" %}
        isForeground = true;
{% elif rule.source_callback == "onPause" %}
        isForeground = false;
{% endif %}
    }

{% endfor %}
{% endif %}

    // ==================== Method Adapters ====================

{% for method_mapping in method_mappings %}
{% set source_method = source.methods | filter(attribute="name", value=method_mapping.source_method) | first %}
{% if source_method %}
    /**
     * Adapter for {{ source_method.name }}.
{% if source_method.doc_comment %}
     *
     * Original: {{ source_method.doc_comment }}
{% endif %}
     */
    @Override
    public {{ source_method.return_type | java_type }} {{ source_method.name }}({% for param in source_method.parameters %}{{ param.param_type | java_type }} {{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %}) {
{% if method_mapping.pre_call %}
        {{ method_mapping.pre_call | indent(width=8) }}
{% endif %}
{% for param_mapping in method_mapping.param_mappings %}
{% if param_mapping.converter %}
        {{ param_mapping.converter }}({{ source_method.parameters[param_mapping.source_index].name }});
{% endif %}
{% endfor %}
{% if source_method.return_type != "void" %}
        {{ target.methods | filter(attribute="name", value=method_mapping.target_method) | first | default(value="Object") }} result = delegate.{{ method_mapping.target_method }}({% for param in source_method.parameters %}{{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %});
{% if method_mapping.return_mapping and method_mapping.return_mapping.converter %}
        return {{ method_mapping.return_mapping.converter }}(result);
{% else %}
        return result;
{% endif %}
{% else %}
        delegate.{{ method_mapping.target_method }}({% for param in source_method.parameters %}{{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %});
{% endif %}
{% if method_mapping.post_call %}
        {{ method_mapping.post_call | indent(width=8) }}
{% endif %}
    }

{% endif %}
{% endfor %}

    // ==================== Helper Methods ====================

    /**
     * Gets the underlying HarmonyOS delegate.
     *
     * @return The delegate instance
     */
    public {{ target.name }} getDelegate() {
        return delegate;
    }

{% if has_converters %}
    // ==================== Type Converters ====================

{% for converter in converters %}
    {{ converter | indent(width=4) }}

{% endfor %}
{% endif %}
}
```

### 6.5 百度贴吧 Activity 适配器生成示例

```java
// 生成的代码示例: ActivityAdapter.java

/**
 * Auto-generated by CRAFT v0.1.0
 *
 * Source: android.app.Activity
 * Target: ohos.app.ability.UIAbility
 * Mapping Type: Bridge
 * Confidence: 0.85
 * Generated: 2026-01-20T10:30:00Z
 *
 * DO NOT EDIT MANUALLY - regenerate using CRAFT pipeline
 */

package craft.adapters.android.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.view.View;
import android.view.Window;
import ohos.app.ability.UIAbility;
import ohos.app.ability.AbilityLifecycleCallback;
import ohos.aafwk.ability.AbilitySlice;
import ohos.aafwk.content.Intent as OhosIntent;

/**
 * Adapter for Activity.
 *
 * This adapter bridges Android's android.app.Activity
 * to HarmonyOS's ohos.app.ability.UIAbility.
 */
public class ActivityAdapter extends Activity {

    private final UIAbility delegate;
    private final Context context;

    // Lifecycle state tracking
    private boolean isCreated = false;
    private boolean isForeground = false;

    // View management
    private View contentView;

    public ActivityAdapter(UIAbility delegate, Context context) {
        this.delegate = delegate;
        this.context = context;
    }

    // ==================== Lifecycle Methods ====================

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Bundle 转换
        OhosIntent want = delegate.getWant();
        Bundle convertedBundle = BundleConverter.fromWant(want);

        // HarmonyOS 的 onWindowStageCreate 会在窗口阶段创建时调用
        // 在这里进行初始化
        isCreated = true;
    }

    @Override
    protected void onStart() {
        super.onStart();
        // HarmonyOS 没有直接对应的 onStart
        // 合并到 onForeground 处理
    }

    @Override
    protected void onResume() {
        super.onResume();
        delegate.onForeground();
        isForeground = true;
    }

    @Override
    protected void onPause() {
        super.onPause();
        isForeground = false;
    }

    @Override
    protected void onStop() {
        super.onStop();
        delegate.onBackground();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        delegate.onWindowStageDestroy();
        delegate.onDestroy();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        // 保存状态到 HarmonyOS
        delegate.onSaveState();
    }

    // ==================== View Methods ====================

    @Override
    public void setContentView(int layoutResID) {
        // 转换 layout 资源到 ArkUI
        // 这需要 ResourceConverter 支持
        this.contentView = LayoutInflaterCompat.inflate(context, layoutResID);
    }

    @Override
    public void setContentView(View view) {
        this.contentView = view;
        // 桥接到 ArkUI 组件
    }

    @Override
    public View findViewById(int id) {
        if (contentView != null) {
            return contentView.findViewById(id);
        }
        return null;
    }

    // ==================== Intent Methods ====================

    @Override
    public void startActivity(Intent intent) {
        OhosIntent want = IntentConverter.toWant(intent);
        delegate.startAbility(want);
    }

    @Override
    public void startActivityForResult(Intent intent, int requestCode) {
        OhosIntent want = IntentConverter.toWant(intent);
        delegate.startAbilityForResult(want, requestCode);
    }

    @Override
    public void finish() {
        delegate.terminateSelf();
    }

    @Override
    public Intent getIntent() {
        OhosIntent want = delegate.getWant();
        return IntentConverter.fromWant(want);
    }

    // ==================== Window Methods ====================

    @Override
    public Window getWindow() {
        // 返回桥接的 Window 对象
        return new WindowAdapter(delegate.getWindowStage());
    }

    // ==================== Helper Methods ====================

    public UIAbility getDelegate() {
        return delegate;
    }
}
```

---

## 七、craft-ai: AI 生成引擎

### 7.1 模块职责

利用 Claude API 处理复杂映射场景，生成高质量桥接代码。

### 7.2 AI 使用场景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI 辅助场景分类                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 场景 1: 复杂类型转换                                                  │    │
│  │ 触发条件: 参数类型差异大，需要深度转换                                │    │
│  │ 示例: RecyclerView.Adapter → IDataSource                             │    │
│  │ AI 任务: 生成完整的数据适配器转换代码                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 场景 2: 回调模式差异                                                  │    │
│  │ 触发条件: 回调接口设计不同                                            │    │
│  │ 示例: OnClickListener → onClick 事件                                  │    │
│  │ AI 任务: 生成回调桥接和事件转发代码                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 场景 3: 异步模式差异                                                  │    │
│  │ 触发条件: 异步 API 模式不同 (Callback vs Promise)                     │    │
│  │ 示例: AsyncTask → TaskPool                                            │    │
│  │ AI 任务: 生成异步包装和结果转换代码                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 场景 4: 无对应 API (Shim)                                             │    │
│  │ 触发条件: 目标平台无对应 API                                          │    │
│  │ 示例: Fragment → 需要模拟实现                                         │    │
│  │ AI 任务: 设计并生成模拟实现代码                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 场景 5: 测试用例生成                                                  │    │
│  │ 触发条件: 映射规则生成后                                              │    │
│  │ 示例: 为 Activity 适配器生成测试                                      │    │
│  │ AI 任务: 生成覆盖关键路径的测试代码                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 核心接口设计

```rust
// ============================================================
// 文件: crates/craft-ai/src/lib.rs
// ============================================================

use craft_core::*;

/// AI 生成配置
#[derive(Debug, Clone)]
pub struct AiConfig {
    pub provider: AiProvider,
    pub model: String,
    pub api_key: String,
    pub max_tokens: u32,
    pub temperature: f32,
    pub timeout_secs: u64,
}

/// AI 提供者
#[derive(Debug, Clone)]
pub enum AiProvider {
    Anthropic,
    OpenAI,
    Local,
}

/// Claude 客户端
pub struct ClaudeClient {
    config: AiConfig,
    http_client: reqwest::Client,
    rate_limiter: RateLimiter,
}

impl ClaudeClient {
    /// 生成桥接代码
    pub async fn generate_bridge_code(
        &self,
        source_class: &ClassInfo,
        target_class: &ClassInfo,
        mapping: &ClassMapping,
        context: &BridgeContext,
    ) -> Result<BridgeCode, AiError> {
        let prompt = self.build_bridge_prompt(source_class, target_class, mapping, context);

        let response = self.send_request(&prompt).await?;
        let code = self.parse_code_response(&response)?;

        // 验证生成的代码
        self.validate_generated_code(&code)?;

        Ok(code)
    }

    /// 分析 API 相似度
    pub async fn analyze_similarity(
        &self,
        source: &ClassInfo,
        target: &ClassInfo,
    ) -> Result<f64, AiError> {
        let prompt = format!(
            r#"分析以下两个 API 的语义相似度:

Android API:
类名: {}
方法: {:?}
用途: {}

HarmonyOS API:
类名: {}
方法: {:?}
用途: {}

请返回 0.0 到 1.0 之间的相似度分数，只返回数字。"#,
            source.full_name,
            source.methods.iter().map(|m| &m.name).collect::<Vec<_>>(),
            source.doc_comment.as_deref().unwrap_or(""),
            target.full_name,
            target.methods.iter().map(|m| &m.name).collect::<Vec<_>>(),
            target.doc_comment.as_deref().unwrap_or(""),
        );

        let response = self.send_request(&prompt).await?;
        response.trim().parse::<f64>()
            .map_err(|e| AiError::ParseError(e.to_string()))
    }

    /// 生成测试用例
    pub async fn generate_tests(
        &self,
        mapping: &ClassMapping,
        adapter_code: &str,
    ) -> Result<String, AiError> {
        let prompt = format!(
            r#"为以下适配器代码生成 JUnit 5 测试用例:

适配器代码:
```java
{}
```

映射信息:
- 源类: {}
- 目标类: {}
- 映射类型: {:?}

请生成:
1. 单元测试 (mock 目标对象)
2. 边界条件测试
3. 异常处理测试

只返回 Java 测试代码。"#,
            adapter_code,
            mapping.source.full_name,
            mapping.target.full_name,
            mapping.mapping_type,
        );

        self.send_request(&prompt).await
    }

    /// 构建桥接代码 Prompt
    fn build_bridge_prompt(
        &self,
        source: &ClassInfo,
        target: &ClassInfo,
        mapping: &ClassMapping,
        context: &BridgeContext,
    ) -> String {
        format!(
            r#"你是一个专业的 Android 到 HarmonyOS API 适配专家。

## 任务
为以下 Android API 生成 HarmonyOS 适配器代码。

## 源 API (Android)
```
类名: {}
包名: {}
继承: {:?}
实现接口: {:?}

公开方法:
{}
```

## 目标 API (HarmonyOS)
```
类名: {}
包名: {}

公开方法:
{}
```

## 已知映射
{}

## 上下文信息
{}

## 要求
1. 生成完整的 Java 适配器类
2. 处理所有生命周期映射
3. 处理参数类型转换
4. 处理返回值转换
5. 添加必要的错误处理
6. 添加清晰的注释

只返回 Java 代码，不要解释。"#,
            source.name,
            source.package,
            source.parent_class,
            source.interfaces,
            self.format_methods(&source.methods),
            target.name,
            target.package,
            self.format_methods(&target.methods),
            self.format_mapping(mapping),
            context.additional_info,
        )
    }
}

/// 桥接上下文
#[derive(Debug, Clone)]
pub struct BridgeContext {
    /// 相关的转换器类
    pub converters: Vec<String>,
    /// 已知的类型映射
    pub type_mappings: HashMap<String, String>,
    /// 附加信息
    pub additional_info: String,
}

/// 生成的桥接代码
#[derive(Debug, Clone)]
pub struct BridgeCode {
    /// 主适配器代码
    pub adapter: String,
    /// 辅助转换器代码
    pub converters: Vec<String>,
    /// 测试代码
    pub tests: Option<String>,
}
```

---

## 八、craft-shim: 运行时垫片库

### 8.1 模块职责

提供 Android API 在 HarmonyOS 上的运行时支持，实现无法简单映射的 API。

### 8.2 垫片库架构

```
craft-shim/
├── android.app/              # android.app 包垫片
│   ├── Activity.java
│   ├── Fragment.java
│   ├── Service.java
│   └── Application.java
├── android.content/          # android.content 包垫片
│   ├── Context.java
│   ├── Intent.java
│   ├── SharedPreferences.java
│   └── ContentResolver.java
├── android.view/             # android.view 包垫片
│   ├── View.java
│   ├── ViewGroup.java
│   └── LayoutInflater.java
├── android.widget/           # android.widget 包垫片
│   ├── TextView.java
│   ├── ImageView.java
│   ├── Button.java
│   └── RecyclerView.java
├── android.os/               # android.os 包垫片
│   ├── Bundle.java
│   ├── Handler.java
│   └── Looper.java
├── android.graphics/         # android.graphics 包垫片
│   ├── Bitmap.java
│   ├── Canvas.java
│   └── drawable/
├── android.database/         # android.database 包垫片
│   └── sqlite/
├── android.media/            # android.media 包垫片
│   └── MediaPlayer.java
├── android.webkit/           # android.webkit 包垫片
│   └── WebView.java
├── converters/               # 类型转换器
│   ├── BundleConverter.java
│   ├── IntentConverter.java
│   ├── BitmapConverter.java
│   └── ...
└── internal/                 # 内部实现
    ├── ViewBridge.java
    └── LifecycleManager.java
```

### 8.3 百度贴吧关键垫片实现

#### 8.3.1 RecyclerView 垫片

```java
// ============================================================
// 文件: craft-shim/android.widget/RecyclerView.java
// ============================================================

package android.widget;

import ohos.agp.components.Component;
import ohos.agp.components.ListContainer;
import java.util.List;

/**
 * RecyclerView 垫片实现
 *
 * 将 Android RecyclerView 模式桥接到 HarmonyOS ListContainer
 */
public class RecyclerView extends ViewGroup {

    private Adapter adapter;
    private LayoutManager layoutManager;
    private ListContainer delegate;

    // 内部 HarmonyOS 数据源
    private RecyclerDataSource dataSource;

    public RecyclerView(Context context) {
        super(context);
        this.delegate = new ListContainer(context.getOhosContext());
        this.dataSource = new RecyclerDataSource();
    }

    public void setAdapter(Adapter adapter) {
        this.adapter = adapter;
        // 连接 Adapter 到 HarmonyOS 数据源
        this.dataSource.setAdapter(adapter);
        this.delegate.setItemProvider(new RecyclerItemProvider(adapter));
    }

    public void setLayoutManager(LayoutManager layout) {
        this.layoutManager = layout;
        // 配置 ListContainer 的布局模式
        if (layout instanceof LinearLayoutManager) {
            LinearLayoutManager llm = (LinearLayoutManager) layout;
            delegate.setOrientation(llm.getOrientation() == LinearLayoutManager.VERTICAL
                ? Component.VERTICAL : Component.HORIZONTAL);
        } else if (layout instanceof GridLayoutManager) {
            // 使用 TableLayoutManager
            GridLayoutManager glm = (GridLayoutManager) layout;
            // HarmonyOS 使用不同的网格配置方式
        }
    }

    public void scrollToPosition(int position) {
        delegate.scrollTo(position);
    }

    public void smoothScrollToPosition(int position) {
        delegate.scrollToCenter(position);
    }

    // ==================== Adapter 基类 ====================

    public static abstract class Adapter<VH extends ViewHolder> {

        private RecyclerView recyclerView;
        private List<AdapterDataObserver> observers = new ArrayList<>();

        public abstract VH onCreateViewHolder(ViewGroup parent, int viewType);
        public abstract void onBindViewHolder(VH holder, int position);
        public abstract int getItemCount();

        public int getItemViewType(int position) {
            return 0;
        }

        public void notifyDataSetChanged() {
            for (AdapterDataObserver observer : observers) {
                observer.onChanged();
            }
        }

        public void notifyItemInserted(int position) {
            for (AdapterDataObserver observer : observers) {
                observer.onItemRangeInserted(position, 1);
            }
        }

        public void notifyItemRemoved(int position) {
            for (AdapterDataObserver observer : observers) {
                observer.onItemRangeRemoved(position, 1);
            }
        }

        void attachToRecyclerView(RecyclerView rv) {
            this.recyclerView = rv;
        }

        void registerAdapterDataObserver(AdapterDataObserver observer) {
            observers.add(observer);
        }
    }

    // ==================== ViewHolder 基类 ====================

    public static abstract class ViewHolder {
        public View itemView;
        int position;
        int itemViewType;

        public ViewHolder(View itemView) {
            this.itemView = itemView;
        }

        public int getAdapterPosition() {
            return position;
        }

        public int getLayoutPosition() {
            return position;
        }
    }

    // ==================== LayoutManager 基类 ====================

    public static abstract class LayoutManager {
        RecyclerView recyclerView;

        public void onLayoutChildren(Recycler recycler, State state) {
            // 默认实现
        }

        public boolean canScrollVertically() {
            return true;
        }

        public boolean canScrollHorizontally() {
            return false;
        }
    }

    // ==================== HarmonyOS 桥接 ====================

    private class RecyclerItemProvider extends BaseItemProvider {

        private Adapter adapter;

        RecyclerItemProvider(Adapter adapter) {
            this.adapter = adapter;
        }

        @Override
        public int getCount() {
            return adapter.getItemCount();
        }

        @Override
        public Object getItem(int position) {
            return position; // 返回索引作为标识
        }

        @Override
        public long getItemId(int position) {
            return position;
        }

        @Override
        public Component getComponent(int position, Component convertComponent, ComponentContainer parent) {
            int viewType = adapter.getItemViewType(position);
            ViewHolder holder;

            if (convertComponent == null) {
                // 创建新的 ViewHolder
                holder = adapter.onCreateViewHolder(RecyclerView.this, viewType);
            } else {
                // 复用现有组件
                holder = (ViewHolder) convertComponent.getTag();
            }

            // 绑定数据
            holder.position = position;
            adapter.onBindViewHolder(holder, position);

            Component component = holder.itemView.getOhosComponent();
            component.setTag(holder);
            return component;
        }
    }
}
```

#### 8.3.2 SharedPreferences 垫片

```java
// ============================================================
// 文件: craft-shim/android.content/SharedPreferences.java
// ============================================================

package android.content;

import ohos.data.preferences.Preferences;
import ohos.data.preferences.PreferencesHelper;
import java.util.Map;
import java.util.Set;

/**
 * SharedPreferences 垫片实现
 *
 * 桥接到 HarmonyOS Preferences API
 */
public interface SharedPreferences {

    Map<String, ?> getAll();
    String getString(String key, String defValue);
    Set<String> getStringSet(String key, Set<String> defValues);
    int getInt(String key, int defValue);
    long getLong(String key, long defValue);
    float getFloat(String key, float defValue);
    boolean getBoolean(String key, boolean defValue);
    boolean contains(String key);
    Editor edit();

    interface Editor {
        Editor putString(String key, String value);
        Editor putStringSet(String key, Set<String> values);
        Editor putInt(String key, int value);
        Editor putLong(String key, long value);
        Editor putFloat(String key, float value);
        Editor putBoolean(String key, boolean value);
        Editor remove(String key);
        Editor clear();
        boolean commit();
        void apply();
    }

    // 注册监听器
    void registerOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener listener);
    void unregisterOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener listener);

    interface OnSharedPreferenceChangeListener {
        void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key);
    }
}

/**
 * SharedPreferences 实现类
 */
class SharedPreferencesImpl implements SharedPreferences {

    private final Preferences ohosPrefs;
    private final String name;
    private final List<OnSharedPreferenceChangeListener> listeners = new ArrayList<>();

    SharedPreferencesImpl(ohos.app.Context context, String name, int mode) {
        this.name = name;
        this.ohosPrefs = PreferencesHelper.getPreferences(context, name);
    }

    @Override
    public String getString(String key, String defValue) {
        return ohosPrefs.getString(key, defValue);
    }

    @Override
    public int getInt(String key, int defValue) {
        return ohosPrefs.getInt(key, defValue);
    }

    @Override
    public long getLong(String key, long defValue) {
        return ohosPrefs.getLong(key, defValue);
    }

    @Override
    public boolean getBoolean(String key, boolean defValue) {
        return ohosPrefs.getBoolean(key, defValue);
    }

    @Override
    public boolean contains(String key) {
        return ohosPrefs.hasKey(key);
    }

    @Override
    public Editor edit() {
        return new EditorImpl(this);
    }

    @Override
    public Map<String, ?> getAll() {
        return ohosPrefs.getAll();
    }

    void notifyListeners(String key) {
        for (OnSharedPreferenceChangeListener listener : listeners) {
            listener.onSharedPreferenceChanged(this, key);
        }
    }

    /**
     * Editor 实现
     */
    private class EditorImpl implements Editor {

        private final SharedPreferencesImpl prefs;
        private final Map<String, Object> modifications = new HashMap<>();
        private boolean clear = false;

        EditorImpl(SharedPreferencesImpl prefs) {
            this.prefs = prefs;
        }

        @Override
        public Editor putString(String key, String value) {
            modifications.put(key, value);
            return this;
        }

        @Override
        public Editor putInt(String key, int value) {
            modifications.put(key, value);
            return this;
        }

        @Override
        public Editor putBoolean(String key, boolean value) {
            modifications.put(key, value);
            return this;
        }

        @Override
        public Editor remove(String key) {
            modifications.put(key, null);
            return this;
        }

        @Override
        public Editor clear() {
            this.clear = true;
            return this;
        }

        @Override
        public boolean commit() {
            return applyInternal(true);
        }

        @Override
        public void apply() {
            applyInternal(false);
        }

        private boolean applyInternal(boolean sync) {
            if (clear) {
                ohosPrefs.clear();
            }

            for (Map.Entry<String, Object> entry : modifications.entrySet()) {
                String key = entry.getKey();
                Object value = entry.getValue();

                if (value == null) {
                    ohosPrefs.delete(key);
                } else if (value instanceof String) {
                    ohosPrefs.putString(key, (String) value);
                } else if (value instanceof Integer) {
                    ohosPrefs.putInt(key, (Integer) value);
                } else if (value instanceof Boolean) {
                    ohosPrefs.putBoolean(key, (Boolean) value);
                } else if (value instanceof Long) {
                    ohosPrefs.putLong(key, (Long) value);
                } else if (value instanceof Float) {
                    ohosPrefs.putFloat(key, (Float) value);
                }

                prefs.notifyListeners(key);
            }

            if (sync) {
                ohosPrefs.flushSync();
            } else {
                ohosPrefs.flush();
            }

            return true;
        }
    }
}
```

---

## 九、craft-pipeline: 流水线编排

### 9.1 模块职责

编排整个 CRAFT 工作流，支持大规模批量处理。

### 9.2 流水线架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Pipeline Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  输入                                                                        │
│  ├── Android SDK 路径                                                        │
│  ├── HarmonyOS SDK 路径                                                      │
│  ├── 配置文件                                                                │
│  └── 已有映射规则                                                            │
│        │                                                                     │
│        ▼                                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                    Stage 1: 解析 (Parsing)                        │       │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │       │
│  │  │ 解析 Android│    │ 解析 OHOS   │    │ 加载规则    │           │       │
│  │  │ SDK         │    │ SDK         │    │             │           │       │
│  │  └─────────────┘    └─────────────┘    └─────────────┘           │       │
│  │         │                  │                  │                   │       │
│  │         ▼                  ▼                  ▼                   │       │
│  │  ClassInfo[]        ClassInfo[]        MappingRule[]             │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                     │                                        │
│                                     ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                   Stage 2: 分析 (Analysis)                        │       │
│  │  ┌─────────────────────────────────────────────────────────────┐ │       │
│  │  │                  并行匹配引擎                                 │ │       │
│  │  │  Android API ──┬──► 语义分析 ──┬──► 最佳匹配 ──► 映射规则    │ │       │
│  │  │                │              │                              │ │       │
│  │  │  Android API ──┼──► 语义分析 ──┼──► 最佳匹配 ──► 映射规则    │ │       │
│  │  │                │              │                              │ │       │
│  │  │  Android API ──┴──► 语义分析 ──┴──► 最佳匹配 ──► 映射规则    │ │       │
│  │  └─────────────────────────────────────────────────────────────┘ │       │
│  │                          │                                        │       │
│  │                          ▼ 低置信度                               │       │
│  │                    ┌─────────────┐                                │       │
│  │                    │ AI 增强分析 │                                │       │
│  │                    └─────────────┘                                │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                     │                                        │
│                                     ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                   Stage 3: 生成 (Generation)                      │       │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │       │
│  │  │ 生成适配器  │    │ 生成测试    │    │ 生成文档    │           │       │
│  │  │ 代码        │    │ 代码        │    │             │           │       │
│  │  └─────────────┘    └─────────────┘    └─────────────┘           │       │
│  │                          │                                        │       │
│  │                          ▼ 复杂映射                               │       │
│  │                    ┌─────────────┐                                │       │
│  │                    │ AI 代码生成 │                                │       │
│  │                    └─────────────┘                                │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                     │                                        │
│                                     ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                   Stage 4: 验证 (Validation)                      │       │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │       │
│  │  │ 语法检查    │    │ 类型检查    │    │ 测试执行    │           │       │
│  │  └─────────────┘    └─────────────┘    └─────────────┘           │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                     │                                        │
│                                     ▼                                        │
│  输出                                                                        │
│  ├── 适配器代码 (Java/Kotlin)                                               │
│  ├── 测试代码 (JUnit)                                                        │
│  ├── 映射报告 (HTML/Markdown)                                                │
│  └── API 文档 (Markdown)                                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 核心接口设计

```rust
// ============================================================
// 文件: crates/craft-pipeline/src/lib.rs
// ============================================================

use craft_core::*;
use craft_parser::SdkParser;
use craft_analyzer::SemanticAnalyzer;
use craft_generator::CodeGenerator;
use craft_ai::ClaudeClient;

/// 流水线配置
#[derive(Debug, Clone, Deserialize)]
pub struct PipelineConfig {
    /// 源 SDK 路径
    pub source_sdk_path: PathBuf,
    /// 目标 SDK 路径
    pub target_sdk_path: PathBuf,
    /// 输出目录
    pub output_dir: PathBuf,
    /// 已有规则路径
    pub rules_path: Option<PathBuf>,
    /// 并行度
    pub parallelism: usize,
    /// AI 配置
    pub ai_config: Option<AiConfig>,
    /// 最小置信度阈值
    pub min_confidence: f64,
    /// 是否生成测试
    pub generate_tests: bool,
    /// 是否生成文档
    pub generate_docs: bool,
}

/// 流水线统计
#[derive(Debug, Default)]
pub struct PipelineStats {
    pub total_source_classes: usize,
    pub total_target_classes: usize,
    pub direct_mappings: usize,
    pub semantic_mappings: usize,
    pub bridge_mappings: usize,
    pub shim_mappings: usize,
    pub unsupported: usize,
    pub ai_enhanced: usize,
    pub generated_adapters: usize,
    pub generated_tests: usize,
    pub duration_secs: f64,
}

/// 流水线编排器
pub struct PipelineOrchestrator {
    config: PipelineConfig,
    parser: Box<dyn SdkParser>,
    analyzer: SemanticAnalyzer,
    generator: Box<dyn CodeGenerator>,
    ai_client: Option<ClaudeClient>,
}

impl PipelineOrchestrator {
    /// 运行完整流水线
    pub async fn run(&self) -> Result<PipelineStats, PipelineError> {
        let start = Instant::now();
        let mut stats = PipelineStats::default();

        // Stage 1: 解析
        info!("Stage 1: Parsing SDKs...");
        let (source_classes, target_classes) = self.parse_sdks().await?;
        stats.total_source_classes = source_classes.len();
        stats.total_target_classes = target_classes.len();

        // Stage 2: 分析
        info!("Stage 2: Analyzing APIs...");
        let mappings = self.analyze_apis(&source_classes, &target_classes).await?;
        self.update_mapping_stats(&mappings, &mut stats);

        // Stage 3: 生成
        info!("Stage 3: Generating code...");
        let generated = self.generate_code(&mappings).await?;
        stats.generated_adapters = generated.adapters.len();
        stats.generated_tests = generated.tests.len();

        // Stage 4: 验证
        info!("Stage 4: Validating output...");
        self.validate_output(&generated).await?;

        // 保存输出
        self.save_output(&generated, &mappings).await?;

        stats.duration_secs = start.elapsed().as_secs_f64();
        Ok(stats)
    }

    /// 解析 SDK
    async fn parse_sdks(&self) -> Result<(Vec<ClassInfo>, Vec<ClassInfo>), PipelineError> {
        let source_parser = JavaParser::new(ParseConfig::default())?;
        let target_parser = ArkTsParser::new(ParseConfig::default())?;

        // 并行解析
        let (source, target) = tokio::join!(
            tokio::task::spawn_blocking(move || {
                source_parser.parse_directory(&self.config.source_sdk_path)
            }),
            tokio::task::spawn_blocking(move || {
                target_parser.parse_directory(&self.config.target_sdk_path)
            })
        );

        Ok((source??, target??))
    }

    /// 分析 API
    async fn analyze_apis(
        &self,
        source: &[ClassInfo],
        target: &[ClassInfo],
    ) -> Result<Vec<ClassMapping>, PipelineError> {
        // 基础分析
        let mut mappings = self.analyzer.analyze(source, target)?;

        // AI 增强 (低置信度的映射)
        if let Some(ref ai_client) = self.ai_client {
            let low_confidence: Vec<_> = mappings
                .iter_mut()
                .filter(|m| m.confidence.value() < 0.7)
                .collect();

            for mapping in low_confidence {
                let enhanced = ai_client
                    .enhance_mapping(mapping)
                    .await
                    .unwrap_or_else(|_| mapping.clone());
                *mapping = enhanced;
            }
        }

        Ok(mappings)
    }

    /// 生成代码
    async fn generate_code(&self, mappings: &[ClassMapping]) -> Result<GeneratedOutput, PipelineError> {
        let mut output = GeneratedOutput::default();

        // 使用 Rayon 并行生成
        let adapters: Vec<_> = mappings
            .par_iter()
            .filter_map(|mapping| {
                self.generator.generate_adapter(mapping).ok()
            })
            .collect();

        output.adapters = adapters;

        // 生成测试
        if self.config.generate_tests {
            let tests: Vec<_> = mappings
                .par_iter()
                .filter_map(|mapping| {
                    self.generator.generate_tests(mapping).ok()
                })
                .collect();
            output.tests = tests;
        }

        Ok(output)
    }
}

/// 生成输出
#[derive(Debug, Default)]
pub struct GeneratedOutput {
    pub adapters: Vec<GeneratedCode>,
    pub tests: Vec<GeneratedCode>,
    pub docs: Vec<GeneratedCode>,
    pub converters: Vec<GeneratedCode>,
}
```

---

## 十、百度贴吧完整适配方案

### 10.1 API 分类与工作量

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    百度贴吧 API 适配工作量详细分解                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ 一、生命周期 API (P0)                                                   ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                        ║  │
│  ║  类名                    方法数    映射类型    CRAFT 覆盖    人工介入   ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  Activity                15       Bridge      80%          3 方法     ║  │
│  ║  Fragment                20       Shim        40%          12 方法    ║  │
│  ║  Service                 8        Bridge      70%          2 方法     ║  │
│  ║  BroadcastReceiver       3        Bridge      90%          0 方法     ║  │
│  ║  Application             5        Bridge      80%          1 方法     ║  │
│  ║  Intent                  25       Semantic    85%          4 方法     ║  │
│  ║  Bundle                  30       Semantic    90%          3 方法     ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  小计                    106      -           ~75%         25 方法    ║  │
│  ║                                                                        ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ 二、UI 组件 API (P0-P1)                                                 ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                        ║  │
│  ║  类名                    方法数    映射类型    CRAFT 覆盖    人工介入   ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  View                    50       Bridge      60%          20 方法    ║  │
│  ║  ViewGroup               20       Bridge      65%          7 方法     ║  │
│  ║  TextView                25       Semantic    85%          4 方法     ║  │
│  ║  ImageView               15       Semantic    80%          3 方法     ║  │
│  ║  EditText                20       Semantic    75%          5 方法     ║  │
│  ║  Button                  8        Direct      95%          0 方法     ║  │
│  ║  RecyclerView            35       Bridge      50%          18 方法    ║  │
│  ║  RecyclerView.Adapter    12       Bridge      40%          7 方法     ║  │
│  ║  LinearLayout            10       Semantic    90%          1 方法     ║  │
│  ║  FrameLayout             8        Semantic    90%          1 方法     ║  │
│  ║  ConstraintLayout        15       Bridge      60%          6 方法     ║  │
│  ║  SwipeRefreshLayout      6        Semantic    80%          1 方法     ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  小计                    224      -           ~70%         73 方法    ║  │
│  ║                                                                        ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ 三、数据存储 API (P1)                                                   ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                        ║  │
│  ║  类名                    方法数    映射类型    CRAFT 覆盖    人工介入   ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  SharedPreferences       12       Semantic    95%          1 方法     ║  │
│  ║  SQLiteDatabase          20       Bridge      75%          5 方法     ║  │
│  ║  SQLiteOpenHelper        6        Bridge      70%          2 方法     ║  │
│  ║  Cursor                  15       Bridge      80%          3 方法     ║  │
│  ║  ContentValues           10       Semantic    90%          1 方法     ║  │
│  ║  ContentResolver         18       Bridge      60%          7 方法     ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  小计                    81       -           ~78%         19 方法    ║  │
│  ║                                                                        ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ 四、网络 API (P1)                                                       ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                        ║  │
│  ║  类名                    方法数    映射类型    CRAFT 覆盖    人工介入   ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  HttpURLConnection       15       Semantic    85%          2 方法     ║  │
│  ║  URL                     8        Direct      95%          0 方法     ║  │
│  ║  Socket                  12       Semantic    80%          2 方法     ║  │
│  ║  SSLSocket               10       Semantic    75%          3 方法     ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  小计                    45       -           ~84%         7 方法     ║  │
│  ║  注: OkHttp/Retrofit 为纯 Java 库，可直接使用                          ║  │
│  ║                                                                        ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ 五、多媒体 API (P1-P2)                                                  ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                        ║  │
│  ║  类名                    方法数    映射类型    CRAFT 覆盖    人工介入   ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  Bitmap                  30       Bridge      65%          11 方法    ║  │
│  ║  BitmapFactory           8        Semantic    80%          2 方法     ║  │
│  ║  Canvas                  40       Bridge      50%          20 方法    ║  │
│  ║  MediaPlayer             25       Bridge      55%          11 方法    ║  │
│  ║  Camera2 API             50       Bridge      40%          30 方法    ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  小计                    153      -           ~52%         74 方法    ║  │
│  ║                                                                        ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ 六、系统服务 API (P1-P2)                                                ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                        ║  │
│  ║  类名                    方法数    映射类型    CRAFT 覆盖    人工介入   ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  NotificationManager     10       Bridge      70%          3 方法     ║  │
│  ║  Notification.Builder    15       Bridge      65%          5 方法     ║  │
│  ║  AlarmManager            8        Semantic    75%          2 方法     ║  │
│  ║  PackageManager          20       Bridge      60%          8 方法     ║  │
│  ║  Handler/Looper          12       Semantic    80%          2 方法     ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  小计                    65       -           ~70%         20 方法    ║  │
│  ║                                                                        ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ 七、WebView API (P2)                                                    ║  │
│  ╠═══════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                        ║  │
│  ║  类名                    方法数    映射类型    CRAFT 覆盖    人工介入   ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  WebView                 30       Bridge      55%          14 方法    ║  │
│  ║  WebViewClient           10       Bridge      60%          4 方法     ║  │
│  ║  WebChromeClient         12       Bridge      55%          5 方法     ║  │
│  ║  WebSettings             15       Semantic    70%          5 方法     ║  │
│  ║  JavascriptInterface     5        Bridge      50%          3 方法     ║  │
│  ║  ─────────────────────────────────────────────────────────────────────║  │
│  ║  小计                    72       -           ~58%         31 方法    ║  │
│  ║                                                                        ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
│  ════════════════════════════════════════════════════════════════════════   │
│  总计                                                                        │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  API 总数:              ~746 方法                                            │
│  CRAFT 自动覆盖:        ~68% (~507 方法)                                     │
│  需人工介入:            ~32% (~239 方法)                                     │
│                                                                              │
│  其中:                                                                       │
│  - Direct 映射:         ~15% (自动)                                          │
│  - Semantic 映射:       ~35% (自动，需审核)                                  │
│  - Bridge 映射:         ~40% (部分自动 + AI 辅助)                            │
│  - Shim 映射:           ~8% (需要手动实现)                                   │
│  - 不支持:              ~2% (需替代方案)                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 开发里程碑

```
Phase 1: 基础框架 (4 周)
├── Week 1-2: craft-core + craft-parser
│   ├── 完成核心数据结构定义
│   ├── 完成 Java 解析器
│   └── 完成 ArkTS 声明文件解析器
└── Week 3-4: craft-analyzer
    ├── 完成相似度计算引擎
    ├── 完成基础映射生成
    └── 完成生命周期分析器

Phase 2: 代码生成 (3 周)
├── Week 5-6: craft-generator
│   ├── 完成 Java 适配器模板
│   ├── 完成测试生成器
│   └── 完成文档生成器
└── Week 7: craft-ai
    ├── 完成 Claude API 集成
    └── 完成复杂映射 Prompt 设计

Phase 3: 垫片库 (4 周)
├── Week 8-9: 核心垫片
│   ├── Activity/Fragment 垫片
│   ├── View 基础垫片
│   └── 数据存储垫片
└── Week 10-11: 扩展垫片
    ├── RecyclerView 垫片
    ├── 多媒体垫片
    └── WebView 垫片

Phase 4: 流水线 (2 周)
├── Week 12: craft-pipeline
│   ├── 完成任务调度器
│   └── 完成进度追踪
└── Week 13: craft-cli
    └── 完成命令行工具

Phase 5: 验证与优化 (3 周)
├── Week 14-15: 百度贴吧适配验证
│   ├── 生成全部适配器
│   ├── 运行测试套件
│   └── 修复问题
└── Week 16: 性能优化
    ├── 解析性能优化
    └── 生成质量优化

总计: 16 周 (4 个月)
```

---

## 十一、文档版本

| 版本 | 日期 | 修改内容 |
|------|------|---------|
| 1.0.0 | 2026-01-20 | 初始版本 |

---

*CRAFT - AI 驱动的跨平台 API 适配层生成框架*
