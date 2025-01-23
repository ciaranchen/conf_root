# Conf Root

![PyPI - Version](https://img.shields.io/pypi/v/conf_root)

基于Pydantic的科研配置文件取用工具。主要想法是在大量进行实验时，参数经常变动而且难以记录。最好有一种方式能在人类能读懂的配置文件中写出所有的参数，这样每次运行的记录都相对完整且易于整理。库的主要功能如下：

1. 将您定义的类转化为Pydantic Model，并生成配置文件，可以选择使用配置文件优先或输入参数优先地作为类变量的值。
2. 将某些科研项目中的argparse转换为Pydantic Model，进而生成配置文件；从而可以在配置文件中修改输入。

> Note: 仅用于配置文件，不提倡在配置文件类中使用动态的变量和方法。

## 装饰类的定义生成配置文件

项目使用Pydantic Model对配置类进行封装，并产生配置文件。

> note: 类定义的字段需要类型注解。请参阅 pydantic 的文档。

下面是一个对`AppConfig`进行封装

```python
from conf_root import ConfRoot
from pydantic import BaseModel


# @ConfRoot().config(filename='config')
# @ConfRoot().config
# 这个装饰器也支持上面这两种调用方式
@ConfRoot().config('config')
class AppConfig(BaseModel):
    database_host: str = 'localhost'
    database_port: int = 5432


# 在类实例化时，检测是否存在配置文件(文件名为name+后缀)。
# 如不存在则新建文件。
# 如存在配置文件，则加载文件中的配置。
app_config = AppConfig()
```

### 参数解释

#### ConfRoot.__init__(agent_class: Optional[Type[BasicAgent]] = YamlAgent, priority: Literal['file', 'param'] = 'file')

- agent_class 为配置存储的形式。当前支持JsonAgent/YamlAgent/SingleFileYamlAgent。
    - 对于存储到多个文件的agent（JsonAgent、YamlAgent）。存储到由参数指定的路径中，将覆盖原有结果。
    - 对于存储到单个文件的agent（SingleFileYamlAgent）。存储到由参数指定的同一路径中时，将根据类的名称存取其中的数据。
    - 如果指定为None，可以不产生配置文件存储。
    - 可以自行对BasicAgent进行拓展以适配更多类型的序列化方式。
- priority 为加载时的优先级模式。在加载时将同时考虑配置文件和类的初始化参数。默认为`file`，即以配置文件中的值优先加载到类中。`param`即以输入的值为优先加载到类中。

#### ConfRoot.config

可以使用不同方式调用。详见上方示例，其主要参数为 `filename`；支持不同的调用方式。

- filename。保存的文件名。默认时为根据 `{cls.__qualname__}` 产生的文件名。

config 函数将为原类型添加特殊的类变量，这允许动态地修改配置类的读写行为，实现如保存到另一个路径等功能，详情请参考 `examples/` 中的示例。

- `__CONF_LOCATION__`: 用于修改配置文件的路径。
- `__CONF_AGENT__`: 用于修改Agent对象。
    - `class_name`: 返回在（Yaml）配置文件中类的名称。
- `__CONF_ROOT__`: 用于修改ConfRoot对象。

config 还会在原类型的基础上添加 `save_configuration` 方法，方便直接写入配置文件。

对于无法序列化的 `type` 和 `function` 类型，将会给出警告并跳过而不会直接报错。

嵌套，自定义序列化，自定义验证器作为pydantic功能的一部分，可以参见[pydantic的文档](https://docs.pydantic.dev/latest/concepts/models/)。

## 解析 Argparse

在科研项目中会出现一大堆parser.argument，仅需添加两行代码就可以将其命令行参数配置转换为配置文件，并在配置文件中剪辑参数。
这样保存和切换不同的配置文件即可运行不同的版本。 不必重复输入一长串的命令行参数，也不再需要专门的`run.sh`或者`run.bat`。

```python
import argparse
from conf_root import ConfRoot

# 科研项目经常出现一大堆parser.argument
parser = argparse.ArgumentParser()
parser.add_argument("--dataSet", type=str, default="wiki", help="cora, citeseer, wiki, corafull, FedDBLP")
# ...
parser.add_argument("--dropout", type=float, default=0.5)
args = parser.parse_args()

# 解析Argparse并转换为pydantic Model，并且用ConfRoot.config封装它
# cls_name 的默认值为 'argparse'
ArgsClass = ConfRoot().from_argparse(parser, cls_name='argparse')

# 之后可以使用以下代码，创建并使用配置文件。
args_model = ArgsClass(**vars(args))
```

### 参数解释

#### ConfRoot.from_argparse(parser: argparse.ArgumentParser, cls_name: str = 'ArgparseConfig', *args, **kwargs)

解析Argparse并转换为pydantic Model，并且用ConfRoot.config封装它

- paser。需解析的argparse.ArgumentParser。
- cls_name。产生的Model类的类名。默认值为ArgparseConfig。
- *args, **kwargs。其余参数将被作为ConfRoot.config 的

from_argparse 目前仅支持常见的官方Argparse动作，但是对于自定义的Action无法做到转换。这不意味着有不支持的命令行参数会导致报错，这些参数将会被忽略跳过。

## More Example

参见 `examples/*`。
