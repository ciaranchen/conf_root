from dataclasses import dataclass, fields, MISSING, is_dataclass


@dataclass
class BasicAgent:
    """
    类中的函数主要是处理递归问题。
    """
    location: str
    default_extension: str = 'undefined'

    @staticmethod
    def dataclass_default_dict(cls):
        """
        注意这种做法只适用于dataclass，而且必须要带类型注解。
        """
        res = {}
        for field in fields(cls):
            if field.default is not MISSING:
                if is_dataclass(field.type):
                    res[field.name] = BasicAgent.dataclass_default_dict(field.default)
                else:
                    res[field.name] = field.default
            if field.default_factory is not MISSING:
                if is_dataclass(field.type):
                    res[field.name] = BasicAgent.dataclass_default_dict(field.default_factory)
                else:
                    res[field.name] = field.default_factory
        return res

    @staticmethod
    def dict_to_dataclass(data, cls, obj):
        field_types = {f.name: f.type for f in fields(cls)}
        for k, v in data.items():
            # 如果给出了类型，则将读取的数据转换为原类型。
            if k in field_types:
                if is_dataclass(value_type := field_types[k]):
                    if hasattr(obj, k):
                        sub_object = getattr(obj, k)
                        BasicAgent.dict_to_dataclass(v, value_type, sub_object)
                    else:
                        # 创建一个新的对象。
                        sub_object = BasicAgent.build_sub_object(v, value_type)
                    v = sub_object
                else:
                    v = value_type(v)
            setattr(obj, k, v)

    @staticmethod
    def build_sub_object(data, cls):
        # 深度优先地遍历
        # 首先处理类型需要修改的内容
        field_types = {f.name: f.type for f in fields(cls)}
        res = {}
        for k, v in data.items():
            if k in field_types:
                if is_dataclass(value_type := field_types[k]):
                    res[k] = BasicAgent.build_sub_object(v, value_type)
                else:
                    res[k] = value_type(v)

        final_obj = cls(**res, **{k: v for k, v in data.items() if k not in field_types})
        # 这里可能 raise TypeError: missing required positional argument
        # 认为应该不作处理，让它报错。
        return final_obj

    @staticmethod
    def dataclass_to_dict(obj):
        """
        需避开_agent的预留值
        :param obj:
        :return:
        """
        res = {}
        for k, v in obj.__dict__.items():
            if k == '_agent':
                continue
            if is_dataclass(v):
                res[k] = BasicAgent.dataclass_to_dict(v)
            else:
                res[k] = v
        return res
