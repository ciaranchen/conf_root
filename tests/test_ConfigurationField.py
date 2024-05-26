import os
import unittest
from typing import List

from conf_root import ConfRoot
from dataclasses import field


class TestConfigurationField(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.location = 'config.yml'

    def tearDown(self):
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_default_factory(self):
        @ConfRoot(agent_class=None).config
        class AppConfig:
            name: list = field(default_factory=list)

        app_config = AppConfig()
        self.assertTrue(isinstance(app_config.name, list))
        self.assertEqual(len(app_config.name), 0)

    def test_serialize(self):
        @ConfRoot().config(self.location, dynamic=True)
        class AppConfig:
            name: str = field(default='abc', metadata={'serialize': lambda x: 'random_name',
                                                       'deserialize': lambda x: 'cde'})

        app_config = AppConfig()
        self.assertEqual(app_config.name, 'abc')
        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('random_name' in content)
        app_config.load()
        self.assertEqual(app_config.name, 'cde')

    def test_serialize_with_list(self):
        @ConfRoot().config(self.location, dynamic=True)
        class AppConfig:
            user_list: List = field(default_factory=list, metadata={
                'serialize': lambda xs: ','.join([x.lower() for x in xs]),
                'deserialize': lambda s: [x.upper() for x in s.split(',')]
            })

        app_config = AppConfig(['Tom', 'Jerry'])
        self.assertEqual(len(app_config.user_list), 2)
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertEqual(content.strip(), "user_list: ''")
        # 由于默认值的原因，必须使用一次save。
        app_config.save()
        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('tom,jerry' in content)
        app_config.load()
        self.assertEqual(app_config.user_list[0], 'TOM')
        self.assertEqual(app_config.user_list[1], 'JERRY')


if __name__ == '__main__':
    unittest.main()
