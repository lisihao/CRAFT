# NOAH 技术架构设计文档

> **NOAH Opens Android on Harmony**
> 版本: 1.0.0 | 日期: 2026-01-18

## 一、项目愿景与目标

### 1.1 项目定位

NOAH 是一个 **AI 驱动的自动化 API 适配层生成系统**，旨在通过高度自动化的方式，大规模生成 Android API 到 HarmonyOS API 的转接代码。

### 1.2 核心目标

| 目标 | 描述 | 衡量标准 |
|------|------|---------|
| **规模化** | 支持 30,000+ Android API 的自动分析与适配 | API 覆盖率 > 90% |
| **自动化** | 最小化人工干预，AI 驱动的代码生成 | 人工介入率 < 10% |
| **高质量** | 生成的代码符合生产标准 | 自动化测试通过率 > 95% |
| **可维护** | 随 Android/HarmonyOS 版本演进持续更新 | 版本同步延迟 < 1 周 |

### 1.3 设计原则

```
┌─────────────────────────────────────────────────────────────────┐
│                      NOAH 设计原则                               │
├─────────────────────────────────────────────────────────────────┤
│  1. AI First      - AI 是核心生产力，人是审核者                  │
│  2. Spec Driven   - 基于形式化规格的代码生成                     │
│  3. Test Driven   - 每个适配器都有对应的自动化测试                │
│  4. Incremental   - 支持增量式适配，优先高频 API                  │
│  5. Observable    - 全流程可观测、可追溯、可回滚                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、系统总体架构

### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           NOAH System Architecture                       │
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
│  │                     Layer 2: Analysis Engine                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ API Parser   │  │ Semantic     │  │ Compatibility        │   │    │
│  │  │ & Extractor  │  │ Analyzer     │  │ Matcher              │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Layer 3: Knowledge Base                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ API Specs    │  │ Mapping      │  │ Pattern              │   │    │
│  │  │ Repository   │  │ Rules DB     │  │ Library              │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                  Layer 4: AI Generation Engine                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Claude Code  │  │ Code         │  │ Adaptation           │   │    │
│  │  │ Agent        │  │ Generator    │  │ Optimizer            │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   Layer 5: Quality Assurance                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │    │
│  │  │ Unit Test    │  │ Integration  │  │ Compatibility        │   │    │
│  │  │ Generator    │  │ Test Suite   │  │ Validator            │   │    │
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
│ API Parser  │                    │ API Parser  │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       ▼                                  ▼
┌─────────────────────────────────────────────────┐
│              Semantic Mapping Engine             │
│  ┌─────────────────────────────────────────┐    │
│  │  Android API  ←──mapping──→ Harmony API  │    │
│  │  android.app.Activity    ohos.app.UIAbility │
│  │  android.content.Intent  ohos.app.Want      │
│  │  ...                     ...                │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │   AI Code Generator     │
        │   (Claude Code Agent)   │
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

```python
class APIAnalyzer:
    """
    API 分析引擎负责：
    1. 解析 Android/HarmonyOS SDK 源码
    2. 提取 API 签名、参数、返回值、异常
    3. 分析 API 语义（通过文档、命名、使用模式）
    4. 识别 API 依赖关系图
    """

    def parse_sdk(self, sdk_path: str) -> APIRepository:
        """解析 SDK 源码，提取所有公开 API"""
        pass

    def analyze_semantics(self, api: APISpec) -> SemanticInfo:
        """使用 AI 分析 API 的语义含义"""
        pass

    def build_dependency_graph(self, apis: List[APISpec]) -> DependencyGraph:
        """构建 API 依赖关系图"""
        pass
```

#### 3.1.2 API 规格定义

```yaml
# API 规格示例 (YAML Schema)
api_spec:
  platform: android
  version: "14"
  package: android.app
  class: Activity
  methods:
    - name: startActivity
      signature: "void startActivity(Intent intent)"
      params:
        - name: intent
          type: android.content.Intent
          nullable: false
          description: "The intent to start"
      returns:
        type: void
      throws:
        - android.content.ActivityNotFoundException
      since: API 1
      deprecated: false
      semantic_tags:
        - navigation
        - lifecycle
        - inter_component
```

### 3.2 语义映射引擎 (Semantic Mapping Engine)

#### 3.2.1 映射策略分类

```
┌────────────────────────────────────────────────────────────────┐
│                    API 映射策略矩阵                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  策略类型          占比估计    复杂度    AI 介入程度            │
│  ─────────────────────────────────────────────────────         │
│  1:1 直接映射      ~30%       低        低 (规则匹配)           │
│  1:N 分解映射      ~20%       中        中 (模式识别)           │
│  N:1 合并映射      ~15%       中        中 (语义分析)           │
│  语义等价映射      ~20%       高        高 (AI 推理)            │
│  桥接/模拟映射     ~10%       很高      很高 (AI 生成)          │
│  无法映射          ~5%        -         需人工决策              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

#### 3.2.2 映射规则示例

```python
# 映射规则定义
mapping_rules = {
    # 1:1 直接映射
    "direct": [
        {
            "android": "android.app.Activity",
            "harmony": "ohos.app.UIAbility",
            "confidence": 0.95,
            "notes": "Core lifecycle mapping"
        },
        {
            "android": "android.content.Intent",
            "harmony": "ohos.app.Want",
            "confidence": 0.90,
            "notes": "Intent → Want with parameter translation"
        }
    ],

    # 语义等价映射 (需要 AI 分析)
    "semantic_equivalent": [
        {
            "android": "android.widget.Toast.makeText().show()",
            "harmony": "promptAction.showToast()",
            "transform": "API_STYLE_CHANGE",
            "ai_generated": True
        }
    ],

    # 桥接映射 (需要生成桥接代码)
    "bridge": [
        {
            "android": "android.database.sqlite.SQLiteDatabase",
            "harmony": "relationalStore.RdbStore",
            "bridge_required": True,
            "bridge_complexity": "HIGH"
        }
    ]
}
```

### 3.3 AI 代码生成引擎 (AI Generation Engine)

#### 3.3.1 Claude Code Agent 集成

```
┌─────────────────────────────────────────────────────────────────┐
│                Claude Code Agent 工作流                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  输入                                                            │
│  ├── API Spec (Android)                                         │
│  ├── API Spec (HarmonyOS)                                       │
│  ├── Mapping Rules                                              │
│  ├── Code Templates                                             │
│  └── Historical Patterns                                        │
│                                                                 │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Claude Code Agent Pipeline                  │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│  │  │ Analyze │→ │ Design  │→ │Generate │→ │ Verify  │    │   │
│  │  │ Context │  │ Adapter │  │  Code   │  │ Output  │    │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  输出                                                            │
│  ├── Adapter Code (.java/.kt/.ets)                             │
│  ├── Unit Tests                                                 │
│  ├── Documentation                                              │
│  └── Confidence Score                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 代码生成提示词模板

```markdown
## Adapter Generation Prompt Template

你是一个专业的系统级代码生成专家，负责生成 Android API 到 HarmonyOS API 的适配代码。

### 输入信息

**Android API 规格:**
```
{android_api_spec}
```

**对应的 HarmonyOS API:**
```
{harmony_api_spec}
```

**映射规则:**
```
{mapping_rules}
```

### 生成要求

1. 生成一个完整的 Adapter 类，实现 Android API 接口
2. 内部调用对应的 HarmonyOS API
3. 处理参数类型转换
4. 处理异常映射
5. 保持线程安全性
6. 添加必要的注释

### 输出格式

```java
// Auto-generated by NOAH
// Source: {android_class}
// Target: {harmony_class}
// Confidence: {confidence_score}

package noah.adapters.{package};

{generated_code}
```
```

### 3.4 自动化测试框架

#### 3.4.1 测试生成策略

```python
class TestGenerator:
    """
    自动化测试生成器
    为每个生成的 Adapter 自动生成对应的测试用例
    """

    def generate_unit_tests(self, adapter: AdapterCode) -> List[TestCase]:
        """
        生成单元测试：
        1. 方法签名兼容性测试
        2. 参数边界测试
        3. 异常处理测试
        4. 返回值验证测试
        """
        pass

    def generate_integration_tests(self, adapter: AdapterCode) -> List[TestCase]:
        """
        生成集成测试：
        1. 与 HarmonyOS 真实 API 的集成测试
        2. 生命周期测试
        3. 并发测试
        """
        pass

    def generate_compatibility_tests(self,
                                     android_app: APK,
                                     adapter: AdapterCode) -> List[TestCase]:
        """
        生成兼容性测试：
        使用真实 Android 应用验证适配器行为
        """
        pass
```

#### 3.4.2 测试覆盖矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                    测试覆盖矩阵                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  测试类型          自动化率    执行环境        通过标准          │
│  ─────────────────────────────────────────────────────────      │
│  API 签名测试      100%       JVM/模拟器      100% 匹配          │
│  参数转换测试      100%       JVM/模拟器      无数据丢失          │
│  异常映射测试      100%       JVM/模拟器      异常类型正确        │
│  行为等价测试      90%        真机            行为一致            │
│  性能基准测试      100%       真机            < 10% 性能损耗      │
│  兼容性测试        80%        真机            Top 1000 App 通过   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 四、自动化流水线设计

### 4.1 CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NOAH Automation Pipeline                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Stage 1: API Discovery                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  [Monitor SDK Updates] → [Parse New APIs] → [Update Spec DB]    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  Stage 2: Mapping Analysis                                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  [Load API Specs] → [Run Semantic Matcher] → [Generate Mappings]│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  Stage 3: Code Generation                                                │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  [Select APIs] → [Claude Code Generate] → [Code Review Gate]    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  Stage 4: Quality Assurance                                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  [Generate Tests] → [Run Test Suite] → [Coverage Check]         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  Stage 5: Integration                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  [Build Shim Library] → [Run Integration Tests] → [Benchmark]   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  Stage 6: Release                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  [Human Review (if needed)] → [Version Tag] → [Publish]         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 批量处理架构

```python
class BatchProcessor:
    """
    批量处理器 - 支持大规模 API 并行处理
    """

    def __init__(self, config: BatchConfig):
        self.parallel_workers = config.workers  # 默认 10 并发
        self.batch_size = config.batch_size     # 默认 100 API/batch
        self.ai_rate_limit = config.rate_limit  # AI API 速率限制

    async def process_api_batch(self, apis: List[APISpec]) -> BatchResult:
        """
        批量处理 API 适配：
        1. 按复杂度分组
        2. 简单 API 用规则引擎处理
        3. 复杂 API 用 AI 处理
        4. 聚合结果
        """
        simple_apis, complex_apis = self.classify_apis(apis)

        # 简单 API 用规则引擎并行处理
        simple_results = await self.rule_engine.batch_process(simple_apis)

        # 复杂 API 用 AI 处理（带速率限制）
        complex_results = await self.ai_engine.batch_process(
            complex_apis,
            rate_limit=self.ai_rate_limit
        )

        return self.merge_results(simple_results, complex_results)
```

### 4.3 增量更新策略

```
┌─────────────────────────────────────────────────────────────────┐
│                    增量更新策略                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  触发条件                                                        │
│  ├── Android SDK 新版本发布                                      │
│  ├── HarmonyOS SDK 新版本发布                                    │
│  ├── 映射规则更新                                                │
│  └── Bug 修复触发重新生成                                        │
│                                                                 │
│  增量处理流程                                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │ Diff     │ →  │ Impact   │ →  │ Selective│                  │
│  │ Detection│    │ Analysis │    │ Regen    │                  │
│  └──────────┘    └──────────┘    └──────────┘                  │
│       │               │               │                         │
│       ▼               ▼               ▼                         │
│  检测变更 API    分析影响范围    仅重新生成受影响部分              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、项目目录结构

```
NOAH/
├── README.md                    # 项目说明
├── CLAUDE.md                    # Claude Code 开发规范
├── docs/                        # 设计文档
│   ├── ARCHITECTURE_DESIGN.md   # 本文档
│   ├── API_MAPPING_SPEC.md      # API 映射规格说明
│   ├── PIPELINE_DESIGN.md       # 流水线设计
│   └── TESTING_STRATEGY.md      # 测试策略
│
├── src/                         # 源代码
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   ├── api_spec.py          # API 规格定义
│   │   ├── mapping_rule.py      # 映射规则定义
│   │   └── config.py            # 配置管理
│   │
│   ├── analyzers/               # 分析器
│   │   ├── __init__.py
│   │   ├── android_parser.py    # Android SDK 解析器
│   │   ├── harmony_parser.py    # HarmonyOS SDK 解析器
│   │   └── semantic_analyzer.py # 语义分析器
│   │
│   ├── generators/              # 代码生成器
│   │   ├── __init__.py
│   │   ├── adapter_generator.py # 适配器生成器
│   │   ├── test_generator.py    # 测试生成器
│   │   └── doc_generator.py     # 文档生成器
│   │
│   ├── adapters/                # 生成的适配器代码 (输出)
│   │   ├── android.app/
│   │   ├── android.content/
│   │   └── ...
│   │
│   ├── testing/                 # 测试框架
│   │   ├── __init__.py
│   │   ├── test_runner.py       # 测试运行器
│   │   └── validators/          # 验证器
│   │
│   └── pipeline/                # 自动化流水线
│       ├── __init__.py
│       ├── orchestrator.py      # 流程编排
│       ├── batch_processor.py   # 批量处理器
│       └── incremental.py       # 增量更新
│
├── specs/                       # API 规格定义
│   ├── android/                 # Android API 规格
│   │   └── api-versions.xml
│   └── harmony/                 # HarmonyOS API 规格
│       └── api-versions.xml
│
├── templates/                   # 代码模板
│   ├── adapter_java.jinja2
│   ├── adapter_kotlin.jinja2
│   ├── test_java.jinja2
│   └── prompts/                 # AI 提示词模板
│       ├── analyze_api.md
│       ├── generate_adapter.md
│       └── generate_test.md
│
├── configs/                     # 配置文件
│   ├── mapping_rules.yaml       # 映射规则配置
│   ├── pipeline_config.yaml     # 流水线配置
│   └── ai_config.yaml           # AI 服务配置
│
├── tools/                       # 开发工具
│   ├── sdk_downloader.py        # SDK 下载工具
│   ├── spec_validator.py        # 规格验证工具
│   └── benchmark.py             # 性能基准测试
│
└── output/                      # 输出产物
    ├── adapters/                # 编译后的适配器库
    ├── reports/                 # 测试报告
    └── docs/                    # 生成的文档
```

---

## 六、关键技术选型

### 6.1 技术栈

| 层次 | 技术选型 | 理由 |
|------|---------|------|
| **语言** | Python 3.11+ | 生态丰富，AI 集成便利 |
| **AI 引擎** | Claude Code (Opus 4.5) | 强大的代码理解与生成能力 |
| **解析器** | Tree-sitter / JavaParser | 高性能 AST 解析 |
| **模板引擎** | Jinja2 | 灵活的代码模板 |
| **数据存储** | SQLite + YAML | 轻量级，版本控制友好 |
| **任务调度** | Celery + Redis | 分布式批处理 |
| **CI/CD** | GitHub Actions | 自动化流水线 |

### 6.2 AI 使用策略

```python
# AI 使用优化策略
class AIUsageStrategy:
    """
    分层 AI 使用策略，优化成本与效率
    """

    # Level 1: 不使用 AI - 直接规则匹配
    RULE_BASED = {
        "criteria": "1:1 mapping with high confidence",
        "ai_cost": 0,
        "speed": "fast"
    }

    # Level 2: 轻量 AI - 使用小模型验证
    LIGHT_AI = {
        "criteria": "Simple transformation needed",
        "model": "claude-3-haiku",
        "ai_cost": "low",
        "speed": "medium"
    }

    # Level 3: 标准 AI - 使用中等模型生成
    STANDARD_AI = {
        "criteria": "Complex transformation needed",
        "model": "claude-sonnet-4",
        "ai_cost": "medium",
        "speed": "medium"
    }

    # Level 4: 高级 AI - 使用最强模型
    ADVANCED_AI = {
        "criteria": "Novel pattern, bridge code needed",
        "model": "claude-opus-4-5",
        "ai_cost": "high",
        "speed": "slow"
    }
```

---

## 七、实施路线图

### Phase 1: 基础设施 (Foundation)
- [ ] 搭建项目基础结构
- [ ] 实现 Android SDK 解析器
- [ ] 实现 HarmonyOS SDK 解析器
- [ ] 建立 API 规格数据库

### Phase 2: 核心引擎 (Core Engine)
- [ ] 实现语义映射引擎
- [ ] 集成 Claude Code Agent
- [ ] 实现基础代码生成器
- [ ] 建立测试框架

### Phase 3: 自动化流水线 (Pipeline)
- [ ] 实现批量处理器
- [ ] 建立 CI/CD 流水线
- [ ] 实现增量更新机制
- [ ] 建立监控与告警

### Phase 4: 规模化 (Scale)
- [ ] 覆盖核心 Android API (前 5000 个)
- [ ] 性能优化
- [ ] 真机测试验证
- [ ] 文档与工具完善

### Phase 5: 生产就绪 (Production Ready)
- [ ] 完整 API 覆盖
- [ ] 与主流 Android 应用兼容性测试
- [ ] 发布 v1.0 正式版

---

## 八、风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| AI 生成代码质量不稳定 | 高 | 多轮审核 + 自动化测试 + 人工抽检 |
| API 语义理解偏差 | 中 | 建立反馈循环，持续优化映射规则 |
| HarmonyOS API 变更频繁 | 中 | 增量更新机制 + 变更监控 |
| 性能损耗过大 | 中 | 关键路径优化 + Native 桥接 |
| 法律合规风险 | 高 | 仅使用公开 API，遵守开源协议 |

---

## 九、成功指标

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| API 覆盖率 | > 90% | 已适配 API / 总 API 数量 |
| 自动化率 | > 90% | 无需人工介入的 API 占比 |
| 测试通过率 | > 95% | 自动化测试通过数 / 总测试数 |
| 性能损耗 | < 10% | 适配后性能 / 原生性能 |
| 兼容性 | Top 1000 App | 主流应用运行成功率 |

---

*文档版本: 1.0.0*
*最后更新: 2026-01-18*
*作者: NOAH Team (AI-assisted)*
