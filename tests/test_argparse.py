import argparse
import os
import unittest
import yaml
from conf_root import ConfRoot


class TestArgparse(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.location = 'argsparse.yaml'

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
        ArgsClass = ConfRoot(self.location).dataclass_from_argparse(parser)

        args_namespace = parser.parse_args(['--arg2', '30'])
        args_dataclass = ArgsClass(**vars(args_namespace))

        self.assertEqual(args_dataclass.arg1, 10)
        self.assertEqual(args_dataclass.arg2, 30)

        self.assertTrue(os.path.exists(self.location))
        with open(self.location, encoding='utf-8') as yaml_file:
            data = yaml.safe_load(yaml_file)
        self.assertEqual(data['arg1'], 10)
        # 配置文件保存的是默认值 而非传入值。
        self.assertEqual(data['arg2'], 20)

    def test_without_default_value(self):
        parser = argparse.ArgumentParser(description="Test without default value")
        parser.add_argument("--default_value", default=40, type=int)
        parser.add_argument("--arg1", type=int)
        parser.add_argument("--arg2", type=int)
        ArgsClass = ConfRoot(self.location).dataclass_from_argparse(parser)

        args_namespace = parser.parse_args(['--arg2', '30'])
        args_dataclass = ArgsClass(**vars(args_namespace))

        self.assertIsNone(args_dataclass.arg1)
        self.assertEqual(args_dataclass.arg2, 30)
        self.assertEqual(args_dataclass.default_value, 40)

        # 注意，因为dataclass中non-default的定义需在default的变量前，所以在ArgsClass的定义中会对他们进行排序。
        args_dataclass2 = ArgsClass(12, 13)
        self.assertEqual(args_dataclass2.default_value, 40)
        self.assertEqual(args_dataclass2.arg1, 12)
        self.assertEqual(args_dataclass2.arg2, 13)

        self.assertTrue(os.path.exists(self.location))
        with open(self.location, encoding='utf-8') as yaml_file:
            data = yaml.safe_load(yaml_file)
        # 配置文件中不会保存没有默认参数的值。
        self.assertFalse(hasattr(data, 'arg1'))
        self.assertFalse(hasattr(data, 'arg2'))
        self.assertEqual(args_dataclass.default_value, 40)

    def test_action(self):
        parser = argparse.ArgumentParser(description="Test action")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
        parser.add_argument('--foo', action='store_const', const=42)
        parser.add_argument("--items", nargs='+', type=str, help="List of items")
        parser.add_argument('--count', '-c', action='count', default=0)
        ArgsClass = ConfRoot(self.location).dataclass_from_argparse(parser)
        args_dataclass = ArgsClass()

        self.assertFalse(hasattr(args_dataclass, 'items'))
        self.assertFalse(hasattr(args_dataclass, 'help'))
        self.assertFalse(hasattr(args_dataclass, 'count'))
        self.assertTrue(args_dataclass.verbose)
        self.assertEqual(args_dataclass.foo, 42)
