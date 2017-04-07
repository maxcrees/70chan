#!/bin/bash

if [ ! -f 'config.py' ]; then
  echo '! could not find config.py'
  echo '! this script must be run from 70chan root'
  echo '! e.g. ./scripts/newboard.sh'
  exit 1
fi
if [ ! -f 'data/boards.ini' ]; then
  echo '! could not find data/boards.ini'
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

echo -e "\n[$name]" >> data/boards.ini
./bbs.py genMap > "$gopher"
# TODO: XXX
# This is currently susceptible to SQL injection (I think), which isn't *too* bad
# considering this bit isn't web-facing, but it could cause cryptic errors...
if [ -z "$description" ]; then
  sqlite3 "$db" "INSERT INTO boards (name) VALUES ('$name')"
else
  sqlite3 "$db" "INSERT INTO boards (name, description) VALUES ('$name', '$description')"
fi
wordfile="$(./config.py file words).$name"
touch "$wordfile"
echo "*** You must set the right ownership, group, and permissions on '$wordfile' ***"
