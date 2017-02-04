#!/bin/bash

if [ ! -f 'config.py' ]; then
  echo '! could not find config.py'
  echo '! this script must be run from 70chan root'
  echo '! e.g. ./scripts/newboard.sh'
  exit 1
fi

db=$(./config.py file db)
gopher="$(./config.py file gopher).rec"
root="$(./config.py file root)"
name="$1"
description="$2"

if [ ! -f "$db" ]; then
    echo "! could not find $db"
    exit 1
fi

echo -e "!dirproc-raw\t$name\t$root/board.py" >> "$gopher"
if [ -z "$description" ]; then
  sqlite3 "$db" "INSERT INTO boards (name) VALUES ('$name')"
else
  sqlite3 "$db" "INSERT INTO boards (name, description) VALUES ('$name', '$description')"
fi
wordfile="$(./config.py file words).$name"
touch "$wordfile"
echo "*** You must set the right ownership, group, and permissions on '$wordfile' ***"
