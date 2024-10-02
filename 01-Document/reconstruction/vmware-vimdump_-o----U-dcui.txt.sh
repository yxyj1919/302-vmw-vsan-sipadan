#!/bin/sh
         [ -e "commands/vmware-vimdump_-o----U-dcui.txt" ] && exit
         ls "commands/vmware-vimdump_-o----U-dcui.txt.FRAG-"* | sed 's/\(.*\)\(FRAG-\)\(.*\)/\3\ \1\2\3/' | sort -n | while read -r num file; do cat "$file"; done > "commands/vmware-vimdump_-o----U-dcui.txt"
         rm -f "commands/vmware-vimdump_-o----U-dcui.txt.FRAG-"*
      