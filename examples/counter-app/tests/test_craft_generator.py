#!/usr/bin/env python3
"""
CRAFT Framework - 生成器测试套件

测试覆盖:
1. Java 解析器 - 验证能正确解析 Android 代码
2. API 映射 - 验证映射规则正确
3. 代码生成 - 验证生成的代码结构正确
4. OpenHarmony API 风格 - 验证使用 @ohos.xxx 导入
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from craft_generate import JavaParser, HarmonyGenerator, ClassInfo, MethodInfo, API_MAPPING


class TestJavaParser(unittest.TestCase):
    """测试 Java 解析器"""

    def setUp(self):
        self.parser = JavaParser()
        self.test_java_code = '''
package com.example.counter;

import android.app.Activity;
import android.os.Bundle;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void onClick(View v) {
        finish();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
    }
}
'''

    def test_parse_package_name(self):
        """测试包名解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(self.test_java_code)
            f.flush()

            class_info = self.parser.parse_file(f.name)
            self.assertEqual(class_info.package, 'com.example.counter')

            os.unlink(f.name)

    def test_parse_class_name(self):
        """测试类名解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(self.test_java_code)
            f.flush()

            class_info = self.parser.parse_file(f.name)
            self.assertEqual(class_info.name, 'MainActivity')

            os.unlink(f.name)

    def test_parse_parent_class(self):
        """测试父类解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(self.test_java_code)
            f.flush()

            class_info = self.parser.parse_file(f.name)
            self.assertEqual(class_info.parent, 'Activity')

            os.unlink(f.name)

    def test_parse_methods(self):
        """测试方法解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(self.test_java_code)
            f.flush()

            class_info = self.parser.parse_file(f.name)
            method_names = [m.name for m in class_info.methods]

            self.assertIn('onCreate', method_names)
            self.assertIn('onClick', method_names)
            self.assertIn('onDestroy', method_names)

            os.unlink(f.name)

    def test_identify_lifecycle_methods(self):
        """测试生命周期方法识别"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(self.test_java_code)
            f.flush()

            class_info = self.parser.parse_file(f.name)

            for method in class_info.methods:
                if method.name == 'onCreate':
                    self.assertTrue(method.is_lifecycle)
                elif method.name == 'onDestroy':
                    self.assertTrue(method.is_lifecycle)
                elif method.name == 'onClick':
                    self.assertFalse(method.is_lifecycle)

            os.unlink(f.name)


class TestApiMapping(unittest.TestCase):
    """测试 API 映射规则"""

    def test_finish_mapping_exists(self):
        """测试 finish() 映射存在"""
        self.assertIn('finish', API_MAPPING)

    def test_finish_maps_to_terminate_self(self):
        """测试 finish() -> terminateSelf() 映射"""
        self.assertEqual(API_MAPPING['finish']['target'], 'terminateSelf')

    def test_oncreate_mapping_exists(self):
        """测试 onCreate() 映射存在"""
        self.assertIn('onCreate', API_MAPPING)

    def test_ondestroy_mapping_exists(self):
        """测试 onDestroy() 映射存在"""
        self.assertIn('onDestroy', API_MAPPING)

    def test_lifecycle_methods_in_mapping(self):
        """测试所有生命周期方法都有映射"""
        required_mappings = ['finish', 'onCreate', 'onDestroy']
        for method in required_mappings:
            self.assertIn(method, API_MAPPING, f"缺少 {method} 的映射")


class TestHarmonyGenerator(unittest.TestCase):
    """测试代码生成器"""

    def setUp(self):
        self.generator = HarmonyGenerator()
        self.class_info = ClassInfo(
            package='com.example.counter',
            name='MainActivity',
            parent='Activity',
            methods=[
                MethodInfo('onCreate', 'void', [('Bundle', 'savedInstanceState')], True),
                MethodInfo('onDestroy', 'void', [], True),
            ]
        )

    def test_generate_ability_not_empty(self):
        """测试 UIAbility 生成不为空"""
        code = self.generator.generate_ability(self.class_info)
        self.assertTrue(len(code) > 0)

    def test_generate_ability_has_class_declaration(self):
        """测试 UIAbility 包含类声明"""
        code = self.generator.generate_ability(self.class_info)
        self.assertIn('class EntryAbility extends UIAbility', code)

    def test_generate_ability_has_lifecycle_methods(self):
        """测试 UIAbility 包含生命周期方法"""
        code = self.generator.generate_ability(self.class_info)
        self.assertIn('onCreate', code)
        self.assertIn('onDestroy', code)
        self.assertIn('onWindowStageCreate', code)
        self.assertIn('onForeground', code)
        self.assertIn('onBackground', code)

    def test_generate_page_not_empty(self):
        """测试页面生成不为空"""
        code = self.generator.generate_page(self.class_info)
        self.assertTrue(len(code) > 0)

    def test_generate_page_has_component(self):
        """测试页面包含组件声明"""
        code = self.generator.generate_page(self.class_info)
        self.assertIn('@Entry', code)
        self.assertIn('@Component', code)
        self.assertIn('struct Index', code)

    def test_generate_page_has_ui_elements(self):
        """测试页面包含 UI 元素"""
        code = self.generator.generate_page(self.class_info)
        self.assertIn('Text(', code)
        self.assertIn('Button(', code)
        self.assertIn('Column()', code)

    def test_generate_page_has_close_window(self):
        """测试页面包含关闭窗口方法"""
        code = self.generator.generate_page(self.class_info)
        self.assertIn('closeWindow', code)
        self.assertIn('terminateSelf', code)

    def test_generate_adapter_not_empty(self):
        """测试适配器生成不为空"""
        code = self.generator.generate_adapter(self.class_info)
        self.assertTrue(len(code) > 0)

    def test_generate_adapter_has_class(self):
        """测试适配器包含类声明"""
        code = self.generator.generate_adapter(self.class_info)
        self.assertIn('class MainActivityAdapter', code)

    def test_generate_adapter_has_finish_method(self):
        """测试适配器包含 finish() 方法"""
        code = self.generator.generate_adapter(self.class_info)
        self.assertIn('finish()', code)
        self.assertIn('terminateSelf()', code)


class TestOpenHarmonyApiStyle(unittest.TestCase):
    """测试 OpenHarmony API 风格 (@ohos.xxx)"""

    def setUp(self):
        self.generator = HarmonyGenerator()
        self.class_info = ClassInfo(
            package='com.example.counter',
            name='MainActivity',
            parent='Activity',
            methods=[]
        )

    def test_ability_uses_ohos_imports(self):
        """测试 UIAbility 使用 @ohos.xxx 导入"""
        code = self.generator.generate_ability(self.class_info)

        # 验证使用 @ohos.xxx 风格
        self.assertIn("from '@ohos.app.ability.UIAbility'", code)
        self.assertIn("from '@ohos.app.ability.AbilityConstant'", code)
        self.assertIn("from '@ohos.app.ability.Want'", code)
        self.assertIn("from '@ohos.window'", code)
        self.assertIn("from '@ohos.hilog'", code)

        # 验证没有使用 @kit.xxx 风格
        self.assertNotIn("@kit.", code)

    def test_page_uses_ohos_imports(self):
        """测试页面使用 @ohos.xxx 导入"""
        code = self.generator.generate_page(self.class_info)

        # 验证使用 @ohos.xxx 风格
        self.assertIn("from '@ohos.app.ability.common'", code)
        self.assertIn("from '@ohos.hilog'", code)

        # 验证没有使用 @kit.xxx 风格
        self.assertNotIn("@kit.", code)

    def test_adapter_uses_ohos_imports(self):
        """测试适配器使用 @ohos.xxx 导入"""
        code = self.generator.generate_adapter(self.class_info)

        # 验证使用 @ohos.xxx 风格
        self.assertIn("from '@ohos.app.ability.UIAbility'", code)
        self.assertIn("from '@ohos.app.ability.common'", code)
        self.assertIn("from '@ohos.hilog'", code)

        # 验证没有使用 @kit.xxx 风格
        self.assertNotIn("@kit.", code)


class TestLifecycleMapping(unittest.TestCase):
    """测试 Activity -> UIAbility 生命周期映射"""

    def test_oncreate_maps_to_oncreate(self):
        """测试 onCreate -> onCreate"""
        # Android Activity.onCreate() 应该映射到 UIAbility.onCreate()
        self.assertEqual(API_MAPPING['onCreate']['target'], 'onCreate')

    def test_ondestroy_maps_to_ondestroy(self):
        """测试 onDestroy -> onDestroy"""
        # Android Activity.onDestroy() 应该映射到 UIAbility.onDestroy()
        self.assertEqual(API_MAPPING['onDestroy']['target'], 'onDestroy')

    def test_finish_maps_to_terminateself(self):
        """测试 finish() -> terminateSelf()"""
        # Android Activity.finish() 应该映射到 UIAbilityContext.terminateSelf()
        self.assertEqual(API_MAPPING['finish']['target'], 'terminateSelf')
        self.assertIn('UIAbilityContext', API_MAPPING['finish']['harmony_api'])


class TestGeneratedCodeStructure(unittest.TestCase):
    """测试生成代码结构"""

    def setUp(self):
        self.generator = HarmonyGenerator()
        self.class_info = ClassInfo(
            package='com.example.counter',
            name='MainActivity',
            parent='Activity',
            methods=[]
        )

    def test_ability_has_correct_structure(self):
        """测试 UIAbility 结构正确"""
        code = self.generator.generate_ability(self.class_info)

        # 检查必要的结构元素
        required_elements = [
            'export default class',
            'extends UIAbility',
            'onCreate(want: Want',
            'onWindowStageCreate(windowStage:',
            'onDestroy():',
            'onForeground():',
            'onBackground():',
            'loadContent(',
        ]

        for element in required_elements:
            self.assertIn(element, code, f"缺少: {element}")

    def test_page_has_correct_structure(self):
        """测试 ArkUI 页面结构正确"""
        code = self.generator.generate_page(self.class_info)

        required_elements = [
            '@Entry',
            '@Component',
            'struct Index',
            'build()',
            'Column()',
            "Text('Hello World')",
            "Button(",
            '.onClick(',
            'getContext(this)',
            'UIAbilityContext',
        ]

        for element in required_elements:
            self.assertIn(element, code, f"缺少: {element}")

    def test_adapter_has_correct_structure(self):
        """测试适配器结构正确"""
        code = self.generator.generate_adapter(self.class_info)

        required_elements = [
            'export class MainActivityAdapter',
            'private context: common.UIAbilityContext',
            'constructor(context:',
            'finish(): void',
            'terminateSelf()',
            'onCreate(): void',
            'onDestroy(): void',
        ]

        for element in required_elements:
            self.assertIn(element, code, f"缺少: {element}")


class TestTypeAnnotations(unittest.TestCase):
    """测试 TypeScript 类型注解"""

    def setUp(self):
        self.generator = HarmonyGenerator()
        self.class_info = ClassInfo(
            package='com.example.counter',
            name='MainActivity',
            parent='Activity',
            methods=[]
        )

    def test_ability_has_type_annotations(self):
        """测试 UIAbility 有类型注解"""
        code = self.generator.generate_ability(self.class_info)

        # 检查类型注解
        self.assertIn('const TAG: string', code)
        self.assertIn('const DOMAIN: number', code)
        self.assertIn('want: Want', code)
        self.assertIn('launchParam: AbilityConstant.LaunchParam', code)
        self.assertIn('): void', code)

    def test_page_has_type_annotations(self):
        """测试页面有类型注解"""
        code = self.generator.generate_page(self.class_info)

        self.assertIn('const TAG: string', code)
        self.assertIn('const DOMAIN: number', code)
        self.assertIn('context: common.UIAbilityContext', code)
        self.assertIn('): void', code)

    def test_adapter_has_type_annotations(self):
        """测试适配器有类型注解"""
        code = self.generator.generate_adapter(self.class_info)

        self.assertIn('const TAG: string', code)
        self.assertIn('const DOMAIN: number', code)
        self.assertIn('private context: common.UIAbilityContext', code)
        self.assertIn('): void', code)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestJavaParser))
    suite.addTests(loader.loadTestsFromTestCase(TestApiMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestHarmonyGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestOpenHarmonyApiStyle))
    suite.addTests(loader.loadTestsFromTestCase(TestLifecycleMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneratedCodeStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeAnnotations))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "=" * 70)
    print("测试总结")
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
