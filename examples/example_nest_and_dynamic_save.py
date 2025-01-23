"""
支持嵌套。
嵌套时可以只指定agent=None来避免产生存储的文件。
"""
from conf_root import ConfRoot, JsonAgent
from pydantic import BaseModel


@ConfRoot(agent_class=None).config
# 在这种情况下，会将先将类转换为dataclass，再转变为Pydantic Model。
class DataBaseUserConfig:
    database_user: str = 'admin'
    database_pass: str = 'default_password'


@ConfRoot(agent_class=JsonAgent).config(filename='config')
# 可通过agent_class指定配置文件格式
# 此时配置文件名为 `config.json`
class AppConfig(BaseModel):
    database_host: str = 'localhost'
    database_port: int = 5432
    # 可嵌套定义；如果基于dataclass进行修改的话，需通过default_factory 的方式创建
    user_config: DataBaseUserConfig = DataBaseUserConfig()


app_config = AppConfig()
# 允许动态修改内容，并保存到配置文件。
app_config.user_config.database_user = 'db_user'
app_config.user_config.database_pass = 'db_pass'
app_config.save_configuration()
