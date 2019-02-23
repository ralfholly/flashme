import math
import sys

# pylint:disable=no-self-use
class View:
    def __init__(self, terse):
        self.terse = terse

    def print_front(self, front):
        front = "Q: " + View.replace_escapes(front)
        if not self.terse:
            front += "\n"
        return front

    def print_back(self, back):
        back = "A: " + View.replace_escapes(back)
        if not self.terse:
            back += "\n"
        return back

    def print_info(self, stats, verbose=True):
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
        out = ""
        if not self.terse:
            out = "(Y)es (N)o (I)nfo (Q)uit (C)ancel"
            if card_back:
                out = "[A]nswer " + out
        return out + " "

    def print_nothing_to_do(self):
        return "Nothing left to do!"

    def print_nothing_to_do_come_back(self, come_back_days):
        days = int(come_back_days)
        hours = math.ceil((come_back_days - days) * 24)
        text = "Nothing left to do! Please come back in"
        if days > 0:
            text += " %d day(s)" % days
        if hours > 0:
            text += " %d hour(s)" % hours
        return text

    def print_input_cancel_check(self):
        return "Cancel without saving? Y/N "

    def print_version(self, version):
        return "flashme, version " + version

    @staticmethod
    def die(text):
        print("Fatal:", text, file=sys.stderr)
        sys.exit(1)

    @staticmethod
    def replace_escapes(text):
        return text.replace("\\n", "\n")
