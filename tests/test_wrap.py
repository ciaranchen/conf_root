import os.path
import unittest
from dataclasses import dataclass

from conf_root import ConfRoot


class TestWrap(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.location = 'config.yml'

        @dataclass
        class AppConfig:
            num1: int = 42

        self.conf_class = AppConfig
        self.q_location = AppConfig.__qualname__.replace('<locals>.', '') + '.yml'

    def tearDown(self):
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.location)
        except FileNotFoundError:
            pass

        try:
            os.remove(self.q_location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_wrap_direct(self):
        # @ConfRoot().config
        ConfRoot().config(self.conf_class)()
        self.assertTrue(os.path.exists(self.q_location))

    def test_wrap_no_args(self):
        # @ConfRoot().config()
        ConfRoot().config()(self.conf_class)()
        self.assertTrue(os.path.exists(self.q_location))

    def test_wrap_with_args(self):
        # @ConfRoot().config(self.location)
        ConfRoot().config(self.location)(self.conf_class)()
        self.assertTrue(os.path.exists(self.location))

    def test_wrap_with_named_args(self):
        # @ConfRoot().config(name=self.location)
        ConfRoot().config(name=self.location)(self.conf_class)()
        self.assertTrue(os.path.exists(self.location))

    def test_wrap_dynamic(self):
        conf = ConfRoot().config(self.location, True)(self.conf_class)()
        self.assertTrue(os.path.exists(self.location))
        self.assertTrue(hasattr(conf, 'save'))
        self.assertTrue(hasattr(conf, 'load'))

    def test_wrap_named_dynamic(self):
        conf = ConfRoot().config(dynamic=True)(self.conf_class)()
        self.assertTrue(os.path.exists(self.q_location))
        self.assertTrue(hasattr(conf, 'save'))
        self.assertTrue(hasattr(conf, 'load'))

    def test_without_dataclass(self):
        @ConfRoot().config(self.location)
        class AppConfig:
            num1: int = 42

        conf = AppConfig()
        self.assertTrue(os.path.exists(self.location))
