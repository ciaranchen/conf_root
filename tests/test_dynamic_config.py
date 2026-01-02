import os
import unittest
from dataclasses import dataclass
from unittest import skip

from conf_root import ConfRoot


class TestDynamicConfig(unittest.TestCase):
    def setUp(self):
        self.filename1 = 'test_dynamic1.yml'
        self.filename2 = 'test_dynamic2.yml'

    def tearDown(self):
        for filename in [self.filename1, self.filename2]:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def test_dynamic_location(self):
        """测试动态修改配置文件路径"""
        @ConfRoot().config(self.filename1)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 第一次创建实例，使用默认路径
        app_config1 = AppConfig()
        self.assertTrue(os.path.exists(self.filename1))
        self.assertFalse(os.path.exists(self.filename2))

        # 动态修改配置文件路径
        AppConfig.__CONF_LOCATION__ = self.filename2

        # 第二次创建实例，使用新路径
        app_config2 = AppConfig(name='dynamic')
        self.assertTrue(os.path.exists(self.filename2))

        # 验证新文件内容
        with open(self.filename2, 'r') as f:
            content = f.read()
        self.assertIn('name: dynamic', content)

    def test_agent_class_none(self):
        """测试 agent_class 为 None 时不生成配置文件"""
        @ConfRoot(agent_class=None).config(self.filename1)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 创建实例，不应该生成配置文件
        app_config = AppConfig(name='test')
        self.assertFalse(os.path.exists(self.filename1))
