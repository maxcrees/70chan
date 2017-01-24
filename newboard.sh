#!/bin/sh
db=$(./config.py file db)
gopher="$(./config.py file gopher).rec"
name="$1"

echo "!dirproc-raw\t$name\t./board.py" >> "$gopher"
sqlite3 "$db" "INSERT INTO boards (name) VALUES ('$name')"
