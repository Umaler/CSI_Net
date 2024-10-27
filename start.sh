#!/usr/bin/env bash
virtualenv .env && source .env/bin/activate && pip install -r requirements.txt
ipython3 ./source/Drawer.py
