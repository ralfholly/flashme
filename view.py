import math
import sys

# pylint:disable=no-self-use
class View:
    def print_front(self, front):
        return "Q: " + View.replace_escapes(front)

    def print_back(self, back):
        return "A: " + View.replace_escapes(back)

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
        out_show = "[S]how"
        out_rest = "(Y)es (N)o (I)nfo (Q)uit (A)bort "
        if card_back:
            return out_show + " " + out_rest
        return out_rest

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

    def print_input_abort_check(self):
        return "Abort without saving? Y/N "

    def print_version(self, version):
        return "flashme, version " + version

    @staticmethod
    def die(text):
        print("Fatal:", text, file=sys.stderr)
        sys.exit(1)

    @staticmethod
    def replace_escapes(text):
        return text.replace("\\n", "\n")
