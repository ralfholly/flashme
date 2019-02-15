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
    def __init__(self, front, back, **kwargs):
        self.front = front
        self.back = back
        self.box = kwargs['box'] if 'box' in kwargs else 0
        self.timestamp = kwargs['timestamp'] if 'timestamp' in kwargs else 0

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

    def print_statistics(self, stats, verbose=True):
        cards_total = 0
        expired_total = 0
        for entry in stats:
            cards_total += entry[0]
            expired_total += entry[1]
        print("Expired/total: %d/%d" % (expired_total, cards_total), end=" ")
        if verbose:
            print("(", end="")
            for box, entry in enumerate(stats):
                print("%d/%d" % (entry[1], entry[0]), end="")
                if box != len(stats) - 1:
                    print(end=" ")
            print(")", end="")
        print()
