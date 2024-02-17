# Conf Root

基于dataclass的符合逻辑的配置取用方式。

## 使用方法

```python
from conf_root.conf_root import configuration as configuration_at
from dataclasses import dataclass


@configuration_at('settings.yaml')
@dataclass
class AppConfig:
    database_host: str = 'localhost'
    database_port: int = 5432
    database_user: str = 'admin'
    database_password: str = 'default_password'


app_config = AppConfig()
```

## 解释说明

1. 检测是否存在 `settings.yaml`，如果不存在则按照默认值新建文件。
2. 如存在 `settings.yaml`，则加载文件中的配置。
3. 提供存储和加载的接口，可供动态改动。

```python
app_config.save()
app_config.load()
```

> note: dataclass 中的字段需指定类型。
