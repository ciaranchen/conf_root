import os
import unittest
from dataclasses import dataclass

from conf_root import ConfRoot


class TestPriority(unittest.TestCase):
    def setUp(self):
        self.filename = 'test_priority.yml'

    def tearDown(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def test_priority_file(self):
        """测试优先级为'file'时，文件内容优先于参数"""
        @ConfRoot(priority='file').config(self.filename)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 第一次创建实例，生成配置文件
        app_config1 = AppConfig(name='created', value=100)
        self.assertEqual(app_config1.name, 'created')
        self.assertEqual(app_config1.value, 100)

        # 手动修改配置文件
        with open(self.filename, 'w') as f:
            f.write('name: modified\nvalue: 200\n')

        # 第二次创建实例，应该使用文件中的值
        app_config2 = AppConfig(name='override', value=300)
        self.assertEqual(app_config2.name, 'modified')  # 文件值优先
        self.assertEqual(app_config2.value, 200)  # 文件值优先

    def test_priority_param(self):
        """测试优先级为'param'时，参数优先于文件内容"""
        @ConfRoot(priority='param').config(self.filename)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 第一次创建实例，生成配置文件
        app_config1 = AppConfig(name='created', value=100)
        self.assertEqual(app_config1.name, 'created')
        self.assertEqual(app_config1.value, 100)

        # 手动修改配置文件
        with open(self.filename, 'w') as f:
            f.write('name: modified\nvalue: 200\n')

        # 第二次创建实例，应该使用参数值
        app_config2 = AppConfig(name='override', value=300)
        self.assertEqual(app_config2.name, 'override')  # 参数值优先
        self.assertEqual(app_config2.value, 300)  # 参数值优先
