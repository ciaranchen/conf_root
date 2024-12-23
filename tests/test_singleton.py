import unittest

from conf_root import ConfRoot


class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        @ConfRoot(agent_class=None).config
        class AppConfig:
            one_thing: int = 42
            another_thing: int = 1024

        conf1 = AppConfig()
        conf2 = AppConfig()

        self.assertIs(conf1, conf2)


if __name__ == '__main__':
    unittest.main()
