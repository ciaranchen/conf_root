import re
from abc import abstractmethod
from dataclasses import fields as dataclasses_fields, dataclass, is_dataclass, field as dataclass_field, Field
from typing import Any, List


def is_config_class(cls_or_instance):
    return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None


class ConfigurationPreprocessField:
    @abstractmethod
    def field(self) -> Field:
        pass


@dataclass
class ChoiceField(ConfigurationPreprocessField):
    choices: List

    def field(self):
        return dataclass_field(default=self.choices[0],
                               metadata={'choices': self.choices, 'validators': [lambda x: x in self.choices]})
