import json

from conf_root.agents.BasicAgent import BasicAgent, MultiFileAgent
from conf_root.utils import data2obj, obj2data


class JsonAgent(BasicAgent, MultiFileAgent):
    default_extension = '.json'

    def load(self, configuration, instance):
        super().load(configuration, instance)
        location = self.get_configuration_location(configuration)
        with open(location, encoding='utf-8') as file:
            data = json.load(file)
        # 将dict展开为对象。
        data2obj(instance, data, custom=True)
        return instance

    def save(self, configuration, instance):
        super().save(configuration, instance)
        data = obj2data(instance)
        location = self.get_configuration_location(configuration)
        with open(location, "w") as file:
            json.dump(data, file)
