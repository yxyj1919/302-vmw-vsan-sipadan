#!/bin/sh
         [ -e "var/log/vsanmgmt.log" ] && exit
         ls "var/log/vsanmgmt.log.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "var/log/vsanmgmt.log"
         rm -f "var/log/vsanmgmt.log.FRAG-"*


