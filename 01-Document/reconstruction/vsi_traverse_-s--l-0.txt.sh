#!/bin/sh
         [ -e "commands/vsi_traverse_-s--l-0.txt" ] && exit
         ls "commands/vsi_traverse_-s--l-0.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/vsi_traverse_-s--l-0.txt"
         rm -f "commands/vsi_traverse_-s--l-0.txt.FRAG-"*
      