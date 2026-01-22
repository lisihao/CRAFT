#!/usr/bin/env python3
"""
CRAFT Framework - 运行所有测试

测试套件:
1. test_craft_generator.py - 生成器逻辑测试
2. test_openharmony_syntax.py - OpenHarmony 代码语法验证
"""

import os
import sys
import unittest
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_craft_generator import (
    TestJavaParser,
    TestApiMapping,
    TestHarmonyGenerator,
    TestOpenHarmonyApiStyle,
    TestLifecycleMapping,
    TestGeneratedCodeStructure,
    TestTypeAnnotations,
)

from tests.test_openharmony_syntax import (
    TestEtsFilesExist,
    TestOpenHarmonyImports,
    TestArkTSSyntax,
    TestBracketBalance,
    TestUIAbilityLifecycle,
    TestArkUIComponents,
    TestApiMappingImplementation,
)


def print_header(title: str):
    """打印分隔标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_all_tests():
    """运行所有测试套件"""
    print_header("CRAFT Framework - 完整测试套件")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python 版本: {sys.version}")
    print()

    # 创建测试套件
    loader = unittest.TestLoader()
    master_suite = unittest.TestSuite()

    # ========================================
    # 测试组 1: 生成器逻辑测试
    # ========================================
    print_header("测试组 1: 生成器逻辑测试")

    generator_tests = [
        TestJavaParser,
        TestApiMapping,
        TestHarmonyGenerator,
        TestOpenHarmonyApiStyle,
        TestLifecycleMapping,
        TestGeneratedCodeStructure,
        TestTypeAnnotations,
    ]

    generator_suite = unittest.TestSuite()
    for test_class in generator_tests:
        generator_suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    generator_result = runner.run(generator_suite)

    # ========================================
    # 测试组 2: OpenHarmony 语法验证
    # ========================================
    print_header("测试组 2: OpenHarmony 语法验证")

    syntax_tests = [
        TestEtsFilesExist,
        TestOpenHarmonyImports,
        TestArkTSSyntax,
        TestBracketBalance,
        TestUIAbilityLifecycle,
        TestArkUIComponents,
        TestApiMappingImplementation,
    ]

    syntax_suite = unittest.TestSuite()
    for test_class in syntax_tests:
        syntax_suite.addTests(loader.loadTestsFromTestCase(test_class))

    syntax_result = runner.run(syntax_suite)

    # ========================================
    # 总体结果
    # ========================================
    print_header("测试结果总结")

    total_run = generator_result.testsRun + syntax_result.testsRun
    total_failures = len(generator_result.failures) + len(syntax_result.failures)
    total_errors = len(generator_result.errors) + len(syntax_result.errors)
    total_success = total_run - total_failures - total_errors

    print(f"生成器测试:")
    print(f"  运行: {generator_result.testsRun}")
    print(f"  成功: {generator_result.testsRun - len(generator_result.failures) - len(generator_result.errors)}")
    print(f"  失败: {len(generator_result.failures)}")
    print(f"  错误: {len(generator_result.errors)}")
    print()

    print(f"语法验证测试:")
    print(f"  运行: {syntax_result.testsRun}")
    print(f"  成功: {syntax_result.testsRun - len(syntax_result.failures) - len(syntax_result.errors)}")
    print(f"  失败: {len(syntax_result.failures)}")
    print(f"  错误: {len(syntax_result.errors)}")
    print()

    print("-" * 40)
    print(f"总计:")
    print(f"  运行: {total_run}")
    print(f"  成功: {total_success}")
    print(f"  失败: {total_failures}")
    print(f"  错误: {total_errors}")
    print(f"  通过率: {total_success / total_run * 100:.1f}%")
    print()

    # 关键设计验证
    print_header("关键设计验证")

    key_validations = [
        ("Java 解析器能正确解析 Android 代码", len(generator_result.failures) == 0),
        ("API 映射规则正确 (finish -> terminateSelf)", "TestApiMapping" not in str(generator_result.failures)),
        ("生命周期映射正确 (Activity -> UIAbility)", "TestLifecycleMapping" not in str(generator_result.failures)),
        ("使用 OpenHarmony API 风格 (@ohos.xxx)", "TestOpenHarmonyApiStyle" not in str(generator_result.failures) and "TestOpenHarmonyImports" not in str(syntax_result.failures)),
        ("生成代码语法正确", "TestArkTSSyntax" not in str(syntax_result.failures)),
        ("括号平衡检查", "TestBracketBalance" not in str(syntax_result.failures)),
        ("UIAbility 生命周期完整", "TestUIAbilityLifecycle" not in str(syntax_result.failures)),
        ("ArkUI 组件正确", "TestArkUIComponents" not in str(syntax_result.failures)),
    ]

    all_passed = True
    for validation, passed in key_validations:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {validation}")
        if not passed:
            all_passed = False

    print()
    print("=" * 70)
    if all_passed and total_failures == 0 and total_errors == 0:
        print("  🎉 所有测试通过！关键设计验证成功！")
    else:
        print("  ⚠️  存在测试失败，请检查上述详细信息")
    print("=" * 70)

    return total_failures == 0 and total_errors == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
