
# pylint:disable=too-few-public-methods
class FlashCard:
    sep_back = ' : '
    sep_box = ' # '
    sep_timestamp = ' @ '

    def __init__(self, front, back="", box=0, timestamp=0):
        assert front != None
        self.front = front
        assert back != None
        self.back = back
        assert box != None
        self.box = box
        assert timestamp != None
        self.timestamp = timestamp

    def to_card_spec(self):
        card_spec = ""
        card_spec += self.front
        card_spec += FlashCard.sep_back + self.back
        card_spec += FlashCard.sep_box + str(self.box)
        card_spec += FlashCard.sep_timestamp + str(self.timestamp)
        return card_spec

    @classmethod
    def from_card_spec(cls, card_spec):
        # <front>[ : <back>][ # <box>][ @ <timestamp>]
        card = None
        if card_spec:
            front_and_rest = card_spec.split(FlashCard.sep_back)
            front = front_and_rest[0]
            back_and_rest = front_and_rest[1].split(FlashCard.sep_box) if len(front_and_rest) == 2 else [""]
            back = back_and_rest[0]
            box_and_rest = back_and_rest[1].split(FlashCard.sep_timestamp) if len(back_and_rest) == 2 else [0]
            try:
                box = int(box_and_rest[0])
                timestamp = int(box_and_rest[1]) if len(box_and_rest) == 2 else 0
                card = cls(front, back, box=box, timestamp=timestamp)
            except ValueError:
                pass
        return card
