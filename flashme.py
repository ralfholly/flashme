#!/usr/bin/env python3

#   __ _           _
#  / _| | __ _ ___| |__  _ __ ___   ___
# | |_| |/ _` / __| '_ \| '_ ` _ \ / _ \
# |  _| | (_| \__ \ | | | | | | | |  __/
# |_| |_|\__,_|___/_| |_|_| |_| |_|\___|
#

import time

# pylint:disable=too-few-public-methods
class FlashCard:
    sep_back = ' : '
    sep_box = ' # '
    sep_timestamp = ' @ '

    def __init__(self, front, back="", box=0, timestamp=0):
        assert front != None
        self.front = front
        assert back != None
        self.back = back
        assert box != None
        self.box = box
        assert timestamp != None
        self.timestamp = timestamp

    def to_card_spec(self):
        card_spec = ""
        card_spec += self.front
        card_spec += FlashCard.sep_back + self.back
        card_spec += FlashCard.sep_box + str(self.box)
        card_spec += FlashCard.sep_timestamp + str(self.timestamp)
        return card_spec

    @classmethod
    def from_card_spec(cls, card_spec):
        # <front>[ : <back>][ # <box>][ @ <timestamp>]
        card = None
        if card_spec:
            front_and_rest = card_spec.split(FlashCard.sep_back)
            front = front_and_rest[0]
            back_and_rest = front_and_rest[1].split(FlashCard.sep_box) if len(front_and_rest) == 2 else [""]
            back = back_and_rest[0]
            box_and_rest = back_and_rest[1].split(FlashCard.sep_timestamp) if len(back_and_rest) == 2 else [0]
            try:
                box = int(box_and_rest[0])
                timestamp = int(box_and_rest[1]) if len(box_and_rest) == 2 else 0
                card = cls(front, back, box=box, timestamp=timestamp)
            except ValueError:
                pass
        return card


class CardSpecError(Exception):
    pass

class Deck:
    default_expiries = [(60 * 60 * 24) * expiry for expiry in [0, 2, 10, 30, 90, 1000000]]

    def __init__(self, expiries=default_expiries, filename="", **kwargs):
        self.box_count = 6
        self.max_box_num = self.box_count - 1
        self.expiries = expiries
        self.filename = filename

        self.time_fun = kwargs['time_fun'] if 'time_fun' in kwargs else time.time

        assert len(expiries) == self.box_count
        self.boxes = [[] for _ in range(self.box_count)]
        self.current_box = 0

    def load_cards(self, card_specs):
        for card_spec in card_specs:
            card = FlashCard.from_card_spec(card_spec)
            if card:
                if 0 <= card.box <= self.max_box_num:
                    self.boxes[card.box].append(card)
                else:
                    raise CardSpecError("Box number out of range: " + card_spec)
            else:
                raise CardSpecError("Malformed card spec: " + card_spec)

    def insert_card(self, card, box=-1):
        box = box if box != -1 else card.box
        if box < self.box_count:
            card.box = box
            self.boxes[box].append(card)

    def restart(self):
        self.current_box = 0

    def card_expired(self, card, **kwargs):
        time_fun = kwargs['time_fun'] if 'time_fun' in kwargs else self.time_fun
        return time_fun() - card.timestamp >= self.expiries[card.box]

    def get_next_card(self):
        starting_box = self.current_box
        while True:
            for index, card in enumerate(self.boxes[self.current_box]):
                if self.card_expired(card):
                    self.boxes[self.current_box].pop(index)
                    return card
            self.current_box = (self.current_box + 1) % self.box_count
            if self.current_box == starting_box:
                break
        return None

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

class Controller:
    input_quit = "Q"
    input_info = "I"
    input_yes = "Y"
    input_no = "N"
    input_answer = "A"

    def __init__(self, deck):
        self.deck = deck

    def handle(self, inp, card):
        self = self
        if inp == Controller.input_quit:
            return (inp, None)
        elif inp == Controller.input_info:
            return (inp, self.deck.get_statistics)
        elif inp == Controller.input_yes:
            self.deck.right(card)
            return (inp, None)
        elif inp == Controller.input_no:
            self.deck.wrong(card)
            return (inp, None)
        elif inp == Controller.input_answer:
            return (inp, card.back)
        # Default: show answer
        elif not inp and card.back:
            return (Controller.input_answer, card.back)
        return (None, None)

class View:
    def print_front(self, front):
        self = self
        return "Front: " + front

    def print_back(self, back):
        self = self
        return "Back: " + back

    def print_info(self, stats, verbose=True):
        self = self
        cards_total = 0
        expired_total = 0
        for entry in stats:
            cards_total += entry[0]
            expired_total += entry[1]
        out = "Expired/total: %d/%d" % (expired_total, cards_total)
        if verbose:
            out += " ("
            for box, entry in enumerate(stats):
                out += "%d/%d" % (entry[1], entry[0])
                if box != len(stats) - 1:
                    out += " "
            out += ")"
        return out

    def print_input(self, card_back):
        self = self
        out_show = "[A]nswer"
        out_rest = "(Y)es (N)o (I)nfo (Q)uit "
        if card_back:
            return out_show + " " + out_rest
        return out_rest

# pylint:disable=invalid-name
if __name__ == "__main__":
    my_expiries = [0, 1, 2, 3, 4, 100]
    my_deck = Deck(my_expiries)
    my_deck.time_fun = lambda: 105
    my_deck.load_cards(["q1 : a1 # 4 @ 100", "q2 : a2 # 1", "q3 : a3 # 1 @ 101", "q4 : a4 # 0 @ 200"])
    my_controller = Controller(my_deck)
    my_view = View()

    print(my_view.print_info(my_deck.get_statistics()))

    while True:
        my_card = my_deck.get_next_card()
        if not my_card:
            break
        print(my_view.print_front(my_card.front))
        while True:
            my_inp = input(my_view.print_input(my_card.back)).upper()
            result = my_controller.handle(my_inp, my_card)
            if result[0] == Controller.input_info:
                print(my_view.print_info(my_deck.get_statistics()))
            elif result[0] == Controller.input_answer:
                print(my_view.print_back(my_card.back))
            else:
                break
        if my_inp == Controller.input_quit:
            print("Bye.....")
            break
