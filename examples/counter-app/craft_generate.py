#!/usr/bin/env python3
"""
CRAFT Framework - Hello World App Adapter Generator

这个脚本解析 Android Hello World 应用并生成:
1. 适配器层 (Android API 兼容层)
2. OpenHarmony UIAbility 实现
3. ArkUI 页面组件

注意: 使用 OpenHarmony API 风格 (@ohos.xxx)
      兼容 OpenHarmony 3.2+ 和 HarmonyOS
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from pathlib import Path

# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class MethodInfo:
    name: str
    return_type: str
    parameters: List[Tuple[str, str]]  # [(type, name), ...]
    is_lifecycle: bool = False

@dataclass
class ClassInfo:
    package: str
    name: str
    parent: Optional[str]
    methods: List[MethodInfo] = field(default_factory=list)

# ============================================================================
# Java 解析器
# ============================================================================

class JavaParser:
    """解析 Java 源文件"""

    def __init__(self):
        self.lifecycle_methods = {'onCreate', 'onDestroy', 'onStart', 'onStop', 'onResume', 'onPause'}

    def parse_file(self, filepath: str) -> ClassInfo:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取包名
        package_match = re.search(r'package\s+([\w.]+);', content)
        package = package_match.group(1) if package_match else ""

        # 提取类信息
        class_match = re.search(r'public\s+class\s+(\w+)(?:\s+extends\s+(\w+))?', content)
        class_name = class_match.group(1) if class_match else "Unknown"
        parent_class = class_match.group(2) if class_match and class_match.group(2) else None

        # 提取方法
        methods = self._extract_methods(content)

        return ClassInfo(package=package, name=class_name, parent=parent_class, methods=methods)

    def _extract_methods(self, content: str) -> List[MethodInfo]:
        methods = []
        method_pattern = r'(?:@\w+\s+)*(?:public|protected|private)\s+(\w+)\s+(\w+)\s*\(([^)]*)\)'

        for match in re.finditer(method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3).strip()

            parameters = []
            if params_str:
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        parts = param.rsplit(' ', 1)
                        if len(parts) == 2:
                            parameters.append((parts[0], parts[1]))

            methods.append(MethodInfo(
                name=method_name,
                return_type=return_type,
                parameters=parameters,
                is_lifecycle=method_name in self.lifecycle_methods
            ))

        return methods

# ============================================================================
# API 映射
# ============================================================================

# Activity.finish() -> terminateSelf() 映射
API_MAPPING = {
    'finish': {
        'target': 'terminateSelf',
        'description': 'Close the current ability window',
        'harmony_api': 'UIAbilityContext.terminateSelf()'
    },
    'onCreate': {
        'target': 'onCreate',
        'description': 'Ability creation lifecycle',
        'harmony_api': 'UIAbility.onCreate(Want, LaunchParam)'
    },
    'onDestroy': {
        'target': 'onDestroy',
        'description': 'Ability destruction lifecycle',
        'harmony_api': 'UIAbility.onDestroy()'
    }
}

# ============================================================================
# 代码生成器
# ============================================================================

class HarmonyGenerator:
    """生成 OpenHarmony/HarmonyOS 代码"""

    def generate_ability(self, class_info: ClassInfo) -> str:
        """生成 UIAbility (OpenHarmony API 风格)"""
        return f'''/**
 * CRAFT 自动生成 - UIAbility
 * 源自: {class_info.package}.{class_info.name}
 *
 * API 风格: OpenHarmony (@ohos.xxx)
 * 兼容: OpenHarmony 3.2+ / HarmonyOS 3.0+
 *
 * API 映射:
 * - Activity.onCreate() -> UIAbility.onCreate()
 * - Activity.finish() -> UIAbilityContext.terminateSelf()
 * - Activity.onDestroy() -> UIAbility.onDestroy()
 */

import UIAbility from '@ohos.app.ability.UIAbility';
import AbilityConstant from '@ohos.app.ability.AbilityConstant';
import Want from '@ohos.app.ability.Want';
import window from '@ohos.window';
import hilog from '@ohos.hilog';

const TAG: string = 'EntryAbility';
const DOMAIN: number = 0x0000;

export default class EntryAbility extends UIAbility {{

    /**
     * 对应 Android: Activity.onCreate(Bundle)
     * 功能: 初始化 Ability
     */
    onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {{
        hilog.info(DOMAIN, TAG, 'onCreate - 窗口创建');
    }}

    /**
     * OpenHarmony 特有: 窗口舞台创建
     * 对应 Android: Activity.setContentView()
     */
    onWindowStageCreate(windowStage: window.WindowStage): void {{
        hilog.info(DOMAIN, TAG, 'onWindowStageCreate - 加载页面');

        // 加载主页面 (对应 setContentView)
        windowStage.loadContent('pages/Index', (err, data) => {{
            if (err.code) {{
                hilog.error(DOMAIN, TAG, '页面加载失败: %{{public}}s', JSON.stringify(err));
                return;
            }}
            hilog.info(DOMAIN, TAG, '页面加载成功');
        }});
    }}

    /**
     * 对应 Android: Activity.onDestroy()
     * 功能: 释放资源
     */
    onDestroy(): void {{
        hilog.info(DOMAIN, TAG, 'onDestroy - 窗口关闭');
    }}

    onWindowStageDestroy(): void {{
        hilog.info(DOMAIN, TAG, 'onWindowStageDestroy');
    }}

    onForeground(): void {{
        hilog.info(DOMAIN, TAG, 'onForeground - 进入前台');
    }}

    onBackground(): void {{
        hilog.info(DOMAIN, TAG, 'onBackground - 进入后台');
    }}
}}
'''

    def generate_page(self, class_info: ClassInfo) -> str:
        """生成 ArkUI 页面 (OpenHarmony API 风格)"""
        return '''/**
 * CRAFT 自动生成 - ArkUI 页面
 * 对应 Android: activity_main.xml + MainActivity.java
 *
 * API 风格: OpenHarmony (@ohos.xxx)
 * 兼容: OpenHarmony 3.2+ / HarmonyOS 3.0+
 *
 * 功能:
 * 1. 显示 "Hello World" 文本
 * 2. 点击按钮关闭窗口
 *
 * API 映射:
 * - TextView -> Text 组件
 * - Button -> Button 组件
 * - Button.setOnClickListener() -> Button.onClick()
 * - Activity.finish() -> terminateSelf()
 */

import common from '@ohos.app.ability.common';
import hilog from '@ohos.hilog';

const TAG: string = 'IndexPage';
const DOMAIN: number = 0x0000;

@Entry
@Component
struct Index {

    /**
     * 获取 UIAbility 上下文
     * 用于调用 terminateSelf() 关闭窗口
     */
    private context: common.UIAbilityContext = getContext(this) as common.UIAbilityContext;

    /**
     * 构建 UI
     * 对应 Android: activity_main.xml
     */
    build() {
        // Column 对应 Android LinearLayout (vertical)
        Column() {

            // Text 对应 Android TextView
            // android:text="Hello World"
            Text('Hello World')
                .fontSize(32)
                .fontWeight(FontWeight.Bold)
                .fontColor('#333333')
                .margin({ bottom: 48 })

            // Button 对应 Android Button
            // android:id="@+id/btn_close"
            Button('关闭窗口')
                .width(200)
                .height(60)
                .fontSize(18)
                .fontColor(Color.White)
                .backgroundColor('#FF3B30')
                .borderRadius(8)
                .onClick(() => {
                    this.closeWindow();
                })

        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#FFFFFF')
    }

    /**
     * 关闭窗口
     * 对应 Android: Activity.finish()
     *
     * Android 代码:
     *   finish();
     *
     * OpenHarmony 代码:
     *   this.context.terminateSelf();
     */
    closeWindow(): void {
        hilog.info(DOMAIN, TAG, '关闭窗口 - 对应 Activity.finish()');

        // terminateSelf() 对应 Android finish()
        this.context.terminateSelf((err) => {
            if (err.code) {
                hilog.error(DOMAIN, TAG, '关闭失败: %{public}s', JSON.stringify(err));
                return;
            }
            hilog.info(DOMAIN, TAG, '窗口已关闭');
        });
    }
}
'''

    def generate_adapter(self, class_info: ClassInfo) -> str:
        """生成适配器层 (OpenHarmony API 风格)"""
        return f'''/**
 * CRAFT 自动生成 - Android API 适配器
 * 源自: {class_info.package}.{class_info.name}
 *
 * API 风格: OpenHarmony (@ohos.xxx)
 * 兼容: OpenHarmony 3.2+ / HarmonyOS 3.0+
 *
 * 提供 Android Activity API 兼容层
 */

import UIAbility from '@ohos.app.ability.UIAbility';
import common from '@ohos.app.ability.common';
import hilog from '@ohos.hilog';

const TAG: string = '{class_info.name}Adapter';
const DOMAIN: number = 0x0000;

/**
 * Android Activity API 适配器
 *
 * 将 Android API 调用委托给 OpenHarmony API:
 * - finish() -> terminateSelf()
 * - onCreate() -> onCreate()
 * - onDestroy() -> onDestroy()
 */
export class {class_info.name}Adapter {{
    private context: common.UIAbilityContext;

    constructor(context: common.UIAbilityContext) {{
        this.context = context;
    }}

    /**
     * 对应 Android: Activity.finish()
     * 功能: 关闭当前 Activity/Ability 窗口
     *
     * Android 实现:
     *   public void finish() {{
     *       // 关闭 Activity，触发 onDestroy
     *   }}
     *
     * OpenHarmony 实现:
     *   terminateSelf() - 关闭当前 UIAbility
     */
    finish(): void {{
        hilog.info(DOMAIN, TAG, 'finish() called -> terminateSelf()');
        this.context.terminateSelf();
    }}

    /**
     * 对应 Android: Activity.onCreate(Bundle)
     */
    onCreate(): void {{
        hilog.info(DOMAIN, TAG, 'onCreate() called');
    }}

    /**
     * 对应 Android: Activity.onDestroy()
     */
    onDestroy(): void {{
        hilog.info(DOMAIN, TAG, 'onDestroy() called');
    }}
}}
'''


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 70)
    print("  CRAFT Framework - Hello World App Generator")
    print("  Android -> OpenHarmony 适配")
    print("  API 风格: @ohos.xxx (OpenHarmony 3.2+ / HarmonyOS 3.0+)")
    print("=" * 70)
    print()

    script_dir = Path(__file__).parent
    android_src = script_dir / "android/app/src/main/java/com/example/counter/MainActivity.java"
    harmony_dir = script_dir / "harmony/entry/src/main/ets"

    # 解析 Android 源码
    print("[1/4] 解析 Android 源码...")
    parser = JavaParser()
    class_info = parser.parse_file(str(android_src))

    print(f"      包名: {class_info.package}")
    print(f"      类名: {class_info.name}")
    print(f"      父类: {class_info.parent}")
    print(f"      方法数: {len(class_info.methods)}")
    for m in class_info.methods:
        tag = " [生命周期]" if m.is_lifecycle else ""
        print(f"        - {m.return_type} {m.name}(){tag}")
    print()

    # 生成代码
    generator = HarmonyGenerator()

    # 生成 UIAbility
    print("[2/4] 生成 UIAbility...")
    ability_code = generator.generate_ability(class_info)
    ability_file = harmony_dir / "EntryAbility.ets"
    ability_file.parent.mkdir(parents=True, exist_ok=True)
    with open(ability_file, 'w', encoding='utf-8') as f:
        f.write(ability_code)
    print(f"      生成: {ability_file.relative_to(script_dir)}")

    # 生成 ArkUI 页面
    print("[3/4] 生成 ArkUI 页面...")
    page_code = generator.generate_page(class_info)
    pages_dir = harmony_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    page_file = pages_dir / "Index.ets"
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write(page_code)
    print(f"      生成: {page_file.relative_to(script_dir)}")

    # 生成适配器
    print("[4/4] 生成适配器层...")
    adapter_code = generator.generate_adapter(class_info)
    adapter_dir = harmony_dir / "adapters"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    adapter_file = adapter_dir / f"{class_info.name}Adapter.ets"
    with open(adapter_file, 'w', encoding='utf-8') as f:
        f.write(adapter_code)
    print(f"      生成: {adapter_file.relative_to(script_dir)}")

    # 总结
    print()
    print("=" * 70)
    print("  生成完成!")
    print("=" * 70)
    print()
    print("  API 映射:")
    print("  ┌────────────────────────┬────────────────────────────────┐")
    print("  │ Android API            │ HarmonyOS API                  │")
    print("  ├────────────────────────┼────────────────────────────────┤")
    print("  │ Activity.onCreate()    │ UIAbility.onCreate()           │")
    print("  │ Activity.finish()      │ UIAbilityContext.terminateSelf │")
    print("  │ Activity.onDestroy()   │ UIAbility.onDestroy()          │")
    print("  │ setContentView()       │ windowStage.loadContent()      │")
    print("  │ TextView               │ Text()                         │")
    print("  │ Button                 │ Button()                       │")
    print("  │ setOnClickListener()   │ .onClick()                     │")
    print("  └────────────────────────┴────────────────────────────────┘")
    print()
    print("  生成的文件:")
    print(f"    1. {ability_file.relative_to(script_dir)}")
    print(f"    2. {page_file.relative_to(script_dir)}")
    print(f"    3. {adapter_file.relative_to(script_dir)}")
    print()

if __name__ == '__main__':
    main()
