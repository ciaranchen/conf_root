"""
支持嵌套。
嵌套时可以只指定agent=None来避免产生存储的文件。
"""
from conf_root import ConfRoot, JsonAgent
from dataclasses import field
from typing import List


@ConfRoot(agent_class=None).config
class DataBaseUserConfig:
    database_user: str = 'admin'
    database_pass: str = 'default_password'


@ConfRoot(agent_class=JsonAgent).config(filename='config')
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
