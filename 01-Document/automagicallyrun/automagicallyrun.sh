#!/bin/bash

VENV="/opt/gss/venvs/3.5"
LOCALREPO="/opt/gss/git/rmurray-amr2"
EXECUTABLE="automagicallyrun.py"

# ${USAGETRACK} $@
source ${VENV}/bin/activate
${LOCALREPO}/${EXECUTABLE} $@
