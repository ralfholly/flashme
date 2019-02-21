#!/bin/bash

FLASHME_HOME=$(dirname $(readlink -f $0))
export PYTHONPATH=$PYTHONPATH:$FLASHME_HOME
python3 "$FLASHME_HOME/flashme.py" "$@"
