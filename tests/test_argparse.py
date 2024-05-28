import argparse
import os
import unittest

from conf_root import ConfRoot


class TestArgparse(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.location = 'ArgparseConfig.yml'

        self.parser = argparse.ArgumentParser(description="Test without default value")
        self.parser.add_argument("--default_value", default=40, type=int)
        self.parser.add_argument("--arg1", type=int)
        self.parser.add_argument("--arg2", type=int)

    def tearDown(self):
        # 这个方法将在每个测试方法结束后运行
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_with_default_value(self):
        parser = argparse.ArgumentParser(description="Test with default value")
        parser.add_argument("--arg1", default=10, type=int, help="Number 1")
        parser.add_argument("--arg2", default=20, type=int, help="Number 2")
        ArgsClass = ConfRoot().from_argparse(parser, self.location)

        args_namespace = parser.parse_args(['--arg2', '30'])
        args_dataclass = ArgsClass(**vars(args_namespace))

        self.assertEqual(args_dataclass.arg1, 10)
        self.assertEqual(args_dataclass.arg2, 30)

        self.assertTrue(os.path.exists(self.location))
        with open(self.location, encoding='utf-8') as yaml_file:
            content = yaml_file.read()
        self.assertTrue('arg1: 10' in content)
        self.assertTrue('arg2: 30' in content)

    def test_without_default_value(self):
        ArgsClass = ConfRoot().from_argparse(self.parser)

        args_namespace = self.parser.parse_args(['--arg2', '30'])
        args_dataclass = ArgsClass(**vars(args_namespace))

        self.assertIsNone(args_dataclass.arg1)
        self.assertEqual(args_dataclass.arg2, 30)
        self.assertEqual(args_dataclass.default_value, 40)

    def test_without_default_value2(self):
        parser = argparse.ArgumentParser(description="Test without default value")
        parser.add_argument("--default_value", default=40, type=int)
        parser.add_argument("--arg1", type=int, required=True)
        parser.add_argument("--arg2", type=int, required=True)

        ArgsClass = ConfRoot().from_argparse(parser)

        # 注意，因为dataclass中non-default的定义需在default的变量前，所以在ArgsClass的定义中会将required的函数提到最前。
        args_dataclass = ArgsClass(12, 13)
        # print(args_dataclass)
        self.assertEqual(args_dataclass.default_value, 40)
        self.assertEqual(args_dataclass.arg1, 12)
        self.assertEqual(args_dataclass.arg2, 13)

    def test_action(self):
        parser = argparse.ArgumentParser(description="Test action")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
        parser.add_argument('--foo', action='store_const', const=42)
        parser.add_argument("--items", nargs='+', type=str, help="List of items")
        parser.add_argument('--count', '-c', action='count', default=0)
        ArgsClass = ConfRoot().from_argparse(parser)
        args_dataclass = ArgsClass()

        self.assertFalse(hasattr(args_dataclass, 'help'))
        self.assertTrue(args_dataclass.verbose)
        self.assertEqual(args_dataclass.foo, 42)
