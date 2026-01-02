import os
import unittest
from dataclasses import dataclass

from conf_root import ConfRoot


class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.filename = 'test_error_handling.yml'

    def tearDown(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def test_required_field_missing(self):
        """测试必填字段缺失时的行为"""
        @ConfRoot().config(self.filename)
        @dataclass
        class AppConfig:
            name: str  # 没有默认值，必填
            value: int = 42

        # 应该抛出验证错误，因为必填字段name缺失
        with self.assertRaises(Exception):
            app_config = AppConfig()

    def test_type_mismatch(self):
        """测试类型不匹配时的行为"""
        @ConfRoot().config(self.filename)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 第一次创建实例，生成配置文件
        app_config1 = AppConfig()
        self.assertEqual(app_config1.value, 42)

        # 手动修改配置文件，将int类型改为str
        with open(self.filename, 'w') as f:
            f.write('name: test\nvalue: not_an_int\n')

        # 应该抛出类型转换错误
        with self.assertRaises(Exception):
            app_config2 = AppConfig()

    def test_invalid_yaml(self):
        """测试配置文件格式错误时的行为"""
        # 创建一个格式错误的YAML文件
        with open(self.filename, 'w') as f:
            f.write('name: test\nvalue: 42\n  invalid: yaml\n')

        @ConfRoot().config(self.filename)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 应该抛出解析错误
        with self.assertRaises(Exception):
            app_config = AppConfig()

    def test_non_existent_file(self):
        """测试配置文件不存在时的行为"""
        # 使用一个不存在的文件
        non_existent_file = 'non_existent.yml'
        # 确保文件不存在
        if os.path.exists(non_existent_file):
            os.remove(non_existent_file)

        @ConfRoot().config(non_existent_file)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 应该正常创建实例并生成文件
        app_config = AppConfig()
        self.assertTrue(os.path.exists(non_existent_file))
        os.remove(non_existent_file)

    def test_empty_file(self):
        """测试空配置文件时的行为"""
        # 创建一个空文件
        with open(self.filename, 'w') as f:
            f.write('')

        @ConfRoot().config(self.filename)
        @dataclass
        class AppConfig:
            name: str = 'default'
            value: int = 42

        # 应该使用默认值
        app_config = AppConfig()
        self.assertEqual(app_config.name, 'default')
        self.assertEqual(app_config.value, 42)
