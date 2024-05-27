# AIIDpro Scrapy
## Overview
This project includes scrapy spider named with "IdentityIQ" and fastAPI to call spider.
## Requirements
Python 3.10+
Works on Linux
## Install
git clone
cd app
python3 -m venv venv
pip install -r requirements.txt
nohup scrapyd &
scrapyd-deploy default
nohup uvicorn main:app --host 0.0.0.0 --port 80
