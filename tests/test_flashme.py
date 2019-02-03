import unittest

from flashme import FlashCard

class TestFlashMe(unittest.TestCase):

    def test_setup(self):
        self.assertEqual(3, 1 + 2)

    def test_flash_card(self):
        fc = FlashCard("the front", "the back")
        self.assertEqual(fc.front, "the front")
        self.assertEqual(fc.back, "the back")

