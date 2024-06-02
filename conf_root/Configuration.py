import logging
import re
from abc import abstractmethod
from dataclasses import fields as dataclasses_fields, dataclass, is_dataclass, field as dataclass_field, Field
from typing import Any, List

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def is_config_class(cls_or_instance):
    return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None


@dataclass
class Configuration:
    name: str
    cls: Any
    conf_root: Any

    @property
    def filename(self):
        invalid_chars_pattern = r'[\\/:*?"<>|]'
        filename = re.sub(invalid_chars_pattern, '_', self.name)
        return filename

    @property
    def all_dataclass(self):
        def _recursive_dataclass(cls):
            if is_dataclass(cls):
                return sum([_recursive_dataclass(field.type) for field in dataclasses_fields(cls)], [cls])
            return []

        return _recursive_dataclass(self.cls)


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
