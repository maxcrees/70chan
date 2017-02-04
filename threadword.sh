#!/bin/bash
wordlist="$(./config.py file wordlist)"
usedwords="$(./config.py file words).$1"

if [ ! -f "$wordlist" ]; then
    echo "! could not find $wordlist"
    exit 1
elif [ ! -f "$usedwords" ]; then
    echo "! could not find $usedwords"
    exit 1
fi

comm -23 <(sed "s/'s//" "$wordlist" | tr 'A-Z' 'a-z' | sort -u) <(sort -u "$usedwords") | shuf -n1
