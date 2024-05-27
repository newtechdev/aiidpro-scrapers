# AIIDpro Scrapy
## Overview
This project includes scrapy spider named with "IdentityIQ" and fastAPI to schedule spider.
## Requirements
Python 3.10+
<br>
Works on Linux
## Install
git clone
<br>
cd app
<br>
python3 -m venv venv
<br>
pip install -r requirements.txt
<br>
nohup scrapyd &
<br>
scrapyd-deploy default
<br>
nohup uvicorn main:app --host 0.0.0.0 --port 80
