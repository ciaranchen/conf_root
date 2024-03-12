# Conf Root

![PyPI - Version](https://img.shields.io/pypi/v/conf_root)

基于dataclass的符合逻辑的配置取用方式。

## 使用方法

```python
from conf_root import configuration
from dataclasses import dataclass


@configuration
@dataclass
class AppConfig:
    database_host: str = 'localhost'
    database_port: int = 5432
    database_user: str = 'admin'
    database_password: str = 'default_password'


app_config = AppConfig()
```

## 流程说明

1. 检测是否存在配置文件(默认文件名: `config.yaml`) ，如果不存在则按照默认值新建文件。
2. 如存在配置文件，则加载文件中的配置。
3. 提供存储和加载的接口，可供动态改动。

```python
app_config.save()
app_config.load()
```

> note: dataclass 中的字段需指定类型。

## Example

```python
from conf_root import configuration, JsonAgent
from dataclasses import dataclass, field


@dataclass
class DataBaseUserConfig:
    database_user: str = 'admin'
    database_password: str = 'default_password'


@configuration(agent=JsonAgent)
# 可通过agent_class指定配置文件格式
# 此时默认配置文件名为 `config.json`
@dataclass
class AppConfig:
    database_host: str = 'localhost'
    database_port: int = 5432
    # 可嵌套dataclass定义
    user_config: DataBaseUserConfig = field(default_factory=DataBaseUserConfig)


app_config = AppConfig()
```
