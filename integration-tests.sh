#!/bin/bash

if [[ "$CIRCLECI" == 'true' ]]; then
  apk add python3 py3-pip
else
  python3 -m venv venv
  source venv/bin/activate
fi

pip3 install -r features/requirements.txt
behave features/
