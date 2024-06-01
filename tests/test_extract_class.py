import os.path
import unittest
from dataclasses import field

from conf_root import ConfRoot
from conf_root.extract_class import extract_classes_from_file


def my_decorator(cls):
    return cls


@my_decorator
class DecoratedClass:
    pass


@ConfRoot().config()
class Class1:
    name: str = 'name1'


@ConfRoot().config
class Class2:
    name: str = 'name2'
    name2: Class1 = field(default_factory=Class1)


class TestExtractClass(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

        @ConfRoot.config
        class InnerClass:
            pass

    def tearDown(self):
        def remove_files(filename):
            if os.path.exists(filename):
                os.remove(filename)

        remove_files('Class1.yml')
        remove_files('Class2.yml')

    def test_extract_class(self):
        classes = extract_classes_from_file(__file__)
        # 注意：对于定义在类或函数中的配置类，无法import出来。
        self.assertEqual(len(classes), 2)
        classes.sort(key=lambda x: x.__name__)
        self.assertEqual(classes[0].__name__, 'Class1')
        self.assertEqual(classes[1].__name__, 'Class2')
        c1 = classes[0]()
        self.assertEqual(c1.name, 'name1')
        c2 = classes[1]()
        self.assertEqual(c2.name, 'name2')
