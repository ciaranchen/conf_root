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
        parser = argparse.ArgumentParser(description="Test action from argparse documentation")
        parser.add_argument('--foo', action='store_const', const=42)
        parser.add_argument('--bar', action='store_true')
        parser.add_argument('--baz', action='store_false')

        parser.add_argument('--append', action='append')
        # parser.add_argument('--str', dest='types', action='append_const', const=str)
        # parser.add_argument('--int', dest='types', action='append_const', const=int)
        parser.add_argument("--extend", action="extend", nargs="+", type=str)
        parser.add_argument('--count', '-v', action='count', default=0)

        parser.add_argument('--version', action='version', version='%(prog)s 2.0')

        parser.add_argument('--opt', action=argparse.BooleanOptionalAction)
        ArgsClass = ConfRoot().from_argparse(parser)
        ns = parser.parse_args(
            # --str - -int
            '--foo --bar --baz --append 1 --append 2 --extend f1 f2 f3 -vvv --no-opt'.split())
        print(vars(ns))
        args_dataclass = ArgsClass(**vars(ns))

        self.assertEqual(args_dataclass.foo, 42)
        self.assertEqual(args_dataclass.bar, True)
        self.assertEqual(args_dataclass.baz, False)
        self.assertEqual(len(args_dataclass.append), 2)
        self.assertEqual(len(args_dataclass.extend), 3)
        self.assertEqual(args_dataclass.count, 3)
        self.assertEqual(args_dataclass.opt, False)


    def test_skip_action(self):
        class FooAction(argparse.Action):
            def __init__(self, option_strings, dest, nargs=None, **kwargs):
                if nargs is not None:
                    raise ValueError("nargs not allowed")
                super().__init__(option_strings, dest, **kwargs)

            def __call__(self, parser, namespace, values, option_string=None):
                print('%r %r %r' % (namespace, values, option_string))
                setattr(namespace, self.dest, values)

        parser = argparse.ArgumentParser()
        parser.add_argument('--foo', action=FooAction)
        parser.add_argument('bar', action=FooAction)

        ns = parser.parse_args('1 --foo 2'.split())
        ArgsClass = ConfRoot().from_argparse(parser)
        args_dataclass = ArgsClass(**vars(ns))


