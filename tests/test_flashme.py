import unittest

from flashcard import FlashCard
from flashme import Deck

# pylint:disable=no-self-use
# pylint:disable=invalid-name

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
        self.assertEqual("q1", deck.get_next_card(consume=True).front)
        self.assertEqual("q2", deck.get_next_card(consume=True).front)
        self.assertEqual("q3", deck.get_next_card(consume=True).front)
        self.assertEqual("q4", deck.get_next_card(consume=True).front)
        self.assertEqual("q5", deck.get_next_card(consume=True).front)
        self.assertEqual("q6", deck.get_next_card(consume=True).front)
        self.assertEqual(None, deck.get_next_card(consume=True))

    def test_get_next_card_with_timestamp(self):
        expiries = [0, 1, 2, 3, 4, 100]
        deck = Deck(expiries)
        deck.insert_card(FlashCard("q4", "a4", timestamp=2000), 1)
        deck.insert_card(FlashCard("q5", "a5", timestamp=1000), 1)
        deck.insert_card(FlashCard("q1", "a1", timestamp=9000), 0)
        deck.insert_card(FlashCard("q2", "a2", timestamp=8000), 0)
        deck.insert_card(FlashCard("q3", "a3", timestamp=7000), 0)
        deck.insert_card(FlashCard("q6", "a6", timestamp=10000), 2)
        deck.time_fun = lambda: 8001
        self.assertEqual("q2", deck.get_next_card(consume=True).front)
        self.assertEqual("q3", deck.get_next_card(consume=True).front)
        self.assertEqual("q4", deck.get_next_card(consume=True).front)
        self.assertEqual("q5", deck.get_next_card(consume=True).front)
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.time_fun = lambda: 10000
        self.assertEqual("q1", deck.get_next_card(consume=True).front)
        self.assertEqual(None, deck.get_next_card(consume=True))
        self.assertEqual(None, deck.get_next_card(consume=True))
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.time_fun = lambda: 10001
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.time_fun = lambda: 10002
        self.assertEqual("q6", deck.get_next_card(consume=True).front)
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.insert_card(FlashCard("q7", "a7", timestamp=10002), 0)
        self.assertEqual("q7", deck.get_next_card(consume=True).front)
        self.assertEqual(None, deck.get_next_card(consume=True))

    def test_wrong(self):
        deck = Deck()
        deck.insert_card(FlashCard("q3", "a3"), 3)
        card = deck.get_next_card(consume=True)
        self.assertEqual(3, card.box)
        deck.wrong(card)
        self.assertEqual(0, card.box)
        card.timestamp = 0
        deck.restart()
        card = deck.get_next_card(consume=True)
        card.timestamp = 0
        self.assertEqual(0, card.box)
        self.assertEqual("q3", card.front)

    def test_right(self):
        deck = Deck()
        deck.insert_card(FlashCard("q3", "a3"), 3)
        card = deck.get_next_card(consume=True)
        self.assertEqual(3, card.box)
        deck.right(card)
        card.timestamp = 0
        card = deck.get_next_card(consume=True)
        self.assertEqual(4, card.box)
        self.assertEqual("q3", card.front)
        # Cannot promote card beyond last box.
        deck.right(card)
        card.timestamp = 0
        self.assertEqual(5, card.box)
        self.assertEqual("q3", card.front)

    def test_card_expiry(self):
        expiries = [0, 500, 1000, 5000, 8000, 10000]
        deck = Deck(expiries)
        c0 = FlashCard("front", "back", box=0, timestamp=1000)
        self.assertTrue(deck.card_expired(c0, time_fun=lambda: 1000))
        c1 = FlashCard("front", "back", box=1, timestamp=1000)
        self.assertFalse(deck.card_expired(c1, time_fun=lambda: 1000 + 100))
        self.assertFalse(deck.card_expired(c1, time_fun=lambda: 1000 + 499))
        self.assertTrue(deck.card_expired(c1, time_fun=lambda: 1000 + 500))
        self.assertTrue(deck.card_expired(c1, time_fun=lambda: 1000 + 501))
        c2 = FlashCard("front", "back", box=2, timestamp=1000)
        self.assertFalse(deck.card_expired(c2, time_fun=lambda: 1000))
        self.assertFalse(deck.card_expired(c2, time_fun=lambda: 1000 + 100))
        self.assertFalse(deck.card_expired(c2, time_fun=lambda: 1000 + 999))
        self.assertTrue(deck.card_expired(c2, time_fun=lambda: 1000 + 1000))
        self.assertTrue(deck.card_expired(c2, time_fun=lambda: 1000 + 1001))
        # Card in last box never expires.
        c3 = FlashCard("front", "back", box=5, timestamp=1000)
        self.assertFalse(deck.card_expired(c3, time_fun=lambda: 1000))
        self.assertFalse(deck.card_expired(c3, time_fun=lambda: 1000 + 9999))
        self.assertFalse(deck.card_expired(c3, time_fun=lambda: 1000 + 10000))
        self.assertFalse(deck.card_expired(c3, time_fun=lambda: 1000 + 100000))

    def test_simple_session(self):
        expiries = [0, 1, 2, 3, 4, 100]
        deck = Deck(expiries)
        deck.time_fun = lambda: 1000
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.insert_card(FlashCard("q1", "a1", timestamp=1000), 0)

        # Card in box 0, right answer, move to 1
        deck.time_fun = lambda: 1001
        card = deck.get_next_card(consume=True)
        self.assertEqual("q1", card.front)
        deck.wrong(card)
        self.assertEqual(1001, card.timestamp)
        card = deck.get_next_card(consume=True)
        self.assertEqual("q1", card.front)
        self.assertEqual(1001, card.timestamp)
        deck.time_fun = lambda: 1002
        deck.right(card)
        self.assertEqual(1, card.box)
        self.assertEqual(1002, card.timestamp)

        # Card now in box 1, right answer, move to 2
        card = deck.get_next_card(consume=True)
        self.assertEqual(None, deck.get_next_card(consume=True))
        # .. Expire
        deck.time_fun = lambda: 1003
        card = deck.get_next_card(consume=True)
        self.assertEqual("q1", card.front)
        deck.right(card)
        self.assertEqual(2, card.box)
        self.assertEqual(1003, card.timestamp)

        # Card now in box 2, wrong answer, move to 0
        card = deck.get_next_card(consume=True)
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.time_fun = lambda: 1004
        card = deck.get_next_card(consume=True)
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.time_fun = lambda: 1005
        card = deck.get_next_card(consume=True)
        self.assertEqual("q1", card.front)
        deck.wrong(card)
        self.assertEqual(0, card.box)
        self.assertEqual(1005, card.timestamp)

        # Card now in box 0, wrong answer, stay in box 0
        card = deck.get_next_card(consume=True)
        self.assertEqual("q1", card.front)
        deck.wrong(card)
        self.assertEqual(0, card.box)
        self.assertEqual(1005, card.timestamp)

    def test_dont_move_beyond_last_box(self):
        expiries = [0, 1, 2, 3, 4, 100]
        deck = Deck(expiries)
        deck.time_fun = lambda: 1000
        self.assertEqual(None, deck.get_next_card(consume=True))
        deck.insert_card(FlashCard("q1", "a1", timestamp=1000), 4)

        # Card in box 4, right answer, move to 5
        deck.time_fun = lambda: 1004
        card = deck.get_next_card(consume=True)
        self.assertEqual("q1", card.front)
        deck.right(card)
        self.assertEqual(5, card.box)
        self.assertEqual(1004, card.timestamp)

        # Card in last box. Never expires, never presented.
        deck.time_fun = lambda: 1500
        card = deck.get_next_card(consume=True)
        self.assertEqual(None, card)

    def test_get_statistics(self):
        expiries = [0, 500, 1000, 5000, 8000, 10000]
        deck = Deck(expiries, time_fun=lambda: 2001)
        self.assertEqual([[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]], deck.get_statistics())
        deck.insert_card(FlashCard("front", "back", box=0, timestamp=0))
        deck.insert_card(FlashCard("front", "back", box=0, timestamp=1000))
        deck.insert_card(FlashCard("front", "back", box=0, timestamp=1700))
        deck.insert_card(FlashCard("front", "back", box=1, timestamp=1000))
        deck.insert_card(FlashCard("front", "back", box=1, timestamp=1800))
        deck.insert_card(FlashCard("front", "back", box=1, timestamp=1900))
        deck.insert_card(FlashCard("front", "back", box=2, timestamp=1000))
        deck.insert_card(FlashCard("front", "back", box=2, timestamp=1500))
        deck.insert_card(FlashCard("front", "back", box=5, timestamp=1000))
        deck.insert_card(FlashCard("front", "back", box=5, timestamp=2000))
        self.assertEqual([[3, 3], [3, 1], [2, 1], [0, 0], [0, 0], [2, 0]], deck.get_statistics())

    def test_from_card_spec_happy_path(self):
        fc = FlashCard.from_card_spec("front")
        self.assertEqual("front", fc.front)
        self.assertEqual("", fc.back)
        self.assertEqual(0, fc.box)
        self.assertEqual(0, fc.timestamp)

        fc = FlashCard.from_card_spec("front : back")
        self.assertEqual("front", fc.front)
        self.assertEqual("back", fc.back)
        self.assertEqual(0, fc.box)
        self.assertEqual(0, fc.timestamp)

        fc = FlashCard.from_card_spec("front : back # 3")
        self.assertEqual("front", fc.front)
        self.assertEqual("back", fc.back)
        self.assertEqual(3, fc.box)
        self.assertEqual(0, fc.timestamp)

        fc = FlashCard.from_card_spec("front : back # 3 @ 1000")
        self.assertEqual("front", fc.front)
        self.assertEqual("back", fc.back)
        self.assertEqual(3, fc.box)
        self.assertEqual(1000, fc.timestamp)

    def test_from_card_spec_corner_cases(self):
        fc = FlashCard.from_card_spec("front:")
        self.assertEqual("front:", fc.front)
        self.assertEqual("", fc.back)
        fc = FlashCard.from_card_spec("front :")
        self.assertEqual("front :", fc.front)
        self.assertEqual("", fc.back)
        fc = FlashCard.from_card_spec("front : ")
        self.assertEqual("front", fc.front)
        self.assertEqual("", fc.back)
        fc = FlashCard.from_card_spec("front : back @ 123")
        self.assertEqual("front", fc.front)
        self.assertEqual("back @ 123", fc.back)
        fc = FlashCard.from_card_spec("front : back #")
        self.assertEqual("front", fc.front)
        self.assertEqual("back #", fc.back)
        self.assertEqual(0, fc.box)
        self.assertEqual(0, fc.timestamp)
        fc = FlashCard.from_card_spec("front : back #123")
        self.assertEqual("front", fc.front)
        self.assertEqual("back #123", fc.back)
        self.assertEqual(0, fc.box)
        self.assertEqual(0, fc.timestamp)
        fc = FlashCard.from_card_spec("front :  # 7 @ 4711")
        self.assertEqual(fc.front, "front")
        self.assertEqual(fc.back, "")
        self.assertEqual(fc.box, 7)
        self.assertEqual(fc.timestamp, 4711)

    def test_from_card_spec_malformed(self):
        fc = FlashCard.from_card_spec("")
        self.assertEqual(None, fc)
        fc = FlashCard.from_card_spec("front : back # abc")
        self.assertEqual(None, fc)
        fc = FlashCard.from_card_spec("front : back # 3 @ ab")
        self.assertEqual(None, fc)
        fc = FlashCard.from_card_spec("front : back # 123@")
        self.assertEqual(None, fc)

    def test_load_cards_happy_path(self):
        deck = Deck()
        deck.load_from_specs(["q1 : a1 # 4 @ 100", "q2 : a2 # 1", "q3", "q4 : a4 # 0 @ 200"])
        self.assertEqual("q1", deck.boxes[4][0].front)
        self.assertEqual("a2", deck.boxes[1][0].back)
        self.assertEqual(0, deck.boxes[1][0].timestamp)
        self.assertEqual("q3", deck.boxes[0][0].front)
        self.assertEqual(0, deck.boxes[0][0].timestamp)
        self.assertEqual("a4", deck.boxes[0][1].back)
        self.assertEqual(200, deck.boxes[0][1].timestamp)

    def test_load_cards_malformed(self):
        deck = Deck()
        with self.assertRaises(Deck.CardSpecError):
            deck.load_from_specs(["q1 : a1 # 4 @ 100", "q2 : a2 # error", "q3", "q4 : a4 # 0 @ 200"])

    def test_to_card_spec(self):
        fc = FlashCard("front", "back", box=4, timestamp=100)
        self.assertEqual("front : back # 4 @ 100", fc.to_card_spec())
        fc = FlashCard("front1", box=7)
        self.assertEqual("front1 :  # 7 @ 0", fc.to_card_spec())

    def test_next_expiry(self):
        expiries = [0, 500, 1000, 5000, 8000, 10000]
        deck = Deck(expiries, time_fun=lambda: 2001)
        deck.insert_card(FlashCard("front", "back", box=5, timestamp=2000))
        # Cards in last box never expire.
        self.assertEqual(None, deck.next_expiry())
        deck.insert_card(FlashCard("front", "back", box=4, timestamp=1000))
        self.assertEqual(1000 + 8000 - 2001, deck.next_expiry())
        deck.insert_card(FlashCard("front", "back", box=2, timestamp=1500))
        self.assertEqual(1500 + 1000 - 2001, deck.next_expiry())
        deck.insert_card(FlashCard("front", "back", box=2, timestamp=1000))
        self.assertEqual(0, deck.next_expiry())
