from agents.BasicAgent import BasicAgent
import yaml


class YamlAgent(BasicAgent):
    def create(self, cls):
        # 将dataclass默认值转换为dict，便于序列化
        default_dict = self.dataclass_default_dict(cls)

        # 将dict转换为YAML并写入文件
        with open(self.location, "w") as yaml_file:
            yaml.dump(default_dict, yaml_file)

    def load(self, cls, obj):
        with open(self.location, encoding='utf-8') as yaml_file:
            data = yaml.safe_load(yaml_file)

        # 将dict展开为对象。
        self.dict_to_dataclass(data, cls, obj)

    def save(self, obj):
        pass
