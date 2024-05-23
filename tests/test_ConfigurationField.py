import os
import unittest

from conf_root import ConfRoot, config_field


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
        @ConfRoot(agent_class=None).wrap
        class AppConfig:
            name: list = config_field(default_factory=list)

        app_config = AppConfig()
        self.assertTrue(isinstance(app_config.name, list))
        self.assertEqual(len(app_config.name), 0)

    def test_serialize(self):
        @ConfRoot().wrap(self.location, dynamic=True)
        class AppConfig:
            name: str = config_field(default='abc', serialize=lambda x: 'random_name',
                                     deserialize=lambda x: 'cde')

        app_config = AppConfig()
        self.assertEqual(app_config.name, 'abc')
        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('random_name' in content)
        app_config.load()
        self.assertEqual(app_config.name, 'cde')


if __name__ == '__main__':
    unittest.main()
