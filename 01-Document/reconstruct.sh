#!/bin/sh
         ls ./snapshot-*/reconstruction > /dev/null 2>&1
         if [ $? -ne 0 ] && [ ! -d ./reconstruction ]; then
            echo "Failed to find reconstruction directory in either current or "
            echo "snapshot directory. This script must be run from root of "
            echo "vm-support"
            exit 1
         fi
         for d in . ./snapshot-*; do
            if [ -d "$d/reconstruction" ]; then
               ( cd "$d" && for s in ./reconstruction/*; do
                  sh "$s"
               done )
            fi
         done
         