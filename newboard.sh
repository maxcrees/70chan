#!/bin/bash
db=$(./config.py file db)
gopher="$(./config.py file gopher).rec"
name="$1"

if [ ! -f "$db" ]; then
    echo "! could not find $db"
    exit 1
fi

# TODO: config path for ./board.py
echo "!dirproc-raw\t$name\t./board.py" >> "$gopher"
sqlite3 "$db" "INSERT INTO boards (name) VALUES ('$name')"
touch "$(./config.py file words).$name"
