import os.path
import unittest
import json
from typing import Dict


class TestFields(unittest.TestCase):
    def test_more_example1(self):
        from conf_root import ConfRoot, JsonAgent
        from dataclasses import field
        from typing import List

        @ConfRoot(agent_class=None).config
        class DataBaseUserConfig:
            database_user: str = 'admin'
            database_pass: str = 'default_password'

        @ConfRoot(agent_class=JsonAgent).config(name='config', dynamic=True)
        # 可通过agent_class指定配置文件格式
        # 此时配置文件名为 `config.json`
        class AppConfig:
            database_host: str = 'localhost'
            database_port: int = 5432
            # 可嵌套定义, 支持使用dataclasses的field。
            user_config: DataBaseUserConfig = field(default_factory=DataBaseUserConfig)
            # 使用 config_field，支持dataclasses.field 的所有参数；同时可以自定义serialize方式与deserialize方法
            user_list: List = field(default_factory=list, metadata={
                'serialize': lambda xs: ','.join([x.lower() for x in xs]),
                'deserialize': lambda s: [x.upper() for x in s.split(',')]
            })

        app_config = AppConfig()

        # 开始测试
        # 上面设置了dynamic以允许动态修改内容。
        app_config.user_list = ['Alice', 'Bob']
        app_config.user_config.database_user = 'db_user'
        app_config.user_config.database_pass = 'db_pass'
        app_config.save()

        filename = 'config.json'
        default_db_config_name = DataBaseUserConfig.__qualname__.replace('.<locals>.', '.')
        self.assertFalse(os.path.exists(f'{default_db_config_name}.yml'))
        self.assertFalse(os.path.exists(f'config.yml'))
        self.assertTrue(os.path.exists(filename))

        with open(filename) as f:
            data = json.load(f)
        self.assertEqual(data['user_list'], 'alice,bob')
        self.assertIsInstance(data['user_config'], Dict)
        self.assertEqual(data['user_config']['database_user'], 'db_user')
        self.assertEqual(data['user_config']['database_pass'], 'db_pass')

        app_config.load()
        self.assertEqual(app_config.user_list[0], 'ALICE')
        self.assertEqual(app_config.user_list[1], 'BOB')

        # 清理实验中间产物
        os.remove(filename)

    def test_more_example2(self):
        from conf_root import ConfRoot, SingleFileYamlAgent

        # 使用基于Ruamel.yaml的SingleFileYamlAgent是最推荐的做法。
        # 会将所有产生的config映射到同一个Yaml文件中。
        db_config = ConfRoot('config', agent_class=SingleFileYamlAgent)

        @db_config.config
        class DataBaseUserConfig:
            database_user: str = 'user1'
            database_password: str = 'password1'

        @db_config.config
        class DataBaseUserConfig2:
            database_user: str = 'user2'
            database_password: str = 'password2'

        # 如需在类的定义外，可以在初始化配置类前修改加载文件的路径
        db_config.path = 'config_backup'
        db_config.agent = db_config.agent_class('config_backup')

        # 开始测试
        user1 = DataBaseUserConfig()
        user2 = DataBaseUserConfig2()

        old_filename = 'config.yml'
        new_filename = 'config_backup.yml'
        self.assertFalse(os.path.exists(old_filename))
        self.assertTrue(os.path.exists(new_filename))

        # 清理文件
        os.remove(new_filename)


if __name__ == '__main__':
    unittest.main()
