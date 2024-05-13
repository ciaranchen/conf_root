# Conf Root

![PyPI - Version](https://img.shields.io/pypi/v/conf_root)

基于dataclass的符合逻辑的配置文件取用方式。主要功能如下：

1. 封装dataclass到配置文件。
2. 将argparse的设置转换为配置文件。这允许在科研项目的代码中能快速地通过配置文件运行代码。

> Note: 仅用于配置文件，因此不提倡在配置文件类中使用动态的变量。

## 封装dataclass

```python
from conf_root import ConfRoot
from dataclasses import dataclass


# @ConfRoot().wrap(name='config')
# @ConfRoot().wrap
# 这个装饰器也支持上面这两种调用方式
@ConfRoot().wrap('config')
@dataclass
class AppConfig:
    database_host: str = 'localhost'
    database_port: int = 5432


# 检测是否存在配置文件(文件名为name+后缀)(如果未传入name参数，文件名为 `{cls.__qual_name__}.yml`) ，如果不存在则按照默认值新建文件。
# 如存在配置文件，则加载文件中的配置。
app_config = AppConfig()
# 对 app_config 内容改动后，可通过以下方式写入配置文件
app_config.save()
# 对 配置文件 内容改动后，可通过以下方式加载配置文件
app_config.load()
```

> note: dataclass 中的字段需指定类型。如果不指定类型，将被视为类变量而不会被解析为dataclass中的字段。这个库在dataclass的基础上进行解析，将无法直接处理类变量。

### 参数解释

#### `ConfRoot(path = None, agent: Optional[Type[BasicAgent]] = YamlAgent)`

- path 为基本路径。当它为None时，将会设置为当前文件路径。
- agent 为配置存储的形式。当前支持JsonAgent/YamlAgent/RuamelAgent。默认为YamlAgent。
    - 对于存储到多个文件的agent（JsonAgent、YamlAgent），path是配置存储的文件夹路径。
    - 对于存储到单个文件的agent（RuamelAgent），path是配置存储的文件路径。
    - 如果指定为None，可以不产生配置文件存储；同时也不会为类添加save与load方法。
    - 可以继承BasicAgent进行拓展以适配更多类型的序列化方式。

#### `ConfRoot.wrap`

可以使用不同方式调用。详见上方示例。

- name。该配置在path中的位置。
    - 对于多文件存储，name为文件名。指定时可以带上agent相应的后缀名。
    - 对于单文件存储，name为在文件中的section名。

## 解析 Argparse

在科研项目中会出现一大堆parser.argument，我希望能将它们转换为配置文件，而不是每次都要记录运行时的命令行参数。

```python
import argparse
from conf_root import ConfRoot

# 科研项目经常出现一大堆parser.argument
parser = argparse.ArgumentParser()
parser.add_argument("--dataSet", type=str, default="wiki", help="cora, citeseer, wiki, corafull, FedDBLP")
# ...
parser.add_argument("--dropout", type=float, default=0.5)
args = parser.parse_args()

# 解析Argparse并转换为dataclass，并且用ConfRoot.wrap封装它
# cls_name 的默认值为 'argparse'
ArgsClass = ConfRoot().from_argparse(parser, cls_name='argparse')

# 之后可以使用以下代码，创建并使用配置文件。
# 大部分科研项目的情况下，使用下面就可以了
args_dataclass = ArgsClass(**vars(args))
```

### 参数解释

#### `ConfRoot.from_argparse(parser: argparse.ArgumentParser, cls_name: str = 'argparse')`

解析Argparse并转换为dataclass，并且用ConfRoot.wrap封装它

- paser。需解析的argparse.ArgumentParser。
- cls_name。这个参数既是产生的dataclass类的类名，也是使用ConfRoot.wrap封装时的name参数。默认值为argparse。

from_argparse 目前仅支持常见的Argparse动作。这不意味着有不支持的命令行参数会导致报错，这些参数将会被忽略跳过。具体限制如下：

1. Argparse 的 action 必须为 'store(即默认值)', 'store_const', 'store_true', 'store_false' 之一。
2. Argparse 的 nargs 不支持。
3. Argparse 中 choices 和 required 的限制将会被忽略。

## More Example

支持嵌套。
嵌套时可以只指定agent=None来避免产生存储的文件。

```python
from conf_root import ConfRoot, JsonAgent
from dataclasses import dataclass, field


@ConfRoot(agent=None).wrap
@dataclass
class DataBaseUserConfig:
    database_user: str = 'admin'
    database_password: str = 'default_password'


@ConfRoot(agent=JsonAgent).wrap
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
