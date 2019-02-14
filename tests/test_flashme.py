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

    def test_get_next_card_simple(self):
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

    def test_get_next_card_with_timestamp(self):
        deck = Deck()
        expiries = [0, 1, 2, 3, 4, 100]
        deck.insert_card(FlashCard("q4", "a4", timestamp=2000), 1)
        deck.insert_card(FlashCard("q5", "a5", timestamp=1000), 1)
        deck.insert_card(FlashCard("q1", "a1", timestamp=9000), 0)
        deck.insert_card(FlashCard("q2", "a2", timestamp=8000), 0)
        deck.insert_card(FlashCard("q3", "a3", timestamp=7000), 0)
        deck.insert_card(FlashCard("q6", "a6", timestamp=10000), 2)

        deck.time_fun_impl = lambda: 1000
        import pudb; pudb.set_trace()
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
        self.assertEqual(5, card.box)
        self.assertEqual("q3", card.front)

    def test_card_expiry(self):
        deck = Deck()
        expiries = [0, 500, 1000, 5000, 8000, 10000]
        c0 = FlashCard("front", "back", box=0, timestamp=1000)
        self.assertTrue(deck.card_expired(c0, expiries=expiries, time_fun=lambda: 1000))
        c1 = FlashCard("front", "back", box=1, timestamp=1000)
        self.assertFalse(deck.card_expired(c1, expiries=expiries, time_fun=lambda: 1000 + 100))
        self.assertFalse(deck.card_expired(c1, expiries=expiries, time_fun=lambda: 1000 + 499))
        self.assertTrue(deck.card_expired(c1, expiries=expiries, time_fun=lambda: 1000 + 500))
        self.assertTrue(deck.card_expired(c1, expiries=expiries, time_fun=lambda: 1000 + 501))
        c2 = FlashCard("front", "back", box=2, timestamp=1000)
        self.assertFalse(deck.card_expired(c2, expiries=expiries, time_fun=lambda: 1000))
        self.assertFalse(deck.card_expired(c2, expiries=expiries, time_fun=lambda: 1000 + 100))
        self.assertFalse(deck.card_expired(c2, expiries=expiries, time_fun=lambda: 1000 + 999))
        self.assertTrue(deck.card_expired(c2, expiries=expiries, time_fun=lambda: 1000 + 1000))
        self.assertTrue(deck.card_expired(c2, expiries=expiries, time_fun=lambda: 1000 + 1001))
        c3 = FlashCard("front", "back", box=5, timestamp=1000)
        self.assertFalse(deck.card_expired(c3, expiries=expiries, time_fun=lambda: 1000))
        self.assertFalse(deck.card_expired(c3, expiries=expiries, time_fun=lambda: 1000 + 9999))
        self.assertTrue(deck.card_expired(c3, expiries=expiries, time_fun=lambda: 1000 + 10000))
        self.assertTrue(deck.card_expired(c3, expiries=expiries, time_fun=lambda: 1000 + 100000))
