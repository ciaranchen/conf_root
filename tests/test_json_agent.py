import os
import unittest
from dataclasses import dataclass

from conf_root import configuration, JsonAgent


@dataclass
class AppConfig:
    not_default: str
    database_host: str = 'localhost'
    database_port: int = 5432


class TestConfig(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.location = 'settings.json'

    def tearDown(self):
        # 这个方法将在每个测试方法结束后运行
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_create(self):
        DecoratedConfig = configuration(self.location, agent=JsonAgent)(AppConfig)
        app_config = DecoratedConfig('admin')
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

    def test_load(self):
        content = """{"database_host": "127.0.0.1", "database_port": 5432}"""
        # 将处理后的内容写回文件（可以先备份原文件）
        with open(self.location, 'w') as file:
            file.write(content)

        DecoratedConfig = configuration(self.location, agent=JsonAgent)(AppConfig)
        app_config = DecoratedConfig('admin')
        self.assertEqual(app_config.database_host, '127.0.0.1')
        self.assertEqual(app_config.database_port, 5432)

    def test_save(self):
        DecoratedConfig = configuration(self.location, agent=JsonAgent)(AppConfig)
        app_config = DecoratedConfig('admin')
        app_config.database_host = '192.168.1.1'
        app_config.database_port = 3309
        app_config.save()

        # 外部修改配置文件后读取，结果应为配置文件内的设置。
        # 打开文件，读取内容
        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('192.168.1.1' in content)
        self.assertTrue('3309' in content)
        self.assertTrue('admin' in content)
