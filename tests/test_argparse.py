import argparse
import unittest

from conf_root import configuration
from conf_root.a2d import create_dataclass_from_argparse


class TestArgparse(unittest.TestCase):
    def test_create(self):
        parser = argparse.ArgumentParser(description="Example Argument Parser")
        parser.add_argument("--sum1", default=10, type=int, help="Number 1")
        parser.add_argument("--sum2", default=23, type=int)
        parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")

        ArgsClass = create_dataclass_from_argparse(parser)
        ArgsClass = configuration(ArgsClass)


        # 使用ArgsClass
        args_namespace = parser.parse_args()
        args_dataclass = ArgsClass(**vars(args_namespace))
        print(args_dataclass)

