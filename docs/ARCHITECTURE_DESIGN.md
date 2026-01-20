# CRAFT 技术架构设计文档

> **CRAFT Runs Any Framework Technology**
> 版本: 2.0.0 | 日期: 2026-01-20

## 一、项目愿景与目标

### 1.1 项目定位

CRAFT 是一个 **AI 驱动的自动化 API 适配层生成系统**，旨在通过高度自动化的方式，大规模生成跨平台 API 转接代码（如 Android API 到 HarmonyOS API）。

### 1.2 核心目标

| 目标 | 描述 | 衡量标准 |
|------|------|---------|
| **规模化** | 支持 30,000+ API 的自动分析与适配 | API 覆盖率 > 90% |
| **自动化** | 最小化人工干预，AI 驱动的代码生成 | 人工介入率 < 10% |
| **高质量** | 生成的代码符合生产标准 | 自动化测试通过率 > 95% |
| **高性能** | 极低的运行时开销 | 性能损耗 < 5% |
| **内存安全** | 零内存泄漏，零数据竞争 | Rust 编译时保证 |

### 1.3 设计原则

```
┌─────────────────────────────────────────────────────────────────┐
│                      CRAFT 设计原则                               │
├─────────────────────────────────────────────────────────────────┤
│  1. AI First      - AI 是核心生产力，人是审核者                  │
│  2. Safety First  - 内存安全、类型安全、并发安全                 │
│  3. Spec Driven   - 基于形式化规格的代码生成                     │
│  4. Zero Cost     - 零成本抽象，编译时优化                       │
│  5. Verifiable    - 可验证、可测试、可追溯                       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 为什么选择 Rust

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rust 技术优势                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔒 内存安全                                                     │
│  ├── 所有权系统在编译时防止内存泄漏                              │
│  ├── 借用检查器防止悬垂指针和数据竞争                            │
│  └── 无需垃圾回收，确定性内存管理                                │
│                                                                 │
│  ⚡ 极致性能                                                     │
│  ├── 零成本抽象，与 C/C++ 同级性能                               │
│  ├── 无运行时开销，适合系统级代码                                │
│  └── LLVM 后端，高度优化的机器码                                 │
│                                                                 │
│  ✅ 可验证性                                                     │
│  ├── 强类型系统在编译时捕获大量错误                              │
│  ├── 模式匹配确保穷尽性检查                                      │
│  ├── Result/Option 类型强制错误处理                              │
│  └── 丰富的测试框架和文档测试                                    │
│                                                                 │
│  🔧 工具链                                                       │
│  ├── Cargo: 优秀的包管理和构建系统                               │
│  ├── rustfmt/clippy: 代码格式化和静态分析                        │
│  └── 跨平台编译支持                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、系统总体架构

### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       CRAFT System Architecture (Rust)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Layer 1: Input Sources                       │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Android SDK  │  │ HarmonyOS SDK│  │ API Documentation    │   │    │
│  │  │ Source Code  │  │ Source Code  │  │ (AOSP, OpenHarmony)  │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                Layer 2: Analysis Engine (Rust)                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ tree-sitter  │  │ Semantic     │  │ Compatibility        │   │    │
│  │  │ Parser       │  │ Analyzer     │  │ Matcher              │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                Layer 3: Knowledge Base (Rust + SQLite)           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ API Specs    │  │ Mapping      │  │ Pattern              │   │    │
│  │  │ (serde)      │  │ Rules DB     │  │ Library              │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │               Layer 4: AI Generation Engine (Rust)               │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Claude API   │  │ Code         │  │ Template             │   │    │
│  │  │ Client       │  │ Generator    │  │ Engine (Tera)        │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                Layer 5: Quality Assurance (Rust)                 │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Test         │  │ Validator    │  │ Benchmark            │   │    │
│  │  │ Generator    │  │ Engine       │  │ Suite                │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Layer 6: Output Artifacts                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Shim Layer   │  │ Native       │  │ Documentation        │   │    │
│  │  │ Libraries    │  │ Bridges      │  │ & Reports            │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流架构

```
Android API Spec                    HarmonyOS API Spec
      │                                    │
      ▼                                    ▼
┌─────────────┐                    ┌─────────────┐
│ tree-sitter │                    │ tree-sitter │
│ Java Parser │                    │ ArkTS Parser│
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       ▼                                  ▼
┌─────────────────────────────────────────────────┐
│         Semantic Mapping Engine (Rust)           │
│  ┌─────────────────────────────────────────┐    │
│  │  Android API  ←──mapping──→ Harmony API  │    │
│  │  Strongly typed with serde + validation  │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │   AI Code Generator     │
        │   (reqwest + Claude)    │
        └───────────┬─────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Adapter │ │ Bridge  │ │  Test   │
   │  Code   │ │  Code   │ │  Code   │
   └─────────┘ └─────────┘ └─────────┘
```

---

## 三、核心组件详细设计

### 3.1 API 分析引擎 (Analysis Engine)

#### 3.1.1 功能职责

```rust
/// API 分析引擎
/// 负责解析和分析 SDK 源码，提取 API 规格
pub struct ApiAnalyzer {
    java_parser: TreeSitterParser,
    arkts_parser: TreeSitterParser,
    semantic_engine: SemanticEngine,
}

impl ApiAnalyzer {
    /// 解析 SDK 源码，提取所有公开 API
    pub fn parse_sdk(&self, sdk_path: &Path) -> Result<ApiRepository, AnalyzerError> {
        let files = self.discover_source_files(sdk_path)?;
        let apis = files
            .par_iter()  // 使用 rayon 并行处理
            .map(|file| self.parse_file(file))
            .collect::<Result<Vec<_>, _>>()?;

        Ok(ApiRepository::from_specs(apis))
    }

    /// 使用 AI 分析 API 的语义含义
    pub async fn analyze_semantics(&self, api: &ApiSpec) -> Result<SemanticInfo, AnalyzerError> {
        self.semantic_engine.analyze(api).await
    }

    /// 构建 API 依赖关系图
    pub fn build_dependency_graph(&self, apis: &[ApiSpec]) -> DependencyGraph {
        DependencyGraph::build_from(apis)
    }
}
```

#### 3.1.2 API 规格定义 (Type-Safe)

```rust
use serde::{Deserialize, Serialize};

/// API 规格定义 - 强类型、可序列化
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiSpec {
    pub platform: Platform,
    pub version: String,
    pub package: String,
    pub class_name: String,
    pub methods: Vec<MethodSpec>,
    pub fields: Vec<FieldSpec>,
    #[serde(default)]
    pub annotations: Vec<String>,
    #[serde(default)]
    pub semantic_tags: Vec<SemanticTag>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MethodSpec {
    pub name: String,
    pub signature: String,
    pub params: Vec<ParamSpec>,
    pub return_type: TypeSpec,
    pub throws: Vec<String>,
    pub visibility: Visibility,
    #[serde(default)]
    pub is_static: bool,
    #[serde(default)]
    pub is_deprecated: bool,
    pub since: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParamSpec {
    pub name: String,
    #[serde(rename = "type")]
    pub param_type: TypeSpec,
    #[serde(default)]
    pub nullable: bool,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum Platform {
    Android,
    Harmony,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum Visibility {
    Public,
    Protected,
    Private,
    Package,
}
```

#### 3.1.3 使用 tree-sitter 进行高性能解析

```rust
use tree_sitter::{Parser, Language};

pub struct TreeSitterParser {
    parser: Parser,
    language: Language,
}

impl TreeSitterParser {
    pub fn new_java() -> Result<Self, ParserError> {
        let mut parser = Parser::new();
        let language = tree_sitter_java::language();
        parser.set_language(language)?;
        Ok(Self { parser, language })
    }

    pub fn parse_file(&mut self, source: &str) -> Result<ParsedAst, ParserError> {
        let tree = self.parser
            .parse(source, None)
            .ok_or(ParserError::ParseFailed)?;

        let root = tree.root_node();
        self.extract_api_specs(root, source)
    }

    fn extract_api_specs(&self, node: tree_sitter::Node, source: &str) -> Result<ParsedAst, ParserError> {
        // 递归遍历 AST，提取类、方法、字段定义
        // ...
    }
}
```

### 3.2 语义映射引擎 (Semantic Mapping Engine)

#### 3.2.1 映射规则定义

```rust
/// 映射规则 - 强类型定义
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingRule {
    pub id: String,
    pub source: ApiReference,
    pub target: ApiReference,
    pub mapping_type: MappingType,
    pub confidence: f64,
    pub transformations: Vec<Transformation>,
    #[serde(default)]
    pub requires_bridge: bool,
    pub notes: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum MappingType {
    /// 1:1 直接映射
    Direct,
    /// 语义等价映射
    Semantic,
    /// 需要参数转换
    Transform,
    /// 需要桥接代码
    Bridge,
    /// 需要模拟实现
    Shim,
    /// 无法映射
    Unsupported,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transformation {
    pub kind: TransformKind,
    pub source_param: Option<String>,
    pub target_param: Option<String>,
    pub expression: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TransformKind {
    TypeConversion,
    ParameterReorder,
    ParameterMerge,
    ParameterSplit,
    DefaultValue,
    CustomCode,
}
```

#### 3.2.2 映射引擎实现

```rust
pub struct MappingEngine {
    rules: RwLock<HashMap<String, MappingRule>>,
    ai_client: Arc<ClaudeClient>,
}

impl MappingEngine {
    /// 查找最佳映射
    pub async fn find_mapping(
        &self,
        source_api: &ApiSpec,
        target_apis: &[ApiSpec],
    ) -> Result<Option<MappingRule>, MappingError> {
        // 1. 先检查已知规则
        if let Some(rule) = self.find_known_mapping(source_api) {
            return Ok(Some(rule));
        }

        // 2. 尝试名称相似度匹配
        if let Some(rule) = self.find_by_similarity(source_api, target_apis) {
            if rule.confidence > 0.8 {
                return Ok(Some(rule));
            }
        }

        // 3. 使用 AI 进行语义匹配
        self.ai_semantic_match(source_api, target_apis).await
    }

    /// 批量映射 - 使用 rayon 并行处理
    pub async fn batch_map(
        &self,
        sources: &[ApiSpec],
        targets: &[ApiSpec],
    ) -> Vec<Result<MappingRule, MappingError>> {
        // 对于简单映射使用并行处理
        let (simple, complex): (Vec<_>, Vec<_>) = sources
            .iter()
            .partition(|api| self.is_simple_mapping(api));

        let simple_results: Vec<_> = simple
            .par_iter()
            .map(|api| self.find_known_mapping(api).ok_or(MappingError::NotFound))
            .collect();

        // 对于复杂映射使用 AI（带速率限制）
        let complex_results = self.batch_ai_map(&complex, targets).await;

        // 合并结果
        [simple_results, complex_results].concat()
    }
}
```

### 3.3 AI 代码生成引擎

#### 3.3.1 Claude API 客户端

```rust
use reqwest::Client;
use serde_json::json;

pub struct ClaudeClient {
    client: Client,
    api_key: String,
    model: String,
    rate_limiter: RateLimiter,
}

impl ClaudeClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
            model: "claude-opus-4-5-20251101".to_string(),
            rate_limiter: RateLimiter::new(50), // 50 RPM
        }
    }

    pub async fn generate_adapter(
        &self,
        context: &AdapterContext,
    ) -> Result<GeneratedCode, AiError> {
        self.rate_limiter.acquire().await;

        let prompt = self.build_adapter_prompt(context);

        let response = self.client
            .post("https://api.anthropic.com/v1/messages")
            .header("x-api-key", &self.api_key)
            .header("anthropic-version", "2023-06-01")
            .json(&json!({
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            }))
            .send()
            .await?;

        let result: ApiResponse = response.json().await?;
        self.parse_generated_code(&result)
    }
}
```

#### 3.3.2 代码生成器

```rust
use tera::{Tera, Context};

pub struct CodeGenerator {
    templates: Tera,
    ai_client: Arc<ClaudeClient>,
}

impl CodeGenerator {
    pub fn new(template_dir: &Path) -> Result<Self, GeneratorError> {
        let templates = Tera::new(
            template_dir.join("**/*.tera").to_str().unwrap()
        )?;

        Ok(Self {
            templates,
            ai_client: Arc::new(ClaudeClient::new(
                std::env::var("ANTHROPIC_API_KEY")?
            )),
        })
    }

    /// 生成适配器代码
    pub async fn generate(
        &self,
        mapping: &MappingRule,
        source_api: &ApiSpec,
        target_api: &ApiSpec,
    ) -> Result<GeneratedAdapter, GeneratorError> {
        match mapping.mapping_type {
            MappingType::Direct => self.generate_direct_adapter(mapping, source_api, target_api),
            MappingType::Semantic | MappingType::Transform => {
                self.generate_transform_adapter(mapping, source_api, target_api)
            }
            MappingType::Bridge | MappingType::Shim => {
                self.generate_with_ai(mapping, source_api, target_api).await
            }
            MappingType::Unsupported => Err(GeneratorError::Unsupported),
        }
    }

    fn generate_direct_adapter(
        &self,
        mapping: &MappingRule,
        source: &ApiSpec,
        target: &ApiSpec,
    ) -> Result<GeneratedAdapter, GeneratorError> {
        let mut context = Context::new();
        context.insert("source", source);
        context.insert("target", target);
        context.insert("mapping", mapping);
        context.insert("timestamp", &chrono::Utc::now().to_rfc3339());

        let code = self.templates.render("adapter_java.tera", &context)?;

        Ok(GeneratedAdapter {
            code,
            confidence: mapping.confidence,
            requires_review: mapping.confidence < 0.9,
        })
    }
}
```

### 3.4 测试生成框架

```rust
pub struct TestGenerator {
    templates: Tera,
}

impl TestGenerator {
    /// 生成单元测试
    pub fn generate_unit_tests(
        &self,
        adapter: &GeneratedAdapter,
        source_api: &ApiSpec,
    ) -> Result<GeneratedTests, TestGenError> {
        let test_cases: Vec<TestCase> = source_api
            .methods
            .iter()
            .flat_map(|method| self.generate_method_tests(method))
            .collect();

        let mut context = Context::new();
        context.insert("adapter", adapter);
        context.insert("test_cases", &test_cases);

        let code = self.templates.render("test_java.tera", &context)?;

        Ok(GeneratedTests { code, test_cases })
    }

    fn generate_method_tests(&self, method: &MethodSpec) -> Vec<TestCase> {
        let mut tests = vec![
            // 基本功能测试
            TestCase::new(&format!("test_{}_basic", method.name)),
        ];

        // 参数边界测试
        for param in &method.params {
            if param.nullable {
                tests.push(TestCase::new(&format!(
                    "test_{}_{}_null",
                    method.name, param.name
                )));
            }
        }

        // 异常测试
        for exception in &method.throws {
            tests.push(TestCase::new(&format!(
                "test_{}_throws_{}",
                method.name,
                exception.split('.').last().unwrap_or(exception)
            )));
        }

        tests
    }
}
```

---

## 四、并发与性能设计

### 4.1 并发模型

```rust
use tokio::sync::{Semaphore, RwLock};
use rayon::prelude::*;

pub struct BatchProcessor {
    /// CPU 密集型任务使用 rayon 线程池
    cpu_pool: rayon::ThreadPool,
    /// IO 密集型任务使用 tokio
    io_semaphore: Semaphore,
    /// AI API 速率限制
    ai_rate_limiter: RateLimiter,
}

impl BatchProcessor {
    pub async fn process_batch(
        &self,
        apis: Vec<ApiSpec>,
    ) -> Vec<Result<GeneratedAdapter, ProcessError>> {
        // 分类: CPU 密集型 vs IO 密集型
        let (cpu_bound, io_bound): (Vec<_>, Vec<_>) = apis
            .into_iter()
            .partition(|api| self.is_cpu_bound(api));

        // CPU 密集型: 使用 rayon 并行处理
        let cpu_results: Vec<_> = cpu_bound
            .par_iter()
            .map(|api| self.process_cpu_bound(api))
            .collect();

        // IO 密集型: 使用 tokio 异步处理
        let io_results = futures::future::join_all(
            io_bound.iter().map(|api| self.process_io_bound(api))
        ).await;

        [cpu_results, io_results].concat()
    }
}

/// 速率限制器 - 令牌桶算法
pub struct RateLimiter {
    tokens: AtomicU32,
    max_tokens: u32,
    refill_interval: Duration,
}

impl RateLimiter {
    pub async fn acquire(&self) {
        loop {
            let current = self.tokens.load(Ordering::Relaxed);
            if current > 0 {
                if self.tokens
                    .compare_exchange(current, current - 1, Ordering::SeqCst, Ordering::Relaxed)
                    .is_ok()
                {
                    return;
                }
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    }
}
```

### 4.2 内存管理

```rust
/// 使用 Arena 分配器优化大量小对象分配
use bumpalo::Bump;

pub struct ParsingContext<'a> {
    arena: &'a Bump,
    source: &'a str,
}

impl<'a> ParsingContext<'a> {
    /// 在 Arena 中分配字符串，避免频繁堆分配
    pub fn intern_string(&self, s: &str) -> &'a str {
        self.arena.alloc_str(s)
    }
}

/// 使用 Cow 避免不必要的克隆
use std::borrow::Cow;

pub struct ApiReference<'a> {
    pub package: Cow<'a, str>,
    pub class: Cow<'a, str>,
    pub method: Option<Cow<'a, str>>,
}
```

---

## 五、项目目录结构

```
CRAFT/
├── Cargo.toml                      # 工作空间配置
├── Cargo.lock                      # 依赖锁定
├── README.md                       # 项目说明
├── CLAUDE.md                       # Claude Code 开发规范
│
├── crates/                         # Rust crates
│   ├── craft-core/                 # 核心数据结构
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── api_spec.rs         # API 规格定义
│   │       ├── mapping.rs          # 映射规则定义
│   │       └── error.rs            # 错误类型
│   │
│   ├── craft-parser/               # SDK 解析器
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── java.rs             # Java/Kotlin 解析
│   │       ├── arkts.rs            # ArkTS 解析
│   │       └── tree_sitter.rs      # tree-sitter 集成
│   │
│   ├── craft-analyzer/             # 语义分析器
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── semantic.rs         # 语义分析
│   │       └── matcher.rs          # 匹配算法
│   │
│   ├── craft-generator/            # 代码生成器
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── adapter.rs          # 适配器生成
│   │       ├── test.rs             # 测试生成
│   │       └── template.rs         # 模板引擎
│   │
│   ├── craft-ai/                   # AI 集成
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── claude.rs           # Claude API 客户端
│   │       └── prompt.rs           # 提示词管理
│   │
│   ├── craft-pipeline/             # 自动化流水线
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── orchestrator.rs     # 流程编排
│   │       ├── batch.rs            # 批量处理
│   │       └── incremental.rs      # 增量更新
│   │
│   └── craft-cli/                  # 命令行工具
│       ├── Cargo.toml
│       └── src/
│           └── main.rs
│
├── docs/                           # 设计文档
│   ├── ARCHITECTURE_DESIGN.md      # 本文档
│   ├── FEASIBILITY_ANALYSIS.md     # 可行性分析
│   └── API_MAPPING_SPEC.md         # API 映射规格
│
├── templates/                      # 代码模板 (Tera)
│   ├── adapter_java.tera
│   ├── adapter_kotlin.tera
│   ├── test_java.tera
│   └── prompts/                    # AI 提示词
│       └── generate_adapter.md
│
├── specs/                          # API 规格 (YAML/JSON)
│   ├── android/
│   └── harmony/
│
├── configs/                        # 配置文件
│   ├── craft_config.toml           # 主配置
│   └── mapping_rules.yaml          # 映射规则
│
├── tests/                          # 集成测试
│   ├── integration/
│   └── fixtures/
│
└── output/                         # 输出产物
    ├── adapters/
    ├── reports/
    └── benchmarks/
```

---

## 六、关键技术选型

### 6.1 技术栈

| 层次 | 技术选型 | 理由 |
|------|---------|------|
| **语言** | Rust 1.75+ | 内存安全、高性能、可验证性 |
| **异步运行时** | Tokio | 高性能异步 IO |
| **并行计算** | Rayon | 数据并行处理 |
| **解析器** | tree-sitter | 增量解析、多语言支持 |
| **序列化** | serde + serde_json/yaml | 高性能、类型安全 |
| **模板引擎** | Tera | Jinja2 兼容、Rust 原生 |
| **HTTP 客户端** | reqwest | 异步、连接池 |
| **数据库** | SQLite (rusqlite) | 轻量级、嵌入式 |
| **CLI** | clap | 声明式命令行解析 |
| **日志** | tracing | 结构化日志、性能分析 |
| **错误处理** | thiserror + anyhow | 类型安全的错误处理 |

### 6.2 Cargo.toml 工作空间配置

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

[workspace.package]
version = "0.1.0"
edition = "2021"
rust-version = "1.75"
license = "Apache-2.0"
repository = "https://github.com/lisihao/CRAFT"

[workspace.dependencies]
# 异步运行时
tokio = { version = "1.35", features = ["full"] }
futures = "0.3"

# 并行计算
rayon = "1.8"

# 序列化
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
serde_yaml = "0.9"
toml = "0.8"

# 解析
tree-sitter = "0.20"
tree-sitter-java = "0.20"

# 模板
tera = "1.19"

# HTTP
reqwest = { version = "0.11", features = ["json"] }

# 数据库
rusqlite = { version = "0.30", features = ["bundled"] }

# CLI
clap = { version = "4.4", features = ["derive"] }

# 日志
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

# 错误处理
thiserror = "1.0"
anyhow = "1.0"

# 工具
chrono = { version = "0.4", features = ["serde"] }
uuid = { version = "1.6", features = ["v4", "serde"] }
```

### 6.3 错误处理设计

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CraftError {
    #[error("Parse error: {0}")]
    Parse(#[from] ParseError),

    #[error("Mapping error: {0}")]
    Mapping(#[from] MappingError),

    #[error("Generation error: {0}")]
    Generation(#[from] GeneratorError),

    #[error("AI error: {0}")]
    Ai(#[from] AiError),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

#[derive(Error, Debug)]
pub enum ParseError {
    #[error("Failed to parse file: {path}")]
    FileParseFailed { path: PathBuf },

    #[error("Invalid syntax at line {line}, column {column}")]
    InvalidSyntax { line: usize, column: usize },

    #[error("Unsupported language: {0}")]
    UnsupportedLanguage(String),
}

// 使用 Result 类型别名简化
pub type Result<T> = std::result::Result<T, CraftError>;
```

---

## 七、实施路线图

### Phase 1: 基础设施 (Foundation)
- [ ] 搭建 Cargo workspace
- [ ] 实现 craft-core 核心数据结构
- [ ] 集成 tree-sitter 解析器
- [ ] 建立基础 CLI 框架

### Phase 2: 解析与分析 (Parser & Analyzer)
- [ ] 实现 Java/Kotlin 解析器
- [ ] 实现 ArkTS 解析器
- [ ] 建立 API 规格数据库
- [ ] 实现基础语义分析

### Phase 3: AI 集成 (AI Integration)
- [ ] 集成 Claude API
- [ ] 实现提示词模板系统
- [ ] 建立速率限制和重试机制
- [ ] 实现 AI 辅助映射

### Phase 4: 代码生成 (Code Generation)
- [ ] 实现 Tera 模板系统
- [ ] 实现适配器生成器
- [ ] 实现测试生成器
- [ ] 建立质量验证流程

### Phase 5: 流水线 (Pipeline)
- [ ] 实现批量处理器
- [ ] 实现增量更新
- [ ] 建立 CI/CD 流程
- [ ] 性能优化和基准测试

---

## 八、性能目标

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| 解析速度 | > 10,000 files/sec | 单线程解析吞吐量 |
| 批量映射 | > 1,000 APIs/sec | 含 AI 调用的端到端 |
| 内存使用 | < 500MB | 处理 30,000 API 时 |
| 生成代码性能 | < 5% overhead | vs 手写适配器 |
| 编译时间 | < 30s (release) | 完整项目编译 |

---

## 九、安全性保证

```rust
// Rust 编译时保证
// ✅ 内存安全 - 所有权系统
// ✅ 线程安全 - Send/Sync traits
// ✅ 空指针安全 - Option 类型
// ✅ 错误处理 - Result 类型

// 示例: 并发安全的缓存
use std::sync::Arc;
use tokio::sync::RwLock;

pub struct SafeCache<K, V> {
    inner: Arc<RwLock<HashMap<K, V>>>,
}

impl<K: Eq + Hash, V: Clone> SafeCache<K, V> {
    pub async fn get(&self, key: &K) -> Option<V> {
        self.inner.read().await.get(key).cloned()
    }

    pub async fn insert(&self, key: K, value: V) {
        self.inner.write().await.insert(key, value);
    }
}
// 编译器保证: 无数据竞争，无死锁风险
```

---

*文档版本: 2.0.0*
*技术栈: Rust*
*最后更新: 2026-01-20*
*作者: CRAFT Team (AI-assisted)*
