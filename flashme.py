#!/usr/bin/env python3

import time

# pylint:disable=too-few-public-methods
class FlashCard:
    def __init__(self, front, back, **kwargs):
        self.front = front
        self.back = back
        self.box = kwargs['box'] if 'box' in kwargs else 0
        self.timestamp = kwargs['timestamp'] if 'timestamp' in kwargs else 0

class Deck:
    default_expiries = [(60 * 60 * 24) * expiry for expiry in [0, 2, 10, 30, 90, 1000000]]

    def __init__(self, expiries=default_expiries, filename=""):
        self.box_count = 6
        self.max_box_num = self.box_count - 1
        self.expiries = expiries
        self.filename = filename

        assert len(expiries) == self.box_count
        self.boxes = [[] for _ in range(self.box_count)]
        self.current_box = 0

    def insert_card(self, card, box):
        if box < self.box_count:
            card.box = box
            self.boxes[box].append(card)

    def restart(self):
        self.current_box = 0

    def card_expired(self, card, **kwargs):
        time_fun = kwargs['time_fun'] if 'time_fun' in kwargs else self.time_fun_impl
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
        self.boxes[0].append(card)

    def right(self, card):
        if card.box < self.box_count - 1:
            card.box += 1
        self.boxes[card.box].append(card)

    #pylint:disable=no-self-use
    def time_fun_impl(self):
        return time.time()
