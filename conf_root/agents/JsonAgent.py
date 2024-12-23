import json

from conf_root.agents.BasicAgent import BasicAgent
from conf_root.utils import data2obj, obj2data


class JsonAgent(BasicAgent):
    default_extension = '.json'

    def load(self, instance):
        super().load(instance)
        location = instance.__CONF_LOCATION__
        with open(location, encoding='utf-8') as file:
            data = json.load(file)
        # 将dict展开为对象。
        data2obj(instance, data, custom=True)
        return instance

    def save(self, instance):
        super().save(instance)
        location = instance.__CONF_LOCATION__
        data = obj2data(instance)
        with open(location, "w") as file:
            json.dump(data, file)
