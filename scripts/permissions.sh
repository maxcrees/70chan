#!/bin/bash

if [ ! -f 'config.py' ]; then
  echo '! could not find config.py'
  echo '! this script must be run from 70chan root'
  echo '! e.g. ./scripts/permissions.sh'
  exit 1
fi

# Tier 1: web-facing executables
tier1=(board.py del.py post.py)
# Tier 2: secondary, non-web-facing executables
tier2=(. config.py data scripts scripts/*.sh)
# Tier 3: non-executables
tier3=(bbs.py data/config.ini.sample .gopher.rec.sample LICENSE README \
       schema.sql TODO)

if ! chmod -c 771 ${tier1[*]}; then
  echo 'Could not change permissions of the files; maybe you need to sudo?'
  exit 1
fi
chmod -c 770 ${tier2[*]}
chmod -c 660 ${tier3[*]}

if [ -n "$1" ] && [ -n "$2" ]; then
  if ! chown -c "$1":"$2" ${tier1[*]} ${tier2[*]} ${tier3[*]}; then
    echo 'Could not change ownership of the files; maybe you need to sudo?'
    exit 1
  fi
fi
