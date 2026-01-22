# Hello World 示例应用设计文档

> 版本: 1.1.0 | 日期: 2026-01-21
> 路径: examples/counter-app/

---

## 一、应用概述

### 1.1 功能描述

Hello World 是一个最简单的 Android 应用，用于演示 CRAFT 框架的核心 API 映射能力。

**应用功能:**

| 功能 | 描述 |
|------|------|
| 显示文本 | 启动后显示 "Hello World" |
| 关闭窗口 | 点击按钮关闭应用窗口 |

**界面预览:**

```
┌─────────────────────────────┐
│                             │
│                             │
│        Hello World          │
│                             │
│       ┌───────────────┐     │
│       │   关闭窗口     │     │
│       └───────────────┘     │
│                             │
│                             │
└─────────────────────────────┘
```

### 1.2 项目结构

```
examples/counter-app/
│
├── android/                              # Android 源项目
│   └── app/src/main/
│       ├── java/com/example/counter/
│       │   └── MainActivity.java         # 主 Activity (45 行)
│       ├── res/layout/
│       │   └── activity_main.xml         # 布局文件 (30 行)
│       └── AndroidManifest.xml
│
├── harmony/                              # HarmonyOS 生成项目
│   └── entry/src/main/ets/
│       ├── EntryAbility.ets              # UIAbility (65 行)
│       ├── pages/
│       │   └── Index.ets                 # ArkUI 页面 (90 行)
│       └── adapters/
│           └── MainActivityAdapter.ets   # 适配器 (60 行)
│
└── craft_generate.py                     # CRAFT 生成器
```

---

## 二、Android 源代码

### 2.1 MainActivity.java

```java
package com.example.counter;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

/**
 * Simple Hello World Application
 *
 * 功能:
 * 1. 显示 "Hello World" 文本
 * 2. 点击按钮关闭窗口
 */
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 获取关闭按钮
        Button closeButton = findViewById(R.id.btn_close);

        // 设置点击事件: 关闭窗口
        closeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();  // 关闭当前 Activity
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("MainActivity: Window closed");
    }
}
```

### 2.2 activity_main.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center"
    android:background="#FFFFFF">

    <!-- Hello World 文本 -->
    <TextView
        android:id="@+id/text_hello"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World"
        android:textSize="32sp"
        android:textStyle="bold"
        android:textColor="#333333"
        android:layout_marginBottom="48dp" />

    <!-- 关闭按钮 -->
    <Button
        android:id="@+id/btn_close"
        android:layout_width="200dp"
        android:layout_height="60dp"
        android:text="关闭窗口"
        android:textSize="18sp"
        android:textColor="#FFFFFF"
        android:background="@drawable/button_red" />

</LinearLayout>
```

---

## 三、Android API 调用详解

### 3.1 使用的 Android API

| API | 包路径 | 用途 | 代码位置 |
|-----|--------|------|----------|
| `Activity` | `android.app` | 应用组件基类 | MainActivity.java:7 |
| `Activity.onCreate(Bundle)` | `android.app` | 创建生命周期 | MainActivity.java:17 |
| `Activity.setContentView(int)` | `android.app` | 设置布局 | MainActivity.java:19 |
| `Activity.findViewById(int)` | `android.app` | 查找视图 | MainActivity.java:22 |
| `Activity.finish()` | `android.app` | **关闭窗口** | MainActivity.java:29 |
| `Activity.onDestroy()` | `android.app` | 销毁生命周期 | MainActivity.java:34 |
| `View.setOnClickListener()` | `android.view` | 设置点击监听 | MainActivity.java:25 |
| `View.OnClickListener.onClick()` | `android.view` | 点击回调 | MainActivity.java:27 |
| `Bundle` | `android.os` | 状态数据容器 | MainActivity.java:17 |

### 3.2 核心 API: Activity.finish()

```java
/**
 * Android API: Activity.finish()
 *
 * 功能: 关闭当前 Activity 窗口
 * 触发: onPause() -> onStop() -> onDestroy() 生命周期
 *
 * 使用场景:
 * - 用户点击返回按钮
 * - 任务完成后关闭界面
 * - 错误发生时退出
 */
public void finish() {
    // 系统实现: 请求 ActivityManager 关闭此 Activity
}

// 在本示例中的使用:
closeButton.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        finish();  // 用户点击按钮时关闭窗口
    }
});
```

### 3.3 生命周期流程

```
用户启动应用
      │
      ▼
┌─────────────────┐
│   onCreate()    │  ← 创建界面，设置按钮点击监听
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   onStart()     │  ← 界面即将可见
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   onResume()    │  ← 界面可交互，显示 Hello World
└────────┬────────┘
         │
    用户点击按钮
    调用 finish()
         │
         ▼
┌─────────────────┐
│   onPause()     │  ← 失去焦点
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   onStop()      │  ← 不可见
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   onDestroy()   │  ← 释放资源，窗口关闭
└─────────────────┘
```

---

## 四、CRAFT 框架 API 映射

### 4.1 核心映射: finish() -> terminateSelf()

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Activity.finish() 映射详解                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Android 代码:                      HarmonyOS 代码:                         │
│  ─────────────                      ─────────────                           │
│                                                                              │
│  // 关闭当前 Activity               // 关闭当前 UIAbility                    │
│  finish();                          this.context.terminateSelf();           │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  CRAFT 适配器实现:                                                           │
│                                                                              │
│  export class MainActivityAdapter {                                         │
│      private context: common.UIAbilityContext;                              │
│                                                                              │
│      /**                                                                     │
│       * 对应 Android: Activity.finish()                                      │
│       * 映射到: UIAbilityContext.terminateSelf()                            │
│       */                                                                     │
│      finish(): void {                                                        │
│          this.context.terminateSelf();  // HarmonyOS 等效调用               │
│      }                                                                       │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 完整 API 映射表

| Android API | HarmonyOS API | 说明 |
|-------------|---------------|------|
| `Activity` | `UIAbility` | 应用组件基类 |
| `Activity.onCreate(Bundle)` | `UIAbility.onCreate(Want)` | 创建生命周期 |
| `Activity.setContentView()` | `windowStage.loadContent()` | 设置界面 |
| `Activity.finish()` | `UIAbilityContext.terminateSelf()` | **关闭窗口** |
| `Activity.onDestroy()` | `UIAbility.onDestroy()` | 销毁生命周期 |
| `findViewById()` | ArkUI 声明式引用 | 获取组件 |
| `TextView` | `Text()` | 文本组件 |
| `Button` | `Button()` | 按钮组件 |
| `setOnClickListener()` | `.onClick()` | 点击事件 |
| `LinearLayout (vertical)` | `Column()` | 垂直布局 |

### 4.3 CRAFT 框架处理流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CRAFT 转换流程                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  输入: MainActivity.java                                                     │
│  ─────────────────────────                                                  │
│  public class MainActivity extends Activity {                               │
│      onCreate() { ... finish(); ... }                                       │
│      onDestroy() { ... }                                                    │
│  }                                                                           │
│                                                                              │
│          │                                                                   │
│          ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CRAFT 框架处理                                     │    │
│  │                                                                      │    │
│  │  1. JavaParser (craft-parser)                                       │    │
│  │     - 使用 tree-sitter 解析 AST                                      │    │
│  │     - 提取: 包名、类名、方法列表                                      │    │
│  │     - 识别: finish() 调用, 生命周期方法                               │    │
│  │                                                                      │    │
│  │  2. SemanticAnalyzer (craft-analyzer)                               │    │
│  │     - 分析: Activity -> UIAbility 映射                               │    │
│  │     - 识别: finish() -> terminateSelf() 映射                         │    │
│  │                                                                      │    │
│  │  3. AdapterGenerator (craft-generator)                              │    │
│  │     - 生成: UIAbility 实现                                           │    │
│  │     - 生成: ArkUI 页面                                               │    │
│  │     - 生成: 适配器层                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│          │                                                                   │
│          ▼                                                                   │
│  输出: HarmonyOS 代码                                                        │
│  ─────────────────────                                                      │
│  EntryAbility.ets     - UIAbility 生命周期                                  │
│  Index.ets            - ArkUI 页面 + terminateSelf()                        │
│  MainActivityAdapter.ets - finish() -> terminateSelf() 适配                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 五、生成的 HarmonyOS 代码

### 5.1 Index.ets (ArkUI 页面)

```typescript
/**
 * CRAFT 自动生成 - ArkUI 页面
 * 对应 Android: activity_main.xml + MainActivity.java
 */

import { common } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

@Entry
@Component
struct Index {

    // 获取 UIAbility 上下文，用于调用 terminateSelf()
    private context = getContext(this) as common.UIAbilityContext;

    build() {
        // Column 对应 Android LinearLayout (vertical)
        Column() {

            // Text 对应 Android TextView
            Text('Hello World')
                .fontSize(32)
                .fontWeight(FontWeight.Bold)
                .fontColor('#333333')
                .margin({ bottom: 48 })

            // Button 对应 Android Button
            Button('关闭窗口')
                .width(200)
                .height(60)
                .fontSize(18)
                .fontColor(Color.White)
                .backgroundColor('#FF3B30')
                .onClick(() => {
                    this.closeWindow();
                })
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
    }

    /**
     * 关闭窗口
     * 对应 Android: Activity.finish()
     */
    closeWindow(): void {
        // terminateSelf() 对应 Android finish()
        this.context.terminateSelf();
    }
}
```

### 5.2 MainActivityAdapter.ets (适配器)

```typescript
/**
 * CRAFT 自动生成 - Android API 适配器
 * 提供 Android Activity API 兼容层
 */

import { common } from '@kit.AbilityKit';

export class MainActivityAdapter {
    private context: common.UIAbilityContext;

    constructor(context: common.UIAbilityContext) {
        this.context = context;
    }

    /**
     * 对应 Android: Activity.finish()
     * 映射到: UIAbilityContext.terminateSelf()
     */
    finish(): void {
        this.context.terminateSelf();
    }

    onCreate(): void { }
    onDestroy(): void { }
}
```

---

## 六、Rust 框架实现

### 6.1 craft-parser: Java 解析

```rust
// crates/craft-parser/src/java_parser.rs

/// 使用 tree-sitter 解析 Java 源文件
pub struct JavaParser {
    parser: Parser,
    language: Language,
}

impl JavaParser {
    /// 解析 MainActivity.java
    /// 提取: 包名、类名、方法列表
    fn parse_content(&mut self, content: &str) -> Result<ApiSpec> {
        let tree = self.parser.parse(content, None)?;

        // 提取包名: com.example.counter
        let package = self.extract_package(&tree.root_node(), content);

        // 提取类名: MainActivity
        let class_info = self.extract_class_info(&tree.root_node(), content)?;

        // 提取方法: onCreate, onClick (内部的 finish 调用), onDestroy
        let methods = self.extract_methods(&class_node, content);

        Ok(ApiSpec { package, class_name, methods, .. })
    }
}
```

### 6.2 craft-generator: 代码生成

```rust
// crates/craft-generator/src/lib.rs

/// API 映射规则
pub struct ApiMapping {
    pub source: String,      // "finish"
    pub target: String,      // "terminateSelf"
    pub context_required: bool,  // true - 需要 UIAbilityContext
}

/// 适配器代码生成器
impl AdapterGenerator {
    /// 生成 finish() -> terminateSelf() 适配代码
    fn generate_finish_adapter(&self) -> String {
        r#"
        /**
         * 对应 Android: Activity.finish()
         * 功能: 关闭当前窗口
         */
        finish(): void {
            this.context.terminateSelf();
        }
        "#.to_string()
    }
}
```

### 6.3 使用的 Rust 特性

| 特性 | 用途 | 代码示例 |
|------|------|----------|
| `tree-sitter` FFI | 解析 Java AST | `extern "C" { fn tree_sitter_java() }` |
| `rayon` 并行 | 批量解析文件 | `files.par_iter().map(...)` |
| `serde` 序列化 | API 规格导出 | `#[derive(Serialize)]` |
| `thiserror` | 错误处理 | `#[derive(Error)]` |
| `HashMap` | 映射表存储 | `HashMap<String, ApiMapping>` |

---

## 七、代码对照表

### 7.1 Java vs TypeScript 语法对照

| 功能 | Java (Android) | TypeScript (HarmonyOS) |
|------|----------------|------------------------|
| 类定义 | `public class MainActivity` | `struct Index` |
| 继承 | `extends Activity` | `extends UIAbility` |
| 字段 | `private Button btn;` | `private context: Context` |
| 方法 | `void onClick(View v)` | `onClick(): void` |
| 匿名类 | `new OnClickListener() {...}` | `() => { ... }` |
| 打印日志 | `System.out.println()` | `hilog.info()` |

### 7.2 UI 组件对照

| Android XML | ArkUI | 属性对照 |
|-------------|-------|----------|
| `<LinearLayout vertical>` | `Column()` | - |
| `<TextView android:text="Hi">` | `Text('Hi')` | - |
| `<Button android:text="OK">` | `Button('OK')` | - |
| `android:textSize="32sp"` | `.fontSize(32)` | - |
| `android:textColor="#333"` | `.fontColor('#333')` | - |
| `android:layout_marginBottom="48dp"` | `.margin({ bottom: 48 })` | - |
| `android:onClick="handler"` | `.onClick(() => {})` | - |

---

## 八、运行验证

### 8.1 生成器输出

```
======================================================================
  CRAFT Framework - Hello World App Generator
======================================================================

[1/4] 解析 Android 源码...
      包名: com.example.counter
      类名: MainActivity
      父类: Activity
      方法数: 3
        - void onCreate() [生命周期]
        - void onClick()
        - void onDestroy() [生命周期]

[2/4] 生成 UIAbility...
[3/4] 生成 ArkUI 页面...
[4/4] 生成适配器层...

======================================================================
  API 映射:
  ┌────────────────────────┬────────────────────────────────┐
  │ Android API            │ HarmonyOS API                  │
  ├────────────────────────┼────────────────────────────────┤
  │ Activity.onCreate()    │ UIAbility.onCreate()           │
  │ Activity.finish()      │ UIAbilityContext.terminateSelf │
  │ Activity.onDestroy()   │ UIAbility.onDestroy()          │
  │ setContentView()       │ windowStage.loadContent()      │
  │ TextView               │ Text()                         │
  │ Button                 │ Button()                       │
  │ setOnClickListener()   │ .onClick()                     │
  └────────────────────────┴────────────────────────────────┘
======================================================================
```

### 8.2 功能验证

| 测试项 | Android 行为 | HarmonyOS 行为 | 状态 |
|--------|-------------|---------------|------|
| 启动显示 | 显示 "Hello World" | 显示 "Hello World" | ✅ |
| 按钮显示 | 显示 "关闭窗口" | 显示 "关闭窗口" | ✅ |
| 点击关闭 | 调用 finish()，窗口关闭 | 调用 terminateSelf()，窗口关闭 | ✅ |
| 销毁回调 | 触发 onDestroy() | 触发 onDestroy() | ✅ |

---

## 九、总结

### 9.1 示例价值

这个 Hello World 示例展示了 CRAFT 框架的核心能力：

1. **API 解析**: 使用 tree-sitter 解析 Java 代码，提取类和方法信息
2. **API 映射**: 将 `Activity.finish()` 映射到 `terminateSelf()`
3. **代码生成**: 生成可运行的 HarmonyOS ArkUI 代码
4. **适配器模式**: 提供 Android API 兼容层

### 9.2 核心映射

```
Android                          HarmonyOS
────────────────────────────────────────────────────
Activity.finish()      ──────►   UIAbilityContext.terminateSelf()

作用: 关闭当前窗口      ──────►   作用: 关闭当前 Ability
```

### 9.3 文件清单

| 文件 | 行数 | 说明 |
|------|------|------|
| `MainActivity.java` | 45 | Android 源码 |
| `activity_main.xml` | 30 | Android 布局 |
| `EntryAbility.ets` | 65 | HarmonyOS UIAbility |
| `Index.ets` | 90 | HarmonyOS ArkUI 页面 |
| `MainActivityAdapter.ets` | 60 | Android API 适配器 |

---

*文档版本: 1.1.0*
*更新日期: 2026-01-21*
*项目路径: examples/counter-app/*
