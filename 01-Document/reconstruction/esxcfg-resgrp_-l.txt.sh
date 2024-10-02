#!/bin/sh
         [ -e "commands/esxcfg-resgrp_-l.txt" ] && exit
         ls "commands/esxcfg-resgrp_-l.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/esxcfg-resgrp_-l.txt"
         rm -f "commands/esxcfg-resgrp_-l.txt.FRAG-"*
      