#!/bin/sh
         [ -e "commands/lspci_-e.txt" ] && exit
         ls "commands/lspci_-e.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/lspci_-e.txt"
         rm -f "commands/lspci_-e.txt.FRAG-"*


