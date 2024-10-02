#!/bin/sh
         [ -e "commands/vmkvsitools_lsof.txt" ] && exit
         ls "commands/vmkvsitools_lsof.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/vmkvsitools_lsof.txt"
         rm -f "commands/vmkvsitools_lsof.txt.FRAG-"*


