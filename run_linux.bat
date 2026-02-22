#!/bin/bash
cd "$(dirname "$0")"
pip install -r requirements.txt --break-system-packages
python3 entry-ui.py