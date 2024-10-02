#!/bin/sh
         [ -e "commands/esxcfg-info_-a.txt" ] && exit
         ls "commands/esxcfg-info_-a.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/esxcfg-info_-a.txt"
         rm -f "commands/esxcfg-info_-a.txt.FRAG-"*
      