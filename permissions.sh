#!/bin/bash

# Tier 1: web-facing executables
tier1=(board.py del.py post.py)
# Tier 2: secondary, non-web-facing executables
tier2=(. .git config.py data newboard.sh permissions.sh threadword.sh)
# Tier 3: non-executables
tier3=(bbs.py config.ini.sample .gopher.rec.sample LICENSE README \
       schema.sql TODO)

chmod 771 ${tier1[*]}
chmod 770 ${tier2[*]}
chmod 660 ${tier3[*]}
