import logging
import re
from dataclasses import fields as dataclasses_fields, dataclass, is_dataclass
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
    conf_root: Any

    @property
    def filename(self):
        invalid_chars_pattern = r'[\\/:*?"<>|]'
        filename = re.sub(invalid_chars_pattern, '_', self.name)
        return filename

    @property
    def all_dataclass(self):
        def _recursive_dataclass(cls):
            res = []
            if is_dataclass(cls):
                for field in dataclasses_fields(cls):
                    res.extend(_recursive_dataclass(field.type))
                res.append(cls)
            return res

        return _recursive_dataclass(self.cls)
