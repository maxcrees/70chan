#!/bin/bash

if [ ! -f 'config.py' ]; then
  echo '! could not find config.py'
  echo '! this script must be run from 70chan root'
  echo '! e.g. ./scripts/threadword.sh'
  exit 1
fi

if [ -z "$1" ]; then
  echo '! a board name is required'
  exit 1
fi

wordlist="$(./config.py file wordlist)"
usedwords="$(./config.py file words).$1"

# Existence of $wordlist is already checked by config.py
if [ ! -f "$usedwords" ]; then
  echo "! could not find $usedwords"
  exit 1
fi

comm -23 <(sed "s/'s//" "$wordlist" | tr 'A-Z' 'a-z' | sort -u) <(sort -u "$usedwords") | shuf -n1
