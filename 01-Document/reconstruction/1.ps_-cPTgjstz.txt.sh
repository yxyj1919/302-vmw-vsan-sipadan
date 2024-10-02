#!/bin/sh
         [ -e "commands/1.ps_-cPTgjstz.txt" ] && exit
         ls "commands/1.ps_-cPTgjstz.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/1.ps_-cPTgjstz.txt"
         rm -f "commands/1.ps_-cPTgjstz.txt.FRAG-"*

      
