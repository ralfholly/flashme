#!/usr/bin/env python3

# pylint:disable=too-few-public-methods
class FlashCard:
    def __init__(self, front, back, box=0):
        self.front = front
        self.back = back
        self.box = box

class Deck:
    box_count = 5

    def __init__(self, filename=""):
        self.filename = filename
        self.boxes = [[] for _ in range(Deck.box_count)]
        self.current_box = 0

    def insert_card(self, card, box):
        if box < Deck.box_count:
            card.box = box
            self.boxes[box].append(card)

    def restart(self):
        self.current_box = 0

    def get_next_card(self):
        next_card = None
        while self.current_box < Deck.box_count:
            if self.boxes[self.current_box]:
                next_card = self.boxes[self.current_box].pop(0)
                break
            self.current_box += 1
        return next_card

    def wrong(self, card):
        card.box = 0
        self.boxes[0].append(card)

    def right(self, card):
        if card.box < Deck.box_count - 1:
            card.box += 1
        self.boxes[card.box].append(card)
