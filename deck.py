import time
import sys
import random
import os
import os.path

from flashcard import FlashCard

SECS_PER_DAY = 60 * 60 * 24

# pylint:disable=too-many-instance-attributes
class Deck:
    """ Represents a deck of flashcards, distributed over boxes.
        Implements the main flashcard business logic, eg. card promotion, demotion, expiry.
    """

    class CardSpecError(Exception):
        pass

    class DeckfileNotFoundError(Exception):
        pass

    default_expiries_days = [0, 2, 10, 30, 90, -1]
    default_expiries = [(SECS_PER_DAY) * expiry_days for expiry_days in default_expiries_days]
    flashme_dir_env_string = "FLASHME_DIR"
    comment_leader = "#"

    def __init__(self, expiries=default_expiries, filename=None, **kwargs):
        self.box_count = len(expiries)
        self.max_box_num = self.box_count - 1
        self.expiries = expiries
        self.filename = None
        self.modified = False
        self.cram_list = []

        self.time_fun = kwargs['time_fun'] if 'time_fun' in kwargs else lambda: int(time.time())

        assert len(self.expiries) == self.box_count
        self.boxes = [[] for _ in range(self.box_count)]
        self.current_box_index = 0
        self.current_card_index = None
        self.deckfile_lines = []

        if filename:
            self.filename = Deck.locate_file(filename)
            if not self.filename:
                raise Deck.DeckfileNotFoundError("Flashcard file does not exist or is not accessible")

    def load_from_specs(self, card_specs):
        for line in card_specs:
            card_spec = line.rstrip()
            # Handle empty lines and comments.
            if not card_spec or card_spec.startswith(Deck.comment_leader):
                self.deckfile_lines.append(card_spec)
            else:
                card = FlashCard.from_card_spec(card_spec)
                if card:
                    if 0 <= card.box <= self.max_box_num:
                        self.boxes[card.box].append(card)
                    else:
                        raise Deck.CardSpecError("Box number out of range: " + card_spec)
                    self.deckfile_lines.append(card)
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
        return time_fun() - card.timestamp >= self.expiries[card.box] \
            if card.box < self.max_box_num else False

    def get_next_card(self, consume=False):
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

    def get_next_card_cram_mode(self, cram=None, consume=False):
        assert cram is not None
        card = None
        self.current_card_index = None

        # If cram list is empty (or has become empty), create a fresh random
        # cram list.
        if not self.cram_list:
            # Note! In cram mode we even present cards from the last box.
            if cram == -1:
                for box_index in range(self.box_count):
                    if self.boxes[box_index]:
                        for card_index in range(0, len(self.boxes[box_index])):
                            self.cram_list.append((box_index, card_index))
            else:
                for card_index in range(0, len(self.boxes[cram])):
                    self.cram_list.append((cram, card_index))
            random.shuffle(self.cram_list)

        if self.cram_list:
            self.current_box_index, self.current_card_index = self.cram_list.pop()
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
        self.modified = True

    def right(self, card):
        if card.box < self.box_count - 1:
            card.box += 1
        card.timestamp = self.time_fun()
        self.boxes[card.box].append(card)
        self.modified = True

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
        # Exclude last box.
        for box_index, box in enumerate(self.boxes[0:-1]):
            for card in box:
                expiry = card.timestamp + self.expiries[box_index] - now
                if expiry < 0:
                    expiry = 0
                min_expiry = min(min_expiry, expiry)
        return min_expiry if min_expiry < sys.maxsize else None

    def load_from_file(self):
        with open(self.filename, "r") as f:
            card_specs = f.readlines()
        self.load_from_specs(card_specs)

    def save_to_file(self):
        if self.filename and self.modified:
            with open(self.filename, "w") as f:
                for deckfile_line in self.deckfile_lines:
                    if isinstance(deckfile_line, FlashCard):
                        f.write(deckfile_line.to_card_spec() + "\n")
                    elif isinstance(deckfile_line, str):
                        f.write(deckfile_line + "\n")
                    else:
                        pass

    @staticmethod
    def locate_file(filename):
        resolved_filename = None
        # First, try filename as given.
        if os.access(filename, os.R_OK | os.W_OK):
            resolved_filename = filename
        else:
            # Then all paths found in FLASHME_DIR.
            if Deck.flashme_dir_env_string in os.environ:
                for flashme_dir in reversed(os.environ[Deck.flashme_dir_env_string].split(os.pathsep)):
                    path = os.path.join(flashme_dir, filename)
                    if os.access(path, os.R_OK | os.W_OK):
                        resolved_filename = path
                        break
        return resolved_filename
