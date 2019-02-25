#!/usr/bin/env python3

#
# flashme -- Flashcards for command-line aficionados.
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

class Flashme:
    def __init__(self):
        parser = argparse.ArgumentParser(description="A flashcard system for command-line aficionados")
        parser.add_argument("file", nargs="?", type=str, default=None, help="Flashcard file to be used")
        parser.add_argument("-v", "--version", action="store_true", help="Show flashcard version")
        parser.add_argument(
            "-c", "--cram", nargs="?", type=int, const=-1, metavar="N",
            help="Cram mode for box N. -1: random box cramming (default)")
        parser.add_argument("-i", "--info", action="store_true", help="Show deck info/statistics")
        parser.add_argument("-t", "--terse", action="store_true", help="Terse output style")
        parser.add_argument("-s", "--silent-start", action="store_true", help="Silently exit if no cards have expired")
        parser.add_argument("-r", "--reverse", action="store_true", help="Reverse learning: show back and ask for front")
        self.args = parser.parse_args()

        self.view = View(self.args.terse, self.args.reverse)

        if self.args.version:
            print(self.view.print_version(VERSION))
            sys.exit(0)

        if not self.args.file:
            parser.print_help()
            View.die("Please provide a flashcard file")

        if not os.access(self.args.file, os.R_OK | os.W_OK):
            View.die("Flashcard file does not exist or is not accessible")

        self.deck = Deck(filename=self.args.file)
        self.deck.load_from_file()
        self.controller = Controller(self.deck, self.args.cram)

        if self.args.info:
            print(self.view.print_info(self.deck.get_statistics()))
            sys.exit(0)

        if self.args.cram is None:
            self.get_next_card_fun = lambda: self.deck.get_next_card(consume=False)
        else:
            self.get_next_card_fun = self.init_cram_mode()

        if self.args.silent_start and not self.get_next_card_fun():
            sys.exit(0)

    def run(self):
        try:
            print(self.view.print_version(VERSION))
            print(self.view.print_info(self.deck.get_statistics()))
            self.study_loop()

        except Deck.CardSpecError as cse:
            View.die(str(cse))

    def study_loop(self):
        while True:
            my_card = self.get_next_card_fun()
            if not my_card:
                next_expiry = self.deck.next_expiry()
                if next_expiry is not None:
                    print(self.view.print_nothing_to_do_come_back(next_expiry / SECS_PER_DAY))
                else:
                    print(self.view.print_nothing_to_do())
                self.controller.handle(Controller.input_quit, my_card)
                break
            print(self.view.print_question(my_card), end="")
            while True:
                print(self.view.print_input(my_card.back), end="")
                my_inp = input().upper()
                result = self.controller.handle(my_inp, my_card)
                if result[0] == Controller.input_info:
                    print(self.view.print_info(self.deck.get_statistics()))
                elif result[0] == Controller.input_show:
                    print(self.view.print_answer(my_card), end="")
                elif result[0] == Controller.input_cancel:
                    my_inp = input(self.view.print_input_cancel_check()).upper()
                    if my_inp == Controller.input_yes:
                        return
                else:
                    break

            if my_inp == Controller.input_quit:
                return

    def init_cram_mode(self):
        sts = self.deck.get_statistics()
        tot = sum(card_count for card_count, expired in sts)
        if tot == 0:
            View.die("All boxes are empty")
        if -1 <= self.args.cram <= self.deck.max_box_num:
            if self.args.cram == -1:
                cram_box_str = "random"
            else:
                if sts[self.args.cram][0] == 0:
                    View.die("Box %d is empty" % self.args.cram)
                cram_box_str = "box " + str(self.args.cram)
            print("CRAMMING (%s)" % cram_box_str)
            return lambda: self.deck.get_next_card_cram_mode(cram=self.args.cram, consume=False)
        else:
            View.die("Cram box number must be in range -1 .. " + str(self.deck.max_box_num))
        return None

if __name__ == "__main__":
    Flashme().run()
