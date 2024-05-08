import os.path
import unittest
from dataclasses import dataclass

from conf_root import ConfRoot
from conf_root.agents.JsonAgent import JsonAgent


class MyTestCase(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.default_yaml_location = 'config.yml'
        self.default_json_location = 'config.json'

    def tearDown(self):
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.default_yaml_location)
        except FileNotFoundError:
            pass

        try:
            os.remove(self.default_json_location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def replace_text(self, filename, origin_text, replace_text):
        with open(filename, 'r') as file:
            content = file.read()
        content = content.replace(origin_text, replace_text)
        with open(filename, 'w') as file:
            file.write(content)

    def test_default_yaml_configuration(self):
        # 测试直接使用configuration而不带参数的情况。
        @ConfRoot().wrap
        @dataclass
        class AppConfig:
            something: int = 42

        app_config = AppConfig()
        self.assertTrue(os.path.exists(self.default_yaml_location))
        with open(self.default_yaml_location, 'r') as file:
            content = file.read()
        self.assertTrue('42' in content)
        self.replace_text(self.default_yaml_location, '42', '43')
        app_config2 = AppConfig()
        self.assertEqual(app_config2.something, 43)

    def test_default_json_configuration(self):
        @ConfRoot(agent=JsonAgent).wrap
        @dataclass
        class AppConfig:
            something: int = 42

        app_config = AppConfig()
        self.assertTrue(os.path.exists(self.default_json_location))
        with open(self.default_json_location, 'r') as file:
            content = file.read()
        self.assertTrue('42' in content)
        self.replace_text(self.default_json_location, '42', '43')
        app_config2 = AppConfig()
        self.assertEqual(app_config2.something, 43)


if __name__ == '__main__':
    unittest.main()
