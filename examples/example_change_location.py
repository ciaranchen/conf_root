from conf_root import ConfRoot, SingleFileYamlAgent

# 使用基于Ruamel.yaml的SingleFileYamlAgent是最推荐的做法。
# 会将所有产生的config映射到同一个Yaml文件中。
db_config = ConfRoot(agent_class=SingleFileYamlAgent)


@db_config.config('config')
class DataBaseUserConfig:
    database_user: str = 'user1'
    database_password: str = 'password1'


@db_config.config('config')
class DataBaseUserConfig2:
    database_user: str = 'user2'
    database_password: str = 'password2'


# 如需在类的定义外，可以在初始化配置类前修改加载文件的路径
DataBaseUserConfig.__CONF_LOCATION__ = 'config_backup'
DataBaseUserConfig2.__CONF_LOCATION__ = 'config_backup'
