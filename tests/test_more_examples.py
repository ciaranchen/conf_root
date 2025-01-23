import os.path
import unittest


class TestFields(unittest.TestCase):
    def test_example_nest_and_dynamic_save(self):
        from examples.example_nest_and_dynamic_save import AppConfig, app_config, DataBaseUserConfig
        filename = app_config.__CONF_LOCATION__
        default_db_config_name = DataBaseUserConfig.__qualname__.replace('.<locals>.', '.')

        # 显示嵌套的数据内容
        self.assertEqual(app_config.user_config.database_user, 'db_user')
        self.assertEqual(app_config.user_config.database_pass, 'db_pass')

        self.assertFalse(os.path.exists(f'{default_db_config_name}.yml'))
        self.assertTrue(os.path.exists(filename))

        # 重新加载文件后显示的是保存的结果
        app_config2 = AppConfig()
        self.assertEqual(app_config2.user_config.database_user, 'db_user')
        self.assertEqual(app_config2.user_config.database_pass, 'db_pass')

        # 清理实验中间产物
        os.remove(filename)

    def test_example_class_var(self):
        from examples.example_class_var import (DataBaseUserConfig, DataBaseUserConfig2, db_conf_root,
                                                old_filename, new_filename)
        DataBaseUserConfig()
        DataBaseUserConfig2()

        self.assertFalse(os.path.exists(old_filename))
        self.assertTrue(os.path.exists(new_filename))

        with open(new_filename, 'r') as f:
            content = f.read()
        self.assertIn(f'Custom_{db_conf_root.agent_class.class_name(DataBaseUserConfig)}', content)

        # 清理文件
        os.remove(new_filename)


if __name__ == '__main__':
    unittest.main()
