#!/bin/sh
         [ -e "var/log/dvsData.tar" ] && exit
         ls "var/log/dvsData.tar.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "var/log/dvsData.tar"
         rm -f "var/log/dvsData.tar.FRAG-"*


