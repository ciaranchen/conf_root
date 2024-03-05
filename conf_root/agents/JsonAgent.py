from conf_root.agents.BasicAgent import BasicAgent
import json


class JsonAgent(BasicAgent):
    default_extension = 'json'

    def create(self, cls):
        # 将dataclass默认值转换为dict，便于序列化
        default_dict = self.dataclass_default_dict(cls)

        # 将dict转换为YAML并写入文件
        with open(self.location, "w") as file:
            json.dump(default_dict, file)

    def load(self, cls, obj):
        with open(self.location, encoding='utf-8') as file:
            data = json.load(file)

        # 将dict展开为对象。
        self.dict_to_dataclass(data, cls, obj)

    def save(self, obj):
        data_dict = self.dataclass_to_dict(obj)

        # 将dict转换为YAML并写入文件
        with open(self.location, "w") as file:
            json.dump(data_dict, file)
