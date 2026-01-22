#!/usr/bin/env python3
"""
CRAFT Framework - OpenHarmony 代码语法验证

验证生成的 .ets 文件语法正确性:
1. ArkTS/TypeScript 语法检查
2. OpenHarmony API 导入验证
3. 代码结构完整性检查
"""

import os
import re
import sys
import unittest
from pathlib import Path

# 项目根目录
PROJECT_DIR = Path(__file__).parent.parent
HARMONY_DIR = PROJECT_DIR / "harmony/entry/src/main/ets"


class TestEtsFilesExist(unittest.TestCase):
    """测试 .ets 文件存在"""

    def test_entry_ability_exists(self):
        """测试 EntryAbility.ets 存在"""
        path = HARMONY_DIR / "EntryAbility.ets"
        self.assertTrue(path.exists(), f"文件不存在: {path}")

    def test_index_page_exists(self):
        """测试 Index.ets 存在"""
        path = HARMONY_DIR / "pages/Index.ets"
        self.assertTrue(path.exists(), f"文件不存在: {path}")

    def test_adapter_exists(self):
        """测试 MainActivityAdapter.ets 存在"""
        path = HARMONY_DIR / "adapters/MainActivityAdapter.ets"
        self.assertTrue(path.exists(), f"文件不存在: {path}")


class TestOpenHarmonyImports(unittest.TestCase):
    """测试 OpenHarmony 导入语法"""

    def setUp(self):
        self.ability_code = (HARMONY_DIR / "EntryAbility.ets").read_text()
        self.page_code = (HARMONY_DIR / "pages/Index.ets").read_text()
        self.adapter_code = (HARMONY_DIR / "adapters/MainActivityAdapter.ets").read_text()

    def test_ability_imports_valid(self):
        """测试 UIAbility 导入语法有效"""
        # 检查正确的 OpenHarmony 导入格式
        import_patterns = [
            r"import\s+UIAbility\s+from\s+'@ohos\.app\.ability\.UIAbility'",
            r"import\s+AbilityConstant\s+from\s+'@ohos\.app\.ability\.AbilityConstant'",
            r"import\s+Want\s+from\s+'@ohos\.app\.ability\.Want'",
            r"import\s+window\s+from\s+'@ohos\.window'",
            r"import\s+hilog\s+from\s+'@ohos\.hilog'",
        ]

        for pattern in import_patterns:
            self.assertRegex(self.ability_code, pattern, f"缺少匹配: {pattern}")

    def test_page_imports_valid(self):
        """测试页面导入语法有效"""
        import_patterns = [
            r"import\s+common\s+from\s+'@ohos\.app\.ability\.common'",
            r"import\s+hilog\s+from\s+'@ohos\.hilog'",
        ]

        for pattern in import_patterns:
            self.assertRegex(self.page_code, pattern, f"缺少匹配: {pattern}")

    def test_adapter_imports_valid(self):
        """测试适配器导入语法有效"""
        import_patterns = [
            r"import\s+UIAbility\s+from\s+'@ohos\.app\.ability\.UIAbility'",
            r"import\s+common\s+from\s+'@ohos\.app\.ability\.common'",
            r"import\s+hilog\s+from\s+'@ohos\.hilog'",
        ]

        for pattern in import_patterns:
            self.assertRegex(self.adapter_code, pattern, f"缺少匹配: {pattern}")

    def test_no_kit_imports(self):
        """测试没有 @kit.xxx 导入（HarmonyOS NEXT 风格）"""
        all_code = self.ability_code + self.page_code + self.adapter_code
        self.assertNotIn("@kit.", all_code, "发现 @kit.xxx 导入，应使用 @ohos.xxx")


class TestArkTSSyntax(unittest.TestCase):
    """测试 ArkTS 语法正确性"""

    def setUp(self):
        self.ability_code = (HARMONY_DIR / "EntryAbility.ets").read_text()
        self.page_code = (HARMONY_DIR / "pages/Index.ets").read_text()
        self.adapter_code = (HARMONY_DIR / "adapters/MainActivityAdapter.ets").read_text()

    def test_class_declaration_syntax(self):
        """测试类声明语法"""
        # UIAbility 类声明
        self.assertRegex(
            self.ability_code,
            r"export\s+default\s+class\s+EntryAbility\s+extends\s+UIAbility\s*\{",
            "UIAbility 类声明语法错误"
        )

        # 适配器类声明
        self.assertRegex(
            self.adapter_code,
            r"export\s+class\s+MainActivityAdapter\s*\{",
            "适配器类声明语法错误"
        )

    def test_component_decorator_syntax(self):
        """测试组件装饰器语法"""
        # @Entry 和 @Component 装饰器
        self.assertIn("@Entry", self.page_code)
        self.assertIn("@Component", self.page_code)

        # struct 声明
        self.assertRegex(
            self.page_code,
            r"struct\s+Index\s*\{",
            "组件 struct 声明语法错误"
        )

    def test_method_declaration_syntax(self):
        """测试方法声明语法"""
        # 方法声明格式: methodName(params): returnType { }
        method_patterns = [
            r"onCreate\s*\(\s*want:\s*Want",
            r"onDestroy\s*\(\s*\)\s*:\s*void",
            r"onForeground\s*\(\s*\)\s*:\s*void",
            r"onBackground\s*\(\s*\)\s*:\s*void",
            r"build\s*\(\s*\)\s*\{",
        ]

        code = self.ability_code + self.page_code

        for pattern in method_patterns:
            self.assertRegex(code, pattern, f"方法声明语法错误: {pattern}")

    def test_type_annotations_syntax(self):
        """测试类型注解语法"""
        # const 类型注解
        self.assertRegex(self.ability_code, r"const\s+TAG:\s*string\s*=")
        self.assertRegex(self.ability_code, r"const\s+DOMAIN:\s*number\s*=")

        # 私有成员类型注解
        self.assertRegex(
            self.page_code,
            r"private\s+context:\s*common\.UIAbilityContext",
            "context 类型注解语法错误"
        )

    def test_arrow_function_syntax(self):
        """测试箭头函数语法"""
        # 回调中的箭头函数
        self.assertRegex(
            self.ability_code,
            r"\(\s*err\s*,?\s*data?\s*\)\s*=>\s*\{",
            "箭头函数语法错误"
        )

        # onClick 中的箭头函数
        self.assertRegex(
            self.page_code,
            r"\.onClick\s*\(\s*\(\s*\)\s*=>\s*\{",
            "onClick 箭头函数语法错误"
        )


class TestBracketBalance(unittest.TestCase):
    """测试括号平衡"""

    def setUp(self):
        self.files = [
            HARMONY_DIR / "EntryAbility.ets",
            HARMONY_DIR / "pages/Index.ets",
            HARMONY_DIR / "adapters/MainActivityAdapter.ets",
        ]

    def _check_balance(self, code, open_char, close_char):
        """检查括号平衡"""
        count = 0
        for char in code:
            if char == open_char:
                count += 1
            elif char == close_char:
                count -= 1
            if count < 0:
                return False
        return count == 0

    def test_curly_braces_balanced(self):
        """测试花括号平衡"""
        for file_path in self.files:
            code = file_path.read_text()
            self.assertTrue(
                self._check_balance(code, '{', '}'),
                f"{file_path.name}: 花括号不平衡"
            )

    def test_parentheses_balanced(self):
        """测试圆括号平衡"""
        for file_path in self.files:
            code = file_path.read_text()
            self.assertTrue(
                self._check_balance(code, '(', ')'),
                f"{file_path.name}: 圆括号不平衡"
            )

    def test_square_brackets_balanced(self):
        """测试方括号平衡"""
        for file_path in self.files:
            code = file_path.read_text()
            self.assertTrue(
                self._check_balance(code, '[', ']'),
                f"{file_path.name}: 方括号不平衡"
            )


class TestUIAbilityLifecycle(unittest.TestCase):
    """测试 UIAbility 生命周期方法"""

    def setUp(self):
        self.ability_code = (HARMONY_DIR / "EntryAbility.ets").read_text()

    def test_has_all_lifecycle_methods(self):
        """测试包含所有生命周期方法"""
        required_methods = [
            'onCreate',
            'onDestroy',
            'onWindowStageCreate',
            'onWindowStageDestroy',
            'onForeground',
            'onBackground',
        ]

        for method in required_methods:
            self.assertIn(
                method,
                self.ability_code,
                f"缺少生命周期方法: {method}"
            )

    def test_oncreate_signature(self):
        """测试 onCreate 方法签名"""
        self.assertRegex(
            self.ability_code,
            r"onCreate\s*\(\s*want:\s*Want\s*,\s*launchParam:\s*AbilityConstant\.LaunchParam\s*\)\s*:\s*void",
            "onCreate 方法签名不正确"
        )

    def test_window_stage_create_loads_content(self):
        """测试 onWindowStageCreate 加载页面"""
        self.assertIn("loadContent", self.ability_code)
        self.assertIn("pages/Index", self.ability_code)


class TestArkUIComponents(unittest.TestCase):
    """测试 ArkUI 组件"""

    def setUp(self):
        self.page_code = (HARMONY_DIR / "pages/Index.ets").read_text()

    def test_has_column_layout(self):
        """测试有 Column 布局"""
        self.assertIn("Column()", self.page_code)

    def test_has_text_component(self):
        """测试有 Text 组件"""
        self.assertIn("Text('Hello World')", self.page_code)

    def test_has_button_component(self):
        """测试有 Button 组件"""
        self.assertRegex(self.page_code, r"Button\s*\(")

    def test_button_has_onclick(self):
        """测试 Button 有 onClick 事件"""
        self.assertIn(".onClick(", self.page_code)

    def test_has_style_attributes(self):
        """测试有样式属性"""
        style_attrs = [
            '.fontSize(',
            '.fontWeight(',
            '.width(',
            '.height(',
        ]

        for attr in style_attrs:
            self.assertIn(attr, self.page_code, f"缺少样式属性: {attr}")


class TestApiMappingImplementation(unittest.TestCase):
    """测试 API 映射实现"""

    def setUp(self):
        self.page_code = (HARMONY_DIR / "pages/Index.ets").read_text()
        self.adapter_code = (HARMONY_DIR / "adapters/MainActivityAdapter.ets").read_text()

    def test_finish_mapped_to_terminateself(self):
        """测试 finish() 映射到 terminateSelf()"""
        # 页面中使用 terminateSelf
        self.assertIn("terminateSelf", self.page_code)

        # 适配器中 finish() 调用 terminateSelf()
        self.assertIn("finish()", self.adapter_code)
        self.assertIn("terminateSelf()", self.adapter_code)

    def test_context_used_correctly(self):
        """测试 context 使用正确"""
        # 获取 context
        self.assertIn("getContext(this)", self.page_code)

        # context 类型正确
        self.assertIn("UIAbilityContext", self.page_code)
        self.assertIn("UIAbilityContext", self.adapter_code)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestEtsFilesExist))
    suite.addTests(loader.loadTestsFromTestCase(TestOpenHarmonyImports))
    suite.addTests(loader.loadTestsFromTestCase(TestArkTSSyntax))
    suite.addTests(loader.loadTestsFromTestCase(TestBracketBalance))
    suite.addTests(loader.loadTestsFromTestCase(TestUIAbilityLifecycle))
    suite.addTests(loader.loadTestsFromTestCase(TestArkUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestApiMappingImplementation))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "=" * 70)
    print("OpenHarmony 语法验证总结")
    print("=" * 70)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
