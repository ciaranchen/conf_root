import unittest

import os
import unittest
from dataclasses import dataclass

from conf_root import ConfRoot
from conf_root.agents.SingleFileYamlAgent import SingleFileYamlAgent
from tests.utils import replace_text


class TestSingleFileYamlAgent(unittest.TestCase):
    location = 'settings.yml'

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.conf_root = ConfRoot(self.location, agent_class=SingleFileYamlAgent)

        @self.conf_root.wrap
        @dataclass
        class AppConfig:
            not_default: str
            database_host: str = 'localhost'
            database_port: int = 5432

        @self.conf_root.wrap
        @dataclass
        class AppConfig2:
            one_thing: int = 42
            another_thing: int = 1024

        self.conf1 = AppConfig
        self.conf2 = AppConfig2
        self.section_name1 = self.conf1.__CONF_ROOT__.name
        self.section_name2 = self.conf2.__CONF_ROOT__.name

    @staticmethod
    def replace_text(filename, origin_text, replace_text):
        with open(filename, 'r') as file:
            content = file.read()
        content = content.replace(origin_text, replace_text)
        with open(filename, 'w') as file:
            file.write(content)

    def tearDown(self):
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_create(self):
        app_config = self.conf1('admin')
        app_config2 = self.conf2()

        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue(self.section_name1 in content)
        self.assertTrue(self.section_name2 in content)

    def test_save_and_load(self):
        app_config = self.conf1('admin')
        app_config2 = self.conf2()

        app_config.database_port = 9527
        app_config.save()

        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('9527' in content)
        self.assertTrue(self.section_name2 in content)

        replace_text(self.location, '42', '43')
        conf2 = self.conf2()
        self.assertEqual(conf2.one_thing, 43)
        self.assertEqual(conf2.another_thing, 1024)


