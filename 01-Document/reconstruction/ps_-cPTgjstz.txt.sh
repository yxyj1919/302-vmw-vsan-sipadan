#!/bin/sh
         [ -e "commands/ps_-cPTgjstz.txt" ] && exit
         ls "commands/ps_-cPTgjstz.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/ps_-cPTgjstz.txt"
         rm -f "commands/ps_-cPTgjstz.txt.FRAG-"*


