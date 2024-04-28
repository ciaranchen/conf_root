# Conf Root

![PyPI - Version](https://img.shields.io/pypi/v/conf_root)

基于dataclass的符合逻辑的配置文件取用方式。主要功能如下：

1. 封装dataclass到配置文件。
2. 将argparse的设置转换为配置文件。这在改动一些科研项目的代码时很有用。

## 封装dataclass

```python
from conf_root import configuration, YamlAgent
from dataclasses import dataclass


# @configuration
# 这个装饰器也支持上面这种简写方式
@configuration('config.yaml', agent=YamlAgent)
@dataclass
class AppConfig:
    database_host: str = 'localhost'
    database_port: int = 5432


# 检测是否存在配置文件(默认文件名: `config.yaml`) ，如果不存在则按照默认值新建文件。
# 如存在配置文件，则加载文件中的配置。
app_config = AppConfig()
# 对 app_config 内容改动后，可通过以下方式写入配置文件
app_config.save()
# 对 配置文件 内容改动后，可通过以下方式加载配置文件
app_config.load()
```

> note: dataclass 中的字段需指定类型。

## 解析 Argparse

```python
import argparse
from conf_root import configuration, ArgparseConfiguration

# 科研项目经常出现一大堆parser.argument
parser = argparse.ArgumentParser()
parser.add_argument("--dataSet", type=str, default="wiki", help="cora, citeseer, wiki, corafull, FedDBLP")
# ...
parser.add_argument("--dropout", type=float, default=0.5)
args = parser.parse_args()

# 使用以下代码解析Argparse并转换为支持conf_root的dataclass。
arg_config = ArgparseConfiguration.from_argparse(parser)
ArgsClass = configuration(arg_config.dataclass)

# 之后可以使用以下代码，创建并使用配置文件。
# 大部分科研项目的情况下，使用下面就可以了
args_dataclass = ArgsClass(**vars(args))
# 如果parser中包含不支持的参数，使用下面的方法过滤
args_dataclass2 = ArgsClass(**arg_config.filter_unsupported(args))
```

## More Example

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
