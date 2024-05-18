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
        self.qualname_location = 'TestWrap.__init__.AppConfig.yml'

    def tearDown(self):
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.location)
        except FileNotFoundError:
            pass

        try:
            os.remove(self.qualname_location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_wrap_direct(self):
        # @ConfRoot().wrap
        conf_class = ConfRoot().wrap(self.conf_class)
        conf = conf_class()
        self.assertTrue(os.path.exists(self.qualname_location))

    def test_wrap_no_args(self):
        # @ConfRoot().wrap()
        conf_class = ConfRoot().wrap()(self.conf_class)
        conf = conf_class()
        self.assertTrue(os.path.exists(self.qualname_location))

    def test_wrap_with_args(self):
        # @ConfRoot().wrap(self.location)
        conf_class = ConfRoot().wrap(self.location)(self.conf_class)
        conf = conf_class()
        self.assertTrue(os.path.exists(self.location))

    def test_wrap_with_named_args(self):
        # @ConfRoot().wrap(self.location)
        conf_class = ConfRoot().wrap(name=self.location)(self.conf_class)
        conf = conf_class()
        self.assertTrue(os.path.exists(self.location))

    def test_without_dataclass(self):
        @ConfRoot().wrap(self.location)
        class AppConfig:
            num1: int = 42

        conf = AppConfig()
        self.assertTrue(os.path.exists(self.location))


if __name__ == '__main__':
    unittest.main()
