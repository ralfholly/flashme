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
