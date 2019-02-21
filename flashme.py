#!/usr/bin/env python3

#   __ _           _
#  / _| | __ _ ___| |__  _ __ ___   ___
# | |_| |/ _` / __| '_ \| '_ ` _ \ / _ \
# |  _| | (_| \__ \ | | | | | | | |  __/
# |_| |_|\__,_|___/_| |_|_| |_| |_|\___|
#
# A flashcard system for command-line aficionados.
# Copyright (c) 2019 Ralf Holly, MIT License, see LICENSE file.
#

import argparse
import os
import os.path
import sys
import math

from deck import Deck, SECS_PER_DAY

VERSION = "0.0.9"

#pylint:disable=too-few-public-methods
class Controller:
    input_quit = "Q"
    input_info = "I"
    input_yes = "Y"
    input_no = "N"
    input_answer = "A"

    def __init__(self, deck):
        self.deck = deck

    def handle(self, inp, card):
        retval = (None, None)
        if inp == Controller.input_quit:
            self.deck.save_to_file()
            retval = (inp, None)
        elif inp == Controller.input_info:
            retval = (inp, self.deck.get_statistics)
        elif inp == Controller.input_yes:
            self.deck.consume_current_card()
            self.deck.right(card)
            retval = (inp, None)
        elif inp == Controller.input_no:
            self.deck.consume_current_card()
            self.deck.wrong(card)
            retval = (inp, None)
        elif inp == Controller.input_answer:
            retval = (inp, card.back)
        # Default: show answer
        elif not inp and card.back:
            retval = (Controller.input_answer, card.back)
        return retval

class View:
    def print_front(self, front):
        self = self
        return "Q: " + front

    def print_back(self, back):
        self = self
        return "A: " + back

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

    def print_nothing_to_do(self, come_back_days):
        self = self
        days = int(come_back_days)
        hours = math.ceil((come_back_days - days) * 24)
        text = "Nothing left to do! Please come back in"
        if days > 0:
            text += " %d day(s)" % days
        if hours > 0:
            text += " %d hour(s)" % hours
        return text

    @staticmethod
    def die(text):
        print("Fatal:", text, file=sys.stderr)
        sys.exit(1)

# pylint:disable=invalid-name
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="A flashcard system for command-line aficionados")
        parser.add_argument("file", nargs="?", type=str, default=None, help="Flashcard file to be used")
        parser.add_argument("-v", "--version", action="store_true", help="Show flashcard version")
        args = parser.parse_args()

        if args.version:
            print(VERSION)
            sys.exit(0)

        if not args.file:
            View.die("Please provide a flashcard file")

        if not os.access(args.file, os.R_OK | os.W_OK):
            View.die("Flashcard file does not exist or is not accessible")

        my_deck = Deck(filename=args.file)
        my_deck.load_from_file()
        my_controller = Controller(my_deck)
        my_view = View()

        print("flashme", VERSION)
        print(my_view.print_info(my_deck.get_statistics()))

        while True:
            my_card = my_deck.get_next_card(consume=False)
            if not my_card:
                next_expiry_in_days = my_deck.next_expiry() / SECS_PER_DAY
                print(my_view.print_nothing_to_do(next_expiry_in_days))
                my_deck.save_to_file()
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
                break

    except Deck.CardSpecError as cse:
        View.die(str(cse))
