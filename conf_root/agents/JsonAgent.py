import json

from conf_root.agents.BasicAgent import MultiFileAgent
from conf_root.utils import data2obj, obj2data


class JsonAgent(MultiFileAgent):
    default_extension = '.json'

    def load(self, location, instance):
        super().load(location, instance)
        with open(location, encoding='utf-8') as file:
            data = json.load(file)
        # 将dict展开为对象。
        data2obj(instance, data, custom=True)
        return instance

    def save(self, location, instance):
        super().save(location, instance)
        data = obj2data(instance)
        with open(location, "w") as file:
            json.dump(data, file)
