import os
import unittest

from conf_root import ConfRoot, ChoiceField


class TestFields(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.location = 'settings.yml'

    def tearDown(self):
        if os.path.exists(self.location):
            os.remove(self.location)

    def test_choice_field(self):
        @ConfRoot().config(self.location)
        class ChoiceFieldTest:
            choice: str = ChoiceField(['A', 'B', 'C'])

        cft = ChoiceFieldTest()
        self.assertTrue(cft.choice, 'A')


if __name__ == '__main__':
    unittest.main()
