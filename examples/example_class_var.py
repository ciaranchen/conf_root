from conf_root import ConfRoot, SingleFileYamlAgent

# 使用基于Ruamel.yaml的SingleFileYamlAgent是最推荐的做法。
# 会将所有产生的config映射到同一个Yaml文件中。
db_conf_root = ConfRoot(agent_class=SingleFileYamlAgent)
old_filename = 'config.yml'


@db_conf_root.config('config.yml')
class DataBaseUserConfig:
    database_user: str = 'user1'
    database_password: str = 'password1'


@db_conf_root.config('config.yml')
class DataBaseUserConfig2:
    database_user: str = 'user2'
    database_password: str = 'password2'


# 如需在类的定义外，可以在初始化配置类前修改加载文件的路径
new_filename = 'config_backup.yml'
DataBaseUserConfig.__CONF_LOCATION__ = new_filename
DataBaseUserConfig2.__CONF_LOCATION__ = new_filename


# 通过重载__CONF_AGENT__中的class_name可以改变类在yml存储中的名称。
class RenameAgent(db_conf_root.agent_class):
    @staticmethod
    def class_name(cls):
        return f'Custom_{cls.__CONF_ROOT__.agent_class.class_name(cls)}'


DataBaseUserConfig.__CONF_AGENT__ = RenameAgent()
