import unittest

import os
import unittest
from dataclasses import dataclass

from conf_root import ConfRoot
from conf_root.agents.RuamelYamlAgent import RuamelYamlAgent


class TestRuamelYamlAgent(unittest.TestCase):
    location = 'settings.yml'

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.conf_root = ConfRoot(self.location, agent_class=RuamelYamlAgent)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(cls.location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_create(self):
        @self.conf_root.wrap
        @dataclass
        class AppConfig:
            not_default: str
            database_host: str = 'localhost'
            database_port: int = 5432

        app_config = AppConfig('admin')
        self.assertEqual(app_config.database_host, 'localhost')
        self.assertEqual(app_config.database_port, 5432)
        self.assertEqual(app_config.not_default, 'admin')

        # 外部修改配置文件后读取，结果应为配置文件内的设置。
        # 打开文件，读取内容
        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('localhost' in content)
        self.assertTrue('5432' in content)
        # admin 因为非默认配置，不在配置文件中。
        self.assertFalse('admin' in content)
