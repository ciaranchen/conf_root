import os
import unittest
from dataclasses import dataclass, field

from conf_root import configuration


@dataclass
class NestedConfig:
    config1: str = 'config1'
    config2: str = 'config2'


@dataclass
class AppConfig:
    nc_defined: NestedConfig
    # note：should use default_factory
    nc_default: NestedConfig = field(default_factory=NestedConfig)


class TestConfig(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.location = 'nested_config.yaml'

    def tearDown(self):
        # 这个方法将在每个测试方法结束后运行
        # 使用os.remove删除在测试中创建的文件
        try:
            os.remove(self.location)
        except FileNotFoundError:
            pass  # 如果文件不存在，忽略错误（也可以根据需求抛出异常）

    def test_create(self):
        DecoratedConfig = configuration(self.location)(AppConfig)

        app_config = DecoratedConfig(NestedConfig(config1='defined1', config2='defined2'))
        self.assertEqual(app_config.nc_default.config1, 'config1')
        self.assertEqual(app_config.nc_default.config2, 'config2')

        self.assertEqual(app_config.nc_defined.config1, 'defined1')
        self.assertEqual(app_config.nc_defined.config2, 'defined2')

        # 外部修改配置文件后读取，结果应为配置文件内的设置。
        # 打开文件，读取内容
        self.assertTrue(os.path.exists(self.location))
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('config1' in content)
        self.assertTrue('config2' in content)
        # defined 因为非默认配置，不在配置文件中。
        self.assertFalse('defined1' in content)
        self.assertFalse('defined2' in content)

        os.remove(self.location)

    def test_load(self):
        content = """nc_default:
    config1: default_load1
nc_defined:
    config1: load1
    config2: load2"""

        # 将处理后的内容写回文件（可以先备份原文件）
        with open(self.location, 'w') as file:
            file.write(content)

        DecoratedConfig = configuration(self.location)(AppConfig)
        app_config = DecoratedConfig(NestedConfig(config1='defined1', config2='defined2'))
        self.assertEqual(app_config.nc_default.config1, 'default_load1')
        self.assertEqual(app_config.nc_default.config2, 'config2')

        self.assertEqual(app_config.nc_defined.config1, 'load1')
        self.assertEqual(app_config.nc_defined.config2, 'load2')

        os.remove(self.location)

    def test_save(self):
        DecoratedConfig = configuration(self.location)(AppConfig)
        app_config = DecoratedConfig(NestedConfig(config1='defined1', config2='defined2'))
        app_config.nc_default.config1 = 'save_default'
        app_config.nc_defined.config1 = 'save_defined'
        app_config.save()

        # 外部修改配置文件后读取，结果应为配置文件内的设置。
        # 打开文件，读取内容
        with open(self.location, 'r') as file:
            content = file.read()
        self.assertTrue('save_default' in content)
        self.assertTrue('save_defined' in content)
