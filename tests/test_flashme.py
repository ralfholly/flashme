import unittest

from flashme import FlashCard, Deck

# pylint:disable=no-self-use
class TestFlashMe(unittest.TestCase):

    def test_setup(self):
        self.assertEqual(3, 1 + 2)

    def test_flash_card(self):
        fc = FlashCard("the front", "the back")
        self.assertEqual(fc.front, "the front")
        self.assertEqual(fc.back, "the back")

    def test_get_next_card(self):
        deck = Deck()
        deck.insert_card(FlashCard("q4", "a4"), 1)
        deck.insert_card(FlashCard("q5", "a5"), 1)
        deck.insert_card(FlashCard("q1", "a1"), 0)
        deck.insert_card(FlashCard("q2", "a2"), 0)
        deck.insert_card(FlashCard("q3", "a3"), 0)
        deck.insert_card(FlashCard("q6", "a6"), 2)
        self.assertEqual("q1", deck.get_next_card().front)
        self.assertEqual("q2", deck.get_next_card().front)
        self.assertEqual("q3", deck.get_next_card().front)
        self.assertEqual("q4", deck.get_next_card().front)
        self.assertEqual("q5", deck.get_next_card().front)
        self.assertEqual("q6", deck.get_next_card().front)
        self.assertEqual(None, deck.get_next_card())

    def test_wrong(self):
        deck = Deck()
        deck.insert_card(FlashCard("q3", "a3"), 3)
        card = deck.get_next_card()
        self.assertEqual(3, card.box)
        deck.wrong(card)
        self.assertEqual(0, card.box)
        deck.restart()
        card = deck.get_next_card()
        self.assertEqual(0, card.box)
        self.assertEqual("q3", card.front)

    def test_right(self):
        deck = Deck()
        deck.insert_card(FlashCard("q3", "a3"), 3)
        card = deck.get_next_card()
        self.assertEqual(3, card.box)
        deck.right(card)
        card = deck.get_next_card()
        self.assertEqual(4, card.box)
        self.assertEqual("q3", card.front)
        # Cannot promote card beyond last box.
        deck.right(card)
        self.assertEqual(4, card.box)
        self.assertEqual("q3", card.front)
