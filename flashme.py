#!/usr/bin/env python3

#
# flashme -- a flashcard system for command-line aficionados.
# Copyright (c) 2019 Ralf Holly, MIT License, see LICENSE file.
#

import argparse
import os
import os.path
import sys

from deck import Deck, SECS_PER_DAY
from view import View
from controller import Controller

VERSION = "0.0.9"

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
