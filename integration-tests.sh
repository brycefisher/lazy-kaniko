if [[ "$CIRCLECI" == 'true' ]]; then
  apk add python3 py3-pip
else
  python -m venv venv
  source venv/bin/activate
fi

pip install -r features/requirements.txt
behave features/
