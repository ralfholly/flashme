import time
import sys
import random

from flashcard import FlashCard

SECS_PER_DAY = 60 * 60 * 24

# pylint:disable=too-many-instance-attributes
class Deck:
    class CardSpecError(Exception):
        pass

    default_expiries = [(SECS_PER_DAY) * expiry for expiry in [0, 2, 10, 30, 90, 1000000]]

    def __init__(self, expiries=default_expiries, filename="", **kwargs):
        self.box_count = len(expiries)
        self.max_box_num = self.box_count - 1
        self.expiries = expiries
        self.filename = filename

        self.time_fun = kwargs['time_fun'] if 'time_fun' in kwargs else lambda: int(time.time())

        assert len(self.expiries) == self.box_count
        self.boxes = [[] for _ in range(self.box_count)]
        self.current_box_index = 0
        self.current_card_index = None

    def load_from_specs(self, card_specs):
        for card_spec in card_specs:
            clean_card_spec = card_spec.rstrip()
            if clean_card_spec:
                card = FlashCard.from_card_spec(clean_card_spec)
                if card:
                    if 0 <= card.box <= self.max_box_num:
                        self.boxes[card.box].append(card)
                    else:
                        raise Deck.CardSpecError("Box number out of range: " + card_spec)
                else:
                    raise Deck.CardSpecError("Malformed card spec: " + card_spec)

    def insert_card(self, card, box=-1):
        box = box if box != -1 else card.box
        if box < self.box_count:
            card.box = box
            self.boxes[box].append(card)

    def restart(self):
        self.current_box_index = 0

    def card_expired(self, card, **kwargs):
        time_fun = kwargs['time_fun'] if 'time_fun' in kwargs else self.time_fun
        return time_fun() - card.timestamp >= self.expiries[card.box]

    def get_next_card(self, consume=True):
        starting_box = self.current_box_index
        while True:
            for current_card_index, card in enumerate(self.boxes[self.current_box_index]):
                if self.card_expired(card):
                    self.current_card_index = current_card_index
                    if consume:
                        self.consume_current_card()
                    return card
            self.current_box_index = (self.current_box_index + 1) % self.box_count
            if self.current_box_index == starting_box:
                break
        # No current card
        self.current_card_index = None
        return None

    def get_next_card_cram_mode(self, cram=None, consume=True):
        assert cram is not None
        self.current_box_index = -1
        if cram == -1:
            while self.current_box_index == -1:
                box_index = random.randint(0, self.max_box_num)
                if self.boxes[box_index]:
                    self.current_box_index = box_index
        else:
            self.current_box_index = cram

        assert self.boxes[self.current_box_index]
        self.current_card_index = random.randint(0, len(self.boxes[self.current_box_index]) - 1)
        card = self.boxes[self.current_box_index][self.current_card_index]
        if consume:
            self.consume_current_card()
        return card

    def consume_current_card(self):
        if not self.current_card_index is None:
            self.boxes[self.current_box_index].pop(self.current_card_index)
        self.current_card_index = None

    def wrong(self, card):
        card.box = 0
        card.timestamp = self.time_fun()
        self.boxes[0].append(card)

    def right(self, card):
        if card.box < self.box_count - 1:
            card.box += 1
        card.timestamp = self.time_fun()
        self.boxes[card.box].append(card)

    def get_statistics(self):
        stats = []
        for box in self.boxes:
            expired_total = 0
            for card in box:
                expired_total += 1 if self.card_expired(card) else 0
            stats.append([len(box), expired_total])
        return stats

    def next_expiry(self):
        now = self.time_fun()
        min_expiry = sys.maxsize
        for box_index, box in enumerate(self.boxes):
            for card in box:
                expiry = card.timestamp + self.expiries[box_index] - now
                if expiry < 0:
                    expiry = 0
                min_expiry = min(min_expiry, expiry)
        return min_expiry

    def load_from_file(self):
        with open(self.filename, "r") as f:
            card_specs = f.readlines()
        self.load_from_specs(card_specs)

    def save_to_file(self):
        with open(self.filename, "w") as f:
            for box in self.boxes:
                for card in box:
                    f.write(card.to_card_spec())
                    f.write("\n")