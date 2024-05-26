import logging
import re
from dataclasses import fields as dataclasses_fields, dataclass
from typing import Any

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def is_config_class(cls_or_instance):
    return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None


@dataclass
class Configuration:
    name: str
    cls: Any

    @property
    def filename(self):
        invalid_chars_pattern = r'[\\/:*?"<>|]'
        filename = re.sub(invalid_chars_pattern, '_', self.name)
        return filename

    @property
    def configuration_classes(self):
        def _recursive_config_class(cls):
            if is_config_class(cls):
                res = []
                for field in dataclasses_fields(cls):
                    res.extend(_recursive_config_class(field.type))
                    res.append(cls)
                return res
            else:
                return []

        return _recursive_config_class(self.cls)

    def yaml_register_classes(self):
        return self.configuration_classes
