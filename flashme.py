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
    input_show = "S"
    input_abort = "A"
    input_abort_yes = "Y"

    def __init__(self, deck, cram):
        self.deck = deck
        self.cram = cram

    def handle(self, inp, card):
        retval = (None, None)
        if inp == Controller.input_quit:
            self.deck.save_to_file()
            retval = (inp, None)
        elif inp == Controller.input_info:
            retval = (inp, self.deck.get_statistics)
        elif inp == Controller.input_yes:
            # No promotion in cram mode.
            if self.cram is None:
                self.deck.consume_current_card()
                self.deck.right(card)
            retval = (inp, None)
        elif inp == Controller.input_no:
            self.deck.consume_current_card()
            self.deck.wrong(card)
            retval = (inp, None)
        elif inp == Controller.input_show:
            retval = (inp, card.back)
        elif inp == Controller.input_abort:
            retval = (inp, None)
        # Default: show answer
        elif not inp and card.back:
            retval = (Controller.input_show, card.back)
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
        out_show = "[S]how"
        out_rest = "(Y)es (N)o (I)nfo (Q)uit (A)bort "
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

    def print_input_abort_check(self):
        self = self
        return "Abort without saving? Y/N "

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
        parser.add_argument(
            "-c", "--cram", nargs="?", type=int, const=-1, metavar="N",
            help="Cram mode for box N. -1: random box cramming (default)")
        parser.add_argument("-i", "--info", action="store_true", help="Show deck info/statistics")
        args = parser.parse_args()

        if args.version:
            print(VERSION)
            sys.exit(0)

        if not args.file:
            parser.print_help()
            View.die("Please provide a flashcard file")

        if not os.access(args.file, os.R_OK | os.W_OK):
            View.die("Flashcard file does not exist or is not accessible")

        my_deck = Deck(filename=args.file)
        my_deck.load_from_file()
        my_controller = Controller(my_deck, args.cram)
        my_view = View()

        if args.info:
            print(my_view.print_info(my_deck.get_statistics()))
            sys.exit(0)

        print("flashme", VERSION)

        if args.cram is None:
            get_next_card = lambda: my_deck.get_next_card(consume=False)
        else:
            sts = my_deck.get_statistics()
            tot = sum(card_count for card_count, expired in sts)
            if tot == 0:
                View.die("All boxes are empty")
            if -1 <= args.cram <= my_deck.max_box_num:
                if args.cram == -1:
                    cram_box_str = "random"
                else:
                    if sts[args.cram][0] == 0:
                        View.die("Box %d is empty" % args.cram)
                    cram_box_str = "box " + str(args.cram)
                print("CRAMMING (%s)" % cram_box_str)
                get_next_card = lambda: my_deck.get_next_card_cram_mode(cram=args.cram, consume=False)
            else:
                View.die("Cram box number must be in range -1 .. " + str(my_deck.max_box_num))

        print(my_view.print_info(my_deck.get_statistics()))

        carry_on = True
        while carry_on:
            my_card = get_next_card()
            if not my_card:
                next_expiry_in_days = my_deck.next_expiry() / SECS_PER_DAY
                print(my_view.print_nothing_to_do(next_expiry_in_days))
                my_deck.save_to_file()
                break
            print(my_view.print_front(my_card.front))
            while carry_on:
                my_inp = input(my_view.print_input(my_card.back)).upper()
                result = my_controller.handle(my_inp, my_card)
                if result[0] == Controller.input_info:
                    print(my_view.print_info(my_deck.get_statistics()))
                elif result[0] == Controller.input_show:
                    print(my_view.print_back(my_card.back))
                elif result[0] == Controller.input_abort:
                    my_inp = input(my_view.print_input_abort_check()).upper()
                    if my_inp == Controller.input_yes:
                        carry_on = False
                else:
                    carry_on = False

            if my_inp == Controller.input_quit:
                carry_on = False

    except Deck.CardSpecError as cse:
        View.die(str(cse))
