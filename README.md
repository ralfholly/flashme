# flashme -- Flashcards for command-line aficionados

## Introduction

I felt compelled to write `flashme` because I couldn't find anything like it. While there are many freeware flashcard programs out there, none met my chief requirement: it must be fully operable from the command-line. My next most important requirement was that cards must be kept in plain text files (so-called deckfiles): I want to be able to diff, grep, and edit deckfiles with standard Unix command-line tools and editors. Binary file formats, including zipped XML files, are a plain nuisance and make it difficult to store flashcards in version control systems.

`flashme` is based on the original [Leitner system](https://en.wikipedia.org/wiki/Leitner_system) and uses six boxes (box 0 to box 5) with the following expiry times (in days): 0, 2, 10, 30, 90; the last box (box 5) never expires. (The number of boxes and expiry times can easily be tweaked, see "Tips and Tricks" below.)

## Usage

Fire-up your favorite editor and create cards by adding so-called CardSpecs, one per line:

```
$ vi english-german
green : grün
house : Haus
It's cold in here : hier drinnen ist es kalt
```

The front of a card is to the left of `' : '`, the back to the right. Note that there must be a space on either side of the front/back separator (colon). If you don't specify a particular box within a CardSpec, the card will go into box 0, the first box, which is what you usually want when you create new cards.

Next, you can start learning by running `flashme` like this

```
$ flashme english-german
```

All cards that have expired will be presented to you. If you indicate that you know the answer (by selecting 'Y') the card is promoted to the next box; if you don't know the answer (by selecting 'N') the card is sent back to box 0. When you select (Q)uit, all boxes (with updated box numbers and timestamps) are commited to the deskfile.

## More on CardSpecs

Formally, CardSpecs look like this:
```
<front>[ : <back>][ # <box>][ @ <timestamp>]
```
`<front>` ist the only mandatory item. `<back>` is the optional back-side of the flashcard. If `<box>` is specified, the card will be assigned to a particular box; if not, it's considered to be in box 0. `<timestamp>` represents the seconds since the Unix epoch when a flashcard was entered into a box; the default timestamp value is 0, which means that the card is considered expired.

Example:
```
sun : Sonne # 3 @ 1550826208
```
This card is in box 3 (the fourth box) and was entered on 2019-02-22 09:02:28 UTC. You can convert timestamps to human-readable date/time with the help of the `date` command:
```
$ date --date "@1550826208" --utc
Fri Feb 22 09:03:28 UTC 2019
```

`\n` character sequences within `<front>` or `<back>` will be replaced with line breaks. This way, your cards can span multiple lines.

## Regular Learning vs. Cramming

Regular learning means that only expired cards are presented for repetition. If a card is remembered correctly, it's promoted to the next higher box until it reaches box 5, where it stays forever. If a card is not remembered correctly, it goes straight back to box 0.

In cram mode (command-line option `--cram`) cards are repeated regardless of whether the card is expired or not. If it's remembered correctly, it stays where it is; otherwise, the card is demoted to box 0. An optional argument to `--cram` determines which box(es) are used for cramming: a value between `0` and `5` draws cards at random from the box with the given number; a value of `-1` randomly chooses cards from all boxes.

## Installation

Just clone the `flashme` repository to a location of your choice. It's recommended that you create a symbolic link to flashme/flashme.sh in a directory that is included in your PATH environment variable, e. g.
```
ln -s ~/flashme/flashme.sh ~/bin/flashme
```

## FLASHME_DIR

You can specify deckfile search paths via the `FLASHME_DIR` environment variable. Use the path separator of your operating system to separate search directories (i. e. `:` on Linux, `;` on Windows). When locating a deckfile, the filename as given on the command-line is tried first. If the deckfile is not reachable, all paths found in `FLASHME_DIR` are searched (in right-to-left order).

## Notification When Cards Have Expired

Personally, I prefer to manually check for expired cards every once in a while. However, here's a simple solution for you if you want to get notified when cards have expired. Run a check regularly (e. g. every hour as a cron user job) and display a notification whenever an interactive shell is opened:

```
$ crontab -e
@hourly /opt/flashme/flashme.sh --expired english-german french-german linux-tips > ~/.flashme.expired
```
```
$ vi ~/.bashrc
FLASHME_EXPIRED_FILE=~/.flashme.expired
if [ -s $FLASHME_EXPIRED_FILE ]; then
    echo "Expired Flashme decks:"
    echo "----------------------"
    cat $FLASHME_EXPIRED_FILE
    # Notify only once per hour:
    rm -f $FLASHME_EXPIRED_FILE
fi
```

Of course, it's even simpler if you run the check directly (every time) in `.bashrc` but this might mean you have to wait a couple of seconds until the prompt appears. A more sophisticated approach would utilize the `PROMPT_COMMAND` environment variable to show an nice "expired" indicator.  Let me know if you have come up with something clever!

## Tips and Tricks

- Put your deckfiles under version control, commit often!
- Display all cards in box 3:
```
grep " # 3 " deckfile
```
- Move all cards from box 5 to box 0:
```
sed -i "s/ # 5 / # 0 /" deckfile
```
- Remove all timestamps (all cards will expire immediately):
```
 sed -i "s/ @ [0-9]\+//" deckfile
```
- Use `--terse` to get a less noisy menu/prompt
- To change the number of boxes or box expiry times, just modify this list in `deck.py`:
```
default_expiries_days = [0, 2, 10, 30, 90, -1]
```
Please note that the last box never expires, so the actual expiry value of the last list element doesn't really matter.
