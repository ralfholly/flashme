#!/usr/bin/env python3

#
# flashme -- Flashcards for command-line aficionados.
# Copyright (c) 2019 Ralf Holly, MIT License, see LICENSE file.
#

import argparse
import sys
import os
import subprocess

from deck import Deck, SECS_PER_DAY
from view import View
from controller import Controller

VERSION = "1.3.1"

class Flashme:
    """ Main program entry point.
        Parses and handles command-line arguments, executes the study loop.
    """
    def __init__(self):
        parser = argparse.ArgumentParser(description="A flashcard system for command-line aficionados")
        parser.add_argument("file", nargs="?", type=str, default=None, metavar="DECKFILE", help="Flashcard deckfile to be used")
        parser.add_argument("-v", "--version", action="store_true", help="Show flashcard version")
        parser.add_argument(
            "-c", "--cram", nargs="?", type=int, const=-1, metavar="N",
            help="Cram mode for box N. -1: random box cramming (default)")
        parser.add_argument("-i", "--info", action="store_true", help="Show deck info/statistics")
        parser.add_argument("-t", "--terse", action="store_true", help="Terse output style")
        parser.add_argument("-s", "--silent-start", action="store_true", help="Silently exit if no cards have expired")
        parser.add_argument("-r", "--reverse", action="store_true", help="Reverse learning: show back and ask for front")
        parser.add_argument("-e", "--edit", action="store_true", help="Edit deckfile with editor defined by EDITOR variable")
        parser.add_argument("-x", "--expired", nargs="+", type=str, default=None, metavar="DECKFILE", help="List count of expired cards for given deckfiles")
        self.args = parser.parse_args()

        self.view = View(self.args.terse, self.args.reverse, self.args.cram)

        if self.args.version:
            print(self.view.print_version(VERSION))
            sys.exit(0)

        if self.args.edit:
            self.launch_editor(self.args.file)

        if self.args.expired:
            print(self.view.print_expired_counts(Flashme.get_expired_counts(self.args.expired)), end="")
            sys.exit(0)

        if not self.args.file:
            parser.print_help()
            View.die("Please provide a flashcard file")

        try:
            self.deck = Deck(filename=self.args.file)
            self.deck.load_from_file()
        except Deck.DeckfileNotFoundError as dfe:
            View.die(dfe)

        self.controller = Controller(self.deck, self.args.cram)

        if self.args.info:
            print(self.view.print_info(self.deck.get_statistics()))
            sys.exit(0)

        if self.args.cram is None:
            self.get_next_card_fun = self.deck.get_next_card
        else:
            self.get_next_card_fun = self.init_cram_mode()

        if self.args.silent_start and not self.get_next_card_fun():
            sys.exit(0)

    def run(self):
        try:
            print(self.view.print_version(VERSION))
            print(self.view.print_deckfile(self.deck.filename))
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
                    print(self.view.print_answer(my_card), end="" if not self.args.cram else " ")
                    # In cram mode, wait for return key press then proceed to next question.
                    if self.args.cram:
                        input()
                        break
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
        elif -1 <= self.args.cram <= self.deck.max_box_num:
            if self.args.cram == -1:
                cram_box_str = "random"
            else:
                if sts[self.args.cram][0] == 0:
                    View.die("Box %d is empty" % self.args.cram)
                cram_box_str = "box " + str(self.args.cram)
            print("CRAMMING (%s)" % cram_box_str)
            return lambda: self.deck.get_next_card_cram_mode(cram=self.args.cram)
        else:
            View.die("Cram box number must be in range -1 .. " + str(self.deck.max_box_num))
        return None

    def launch_editor(self, deckfile):
        editor = os.environ.get("EDITOR")
        if not editor:
            View.die("EDITOR environment variable not defined")
        deckfile = Deck.locate_file(self.args.file)
        if not deckfile:
            View.die("Deckfile " + self.args.file + " doesn't exist")
        try:
            subprocess.run((editor, deckfile), check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            View.die("Failed to launch editor " + editor)

    @staticmethod
    def get_expired_counts(deckfiles):
        expired_counts = []
        for deckfile in deckfiles:
            try:
                deck = Deck(filename=deckfile)
                deck.load_from_file()
                stats = deck.get_statistics()
                expired = sum([exp for tot, exp in stats])
                if expired:
                    expired_counts.append((deckfile, expired))
            except Deck.DeckfileNotFoundError as dfe:
                View.die(dfe)
        return expired_counts

if __name__ == "__main__":
    Flashme().run()
