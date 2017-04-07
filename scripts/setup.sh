#!/bin/bash

read -rp 'Enter username that the gopher server is running under: ' owner
if ! grep -q "^$owner" '/etc/passwd'; then
  echo 'That user does not exist, bailing out...'
  exit 1
fi

read -rp 'Enter group that the gopher server is running under: ' grp
if ! grep -q "^$grp" '/etc/group'; then
  echo 'That group does not exist, bailing out...'
  exit 1
fi

read -rp 'Enter the absolute path of 70chan installation: ' path
if [ ! -d "$path" ]; then
  echo 'That path does not exist. Bailing out...'
  exit 1
fi

cd "$path"
if [ ! -f 'config.py' ]; then
  echo "Could not find config.py in '$path', bailing out..."
  exit 1
fi
if [ ! -f 'data/boards.ini' ]; then
  echo "Could not find data/boards.ini in '$path', bailing out..."
  exit 1
fi
echo 'Changing INSTALLATION_PATH in config.py...'
sed -i "s#INSTALLATION_PATH#'$path'#" config.py

echo
echo 'Creating gophermap.rec...'
gopher="$(./config.py file gopher).rec"
./bbs.py genMap > "$gopher"

echo 'Initializing database...'
db="$(./config.py file db)"
if ! sqlite3 -bail -init 'schema.sql' "$db" '.quit'; then
  echo 'Something went wrong with SQLite, bailing out...'
  exit 1
fi

echo
echo 'Changing permissions...'
chmod -c +x scripts/permissions.sh
if ! ./scripts/permissions.sh "$owner" "$grp"; then
  exit 1
fi
echo

echo 'Run ./scripts/newboard.sh to create your first board.'

cd - &>/dev/null
