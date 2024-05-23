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
        # @ConfRoot().wrap
        ConfRoot().wrap(self.conf_class)()
        self.assertTrue(os.path.exists(self.q_location))

    def test_wrap_no_args(self):
        # @ConfRoot().wrap()
        ConfRoot().wrap()(self.conf_class)()
        self.assertTrue(os.path.exists(self.q_location))

    def test_wrap_with_args(self):
        # @ConfRoot().wrap(self.location)
        ConfRoot().wrap(self.location)(self.conf_class)()
        self.assertTrue(os.path.exists(self.location))

    def test_wrap_with_named_args(self):
        # @ConfRoot().wrap(name=self.location)
        ConfRoot().wrap(name=self.location)(self.conf_class)()
        self.assertTrue(os.path.exists(self.location))

    def test_wrap_dynamic(self):
        conf = ConfRoot().wrap(self.location, True)(self.conf_class)()
        self.assertTrue(os.path.exists(self.location))
        self.assertTrue(hasattr(conf, 'save'))
        self.assertTrue(hasattr(conf, 'load'))

    def test_wrap_named_dynamic(self):
        conf = ConfRoot().wrap(dynamic=True)(self.conf_class)()
        self.assertTrue(os.path.exists(self.q_location))
        self.assertTrue(hasattr(conf, 'save'))
        self.assertTrue(hasattr(conf, 'load'))

    def test_without_dataclass(self):
        @ConfRoot().wrap(self.location)
        class AppConfig:
            num1: int = 42

        conf = AppConfig()
        self.assertTrue(os.path.exists(self.location))


if __name__ == '__main__':
    unittest.main()
