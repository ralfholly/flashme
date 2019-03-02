#!/bin/bash

#
# Use 'notify-send' to inform about expired decks/cards
#

if [ -z $1 ]; then
    echo "Usage: $0 <deckfile> ..."
    exit 1
fi

THIS_DIR=$(dirname $(readlink -f $0))
FLASHME_EXPIRED_FILE="/tmp/flashme_expired"

$THIS_DIR/flashme.sh --expired "$@" > $FLASHME_EXPIRED_FILE
if [ -s $FLASHME_EXPIRED_FILE ]; then
    notify-send "Expired Flashme decks:" "$(cat $FLASHME_EXPIRED_FILE)"
fi
