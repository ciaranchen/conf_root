# Conf Root

![PyPI - Version](https://img.shields.io/pypi/v/conf_root)

基于dataclass的科研配置文件取用工具。主要想法是在大量进行实验时，参数经常变动而且难以记录。最好有一种方式能在人类能读懂的配置文件中写出所有的参数，这样每次运行的记录都相对完整且易于整理。库的主要功能如下：

1. 为您定义的类生成一个配置文件；并优先使用配置文件中的值作为类中变量的值。
2. 将某些科研项目中的argparse转换为dataclass，进而生成配置文件；从而可以在配置文件中修改输入。
3. 提供脚本 `conf-root-web`。提供一个web界面，允许您可视化修改类定义的配置文件。

> Note: 仅用于配置文件，不提倡在配置文件类中使用动态的变量。

## 装饰类的定义生成配置文件

项目使用dataclass对配置类进行封装，并产生配置文件。

> note: 类定义的字段需要类型注解。如果不指定字段类型，将被视为类变量而不会被解析为dataclass中的字段，也无法被这个类进行解析。

下面是一个对`AppConfig`进行封装

```python
from conf_root import ConfRoot


# @ConfRoot().config(name='config')
# @ConfRoot().config
# 这个装饰器也支持上面这两种调用方式
@ConfRoot().config('config')
class AppConfig:
    database_host: str = 'localhost'
    database_port: int = 5432


# 在类实例化时，检测是否存在配置文件(文件名为name+后缀)。
# 如不存在则新建文件。
# 如存在配置文件，则加载文件中的配置。
app_config = AppConfig()
```

### 参数解释

#### ConfRoot(path = None, agent_class: Optional[Type[BasicAgent]] = YamlAgent)

- path 为基本路径。当它为None时，将会设置为当前文件路径。
- agent_class 为配置存储的形式。当前支持JsonAgent/YamlAgent/SingleFileYamlAgent。默认为YamlAgent。
    - 对于存储到多个文件的agent（JsonAgent、YamlAgent），path是配置存储的文件夹路径。
    - 对于存储到单个文件的agent（SingleFileYamlAgent），path是配置存储的文件路径。
    - 如果指定为None，可以不产生配置文件存储；同时也不会为类添加save与load方法。
    - 可以继承BasicAgent进行拓展以适配更多类型的序列化方式。

#### ConfRoot.config

可以使用不同方式调用。详见上方示例。

- name。该配置在path中的位置。默认为 `{cls.__qual_name__}`。
    - 对于多文件存储，name为文件名。指定时可以带上agent相应的后缀名。
    - 对于单文件存储，name为在文件中的section名。
- dynamic 为是否允许动态加载与变更配置文件。默认为False。如果设定为True，将会为类添加`save` 和 `load`方法来动态写入或读取配置文件。

### 对field的拓展说明

dataclass中的field可以通过metadata进行拓展。

- comment: 注释。仅在Yaml的输出格式中有效。为导出文件中当前字段的行添加行内注释。
- serialize: 自定义序列化函数。接受序列化字段的值，返回序列化的文本。
- deserialize: 自定义反序列化函数。接受序列化后的文本，返回该字段应有的值。
- validators: 函数的列表。在反序列化时，对获得的值依次校验；如不符合要求抛出 ValidateException.

## 解析 Argparse

在科研项目中会出现一大堆parser.argument，仅需添加两行代码就可以将其命令行参数配置转换为配置文件，并在配置文件中剪辑参数。不必重复输入一长串的命令行参数，也不再需要专门的`run.sh`
或者`run.bat`。

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

#### ConfRoot.from_argparse(parser: argparse.ArgumentParser, cls_name: str = 'argparse')

解析Argparse并转换为dataclass，并且用ConfRoot.wrap封装它

- paser。需解析的argparse.ArgumentParser。
- cls_name。这个参数既是产生的dataclass类的类名，也是使用ConfRoot.wrap封装时的name参数。默认值为argparse。

from_argparse 目前仅支持常见的官方Argparse动作，但是对于自定义的Action来说可能支持有限。这不意味着有不支持的命令行参数会导致报错，这些参数将会被忽略跳过。

## Web界面可视化修改配置文件

### 命令行使用方法

```shell
conf-root-web [-h] [--host HOST] [--port PORT] filename
```

这个脚本允许您在一个网页中可视化地修改您的配置文件。它能读取配置文件中暴露的ConfRoot配置类，并且生成一个可视化修改

- filename 提取配置类的Python文件名
- HOST 服务器的host，默认为 127.0.0.1
- PORT 服务器的port，默认为 8080

### 代码中的使用方法

```python
from conf_root import ConfRoot


@ConfRoot().config('config')
class AppConfig:
    database_host: str = 'localhost'
    database_port: int = 5432


ConfRoot.serve([AppConfig], host='0.0.0.0', port=8000)
```

#### ConfRoot.serve(classes, host='127.0.0.1', port=8080)

- classes 需要展示的配置类列表。
- HOST 服务器的host，默认为 127.0.0.1
- PORT 服务器的port，默认为 8080

## More Example

支持嵌套。
嵌套时可以只指定agent=None来避免产生存储的文件。

```python
from conf_root import ConfRoot, JsonAgent
from dataclasses import field
from typing import List


@ConfRoot(agent_class=None).config
class DataBaseUserConfig:
    database_user: str = 'admin'
    database_password: str = 'default_password'


@ConfRoot(agent_class=JsonAgent).config
# 可通过agent_class指定配置文件格式
# 此时默认配置文件名为 `config.json`
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
```
