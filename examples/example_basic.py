from conf_root import ConfRoot


# @ConfRoot().config(filename='config')
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
