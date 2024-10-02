#!/bin/sh
         [ -e "commands/memstats_-r-group-stats--u-MB.txt" ] && exit
         ls "commands/memstats_-r-group-stats--u-MB.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/memstats_-r-group-stats--u-MB.txt"
         rm -f "commands/memstats_-r-group-stats--u-MB.txt.FRAG-"*


