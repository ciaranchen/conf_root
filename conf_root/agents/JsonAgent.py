import json

from conf_root.agents.BasicAgent import BasicAgent


class JsonAgent(BasicAgent):
    default_extension = '.json'

    def load(self, cls):
        super().load(cls)
        location = cls.__CONF_LOCATION__
        with open(location, encoding='utf-8') as file:
            data = json.load(file)
        return data

    def save(self, instance):
        super().save(instance)
        location = instance.__CONF_LOCATION__
        with open(location, "w") as file:
            file.write(instance.model_dump_json())
