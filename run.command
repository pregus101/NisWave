#!/bin/bash
cd "$(dirname "$0")"
pip3.13 install -r requirements.txt
python3.13 entry-ui.py
