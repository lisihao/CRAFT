# CRAFT 框架运行指南

> 版本: 1.0.0 | 日期: 2025-01-22

## 概述

本文档介绍如何运行 CRAFT 框架，包括：
1. 运行代码生成器（Android → OpenHarmony）
2. 验证生成的代码
3. 在 OpenHarmony 设备上运行应用

---

## 第一部分：运行代码生成器

### 1.1 环境要求

| 依赖项 | 版本要求 | 说明 |
|-------|---------|------|
| Python | 3.8+ | 代码生成器运行环境 |
| 无其他依赖 | - | 使用 Python 标准库 |

### 1.2 运行生成器

```bash
# 1. 进入示例目录
cd examples/counter-app

# 2. 运行生成器（解析 Android 代码 → 生成 OpenHarmony 代码）
python3 craft_generate.py
```

### 1.3 生成器输出

运行成功后，将生成以下文件：

```
harmony/entry/src/main/ets/
├── EntryAbility.ets              # UIAbility 入口
├── pages/
│   └── Index.ets                 # ArkUI 页面组件
└── adapters/
    └── MainActivityAdapter.ets   # Android API 适配器
```

### 1.4 生成器功能说明

| 功能 | 输入 | 输出 |
|-----|------|------|
| Java 解析 | `android/app/src/main/java/**/*.java` | ClassInfo 数据结构 |
| API 映射 | Android API 调用 | OpenHarmony API 调用 |
| 代码生成 | ClassInfo + 映射规则 | `.ets` 文件 |

**核心 API 映射：**

| Android API | OpenHarmony API |
|------------|-----------------|
| `Activity.onCreate()` | `UIAbility.onCreate()` |
| `Activity.onDestroy()` | `UIAbility.onDestroy()` |
| `Activity.finish()` | `UIAbilityContext.terminateSelf()` |
| `setContentView()` | `windowStage.loadContent()` |

---

## 第二部分：验证生成的代码

### 2.1 运行测试套件

```bash
cd examples/counter-app

# 运行所有测试（57 个测试用例）
python3 tests/run_all_tests.py
```

### 2.2 测试覆盖范围

| 测试类别 | 用例数 | 验证内容 |
|---------|-------|---------|
| Java 解析器 | 5 | 包名、类名、方法解析 |
| API 映射 | 5 | 映射规则正确性 |
| 代码生成 | 10 | UIAbility、页面、适配器生成 |
| OpenHarmony API 风格 | 3 | @ohos.xxx 导入格式 |
| 生命周期映射 | 3 | Activity → UIAbility |
| 代码结构 | 3 | 生成代码完整性 |
| 类型注解 | 3 | TypeScript 类型 |
| 文件存在性 | 3 | .ets 文件生成 |
| ArkTS 语法 | 5 | 语法正确性 |
| 括号平衡 | 3 | 代码结构完整 |
| UIAbility 生命周期 | 3 | 生命周期方法完整 |
| ArkUI 组件 | 5 | UI 组件正确 |
| API 映射实现 | 2 | terminateSelf 等 |

**预期结果：**
```
总计:
  运行: 57
  成功: 57
  失败: 0
  错误: 0
  通过率: 100.0%
```

### 2.3 单独运行测试

```bash
# 只运行生成器测试
python3 tests/test_craft_generator.py

# 只运行语法验证测试
python3 tests/test_openharmony_syntax.py
```

---

## 第三部分：运行 OpenHarmony 应用

### 3.1 方案 A：DevEco Studio（推荐）

#### 3.1.1 安装 DevEco Studio

1. 访问 [华为开发者官网](https://developer.huawei.com/consumer/cn/deveco-studio/)
2. 下载 DevEco Studio 4.0+ 版本
3. 按照安装向导完成安装

**系统要求：**

| 项目 | 要求 |
|-----|------|
| 操作系统 | macOS 10.15+ / Windows 10 64-bit / Ubuntu 18.04+ |
| 内存 | 8GB+ (推荐 16GB) |
| 磁盘空间 | 10GB+ |
| DevEco 版本 | 4.0+ (支持 OpenHarmony 4.0+) |

#### 3.1.2 打开项目

1. 启动 DevEco Studio
2. 选择 `File` → `Open`
3. 导航到 `examples/counter-app/harmony` 目录
4. 点击 `OK` 打开项目
5. 等待项目同步完成（首次可能需要下载 SDK）

#### 3.1.3 配置签名（调试模式）

1. 打开 `File` → `Project Structure`
2. 选择 `Signing Configs`
3. 勾选 `Automatically generate signature`
4. 点击 `Apply` → `OK`

#### 3.1.4 运行应用

**使用模拟器：**
1. 点击 `Tools` → `Device Manager`
2. 创建或启动模拟器
3. 点击工具栏的 `Run` 按钮 (▶)

**使用真机：**
1. 在设备上启用开发者模式
2. 使用 USB 连接设备
3. 在设备上允许调试
4. 点击 `Run` 按钮

### 3.2 方案 B：命令行构建（OpenHarmony SDK）

#### 3.2.1 安装 OpenHarmony SDK

```bash
# 克隆 OpenHarmony 文档获取 SDK 信息
git clone https://gitee.com/openharmony/docs.git

# 或直接下载 SDK
# 访问: https://gitee.com/openharmony/docs/tree/master/zh-cn/release-notes
```

#### 3.2.2 使用 hvigor 构建

```bash
cd examples/counter-app/harmony

# 安装依赖
ohpm install

# 构建 HAP 包
hvigorw assembleHap --mode module -p product=default

# 输出位置
# entry/build/default/outputs/default/entry-default-signed.hap
```

#### 3.2.3 安装到设备

```bash
# 使用 hdc (HarmonyOS Device Connector) 安装
hdc install entry/build/default/outputs/default/entry-default-signed.hap

# 启动应用
hdc shell aa start -a EntryAbility -b com.example.counter
```

### 3.3 方案 C：云端模拟器

华为提供在线模拟器服务，无需本地安装：

1. 访问 [DevEco Studio Cloud](https://developer.huawei.com/consumer/cn/devicelab/)
2. 登录华为开发者账号
3. 上传项目或使用在线 IDE
4. 在云端模拟器中运行

---

## 第四部分：项目结构说明

### 4.1 完整项目结构

```
examples/counter-app/
├── android/                          # Android 源代码（输入）
│   └── app/src/main/
│       ├── java/com/example/counter/
│       │   └── MainActivity.java     # Android Activity
│       └── res/layout/
│           └── activity_main.xml     # Android 布局
│
├── harmony/                          # OpenHarmony 项目（输出）
│   ├── AppScope/
│   │   └── app.json5                 # 应用配置
│   ├── entry/
│   │   └── src/main/
│   │       ├── ets/                  # ArkTS 源代码
│   │       │   ├── EntryAbility.ets
│   │       │   ├── pages/Index.ets
│   │       │   └── adapters/MainActivityAdapter.ets
│   │       ├── resources/            # 资源文件
│   │       └── module.json5          # 模块配置
│   ├── build-profile.json5           # 构建配置
│   └── oh-package.json5              # 包配置
│
├── tests/                            # 测试套件
│   ├── test_craft_generator.py       # 生成器测试
│   ├── test_openharmony_syntax.py    # 语法测试
│   └── run_all_tests.py              # 测试运行器
│
├── craft_generate.py                 # CRAFT 代码生成器
└── README.md                         # 项目说明
```

### 4.2 配置文件说明

| 文件 | 作用 |
|-----|------|
| `app.json5` | 应用级配置（bundleName、版本等） |
| `module.json5` | 模块配置（abilities、页面路由等） |
| `build-profile.json5` | 构建配置（SDK 版本、签名等） |
| `oh-package.json5` | 包管理配置（依赖项） |
| `main_pages.json` | 页面路由配置 |

---

## 第五部分：补全资源文件

项目需要以下资源文件才能完整编译：

### 5.1 图标文件

在 `harmony/entry/src/main/resources/base/media/` 目录下需要：

| 文件 | 尺寸 | 用途 |
|-----|------|------|
| `icon.png` | 256x256 | 应用图标 |
| `startIcon.png` | 256x256 | 启动图标 |

### 5.2 颜色配置

创建 `harmony/entry/src/main/resources/base/element/color.json`：

```json
{
  "color": [
    {
      "name": "start_window_background",
      "value": "#FFFFFF"
    }
  ]
}
```

### 5.3 字符串配置

确认 `harmony/entry/src/main/resources/base/element/string.json` 包含：

```json
{
  "string": [
    {
      "name": "module_desc",
      "value": "Counter App Module"
    },
    {
      "name": "EntryAbility_desc",
      "value": "Counter App Entry"
    },
    {
      "name": "EntryAbility_label",
      "value": "Counter"
    }
  ]
}
```

---

## 第六部分：故障排除

### 6.1 常见问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 测试失败 | 文件未生成 | 先运行 `python3 craft_generate.py` |
| DevEco 无法打开项目 | SDK 版本不匹配 | 检查 `build-profile.json5` 中的 SDK 版本 |
| 构建失败：缺少资源 | 图标文件缺失 | 添加 `icon.png` 和 `startIcon.png` |
| 签名错误 | 未配置签名 | 在 DevEco 中启用自动签名 |

### 6.2 日志查看

```bash
# DevEco Studio 日志
# macOS: ~/Library/Logs/Huawei/DevEcoStudio/
# Windows: %USERPROFILE%\.DevEcoStudio\system\log\

# 设备日志
hdc shell hilog | grep Counter
```

### 6.3 清理重建

```bash
cd examples/counter-app/harmony

# 清理构建缓存
rm -rf .hvigor
rm -rf entry/build
rm -rf oh_modules

# 重新构建
hvigorw clean
hvigorw assembleHap
```

---

## 第七部分：验证层级总结

| 层级 | 状态 | 验证方式 |
|-----|------|---------|
| 1. 代码生成 | ✅ 可用 | `python3 craft_generate.py` |
| 2. 单元测试 | ✅ 通过 | `python3 tests/run_all_tests.py` (57/57) |
| 3. 语法验证 | ✅ 通过 | ArkTS 语法检查 |
| 4. 编译构建 | ⚠️ 需补全资源 | DevEco Studio 或 hvigor |
| 5. 模拟器运行 | ⚠️ 需 DevEco | DevEco Studio 模拟器 |
| 6. 真机运行 | ⚠️ 需设备 | OpenHarmony/HarmonyOS 设备 |

---

## 参考链接

- [OpenHarmony 官方文档](https://docs.openharmony.cn/)
- [DevEco Studio 下载](https://developer.huawei.com/consumer/cn/deveco-studio/)
- [ArkTS 语言指南](https://docs.openharmony.cn/pages/v4.0/zh-cn/application-dev/quick-start/arkts-get-started.md)
- [UIAbility 开发指南](https://docs.openharmony.cn/pages/v4.0/zh-cn/application-dev/application-models/uiability-overview.md)
- [OpenHarmony Gitee](https://gitee.com/openharmony)
