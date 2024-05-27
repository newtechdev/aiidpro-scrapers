# AIIDpro Scrapy
## Overview
This project includes scrapy spider named with "IdentityIQ" and fastAPI to schedule spider using json API.
## Requirements
Python 3.10+

Works on Linux (Ubuntu)
## Install
### Set ScrapyD as a System Service
sudo nano /lib/systemd/system/scrapyd.service

<code>
  [Unit]
  
  Description=Scrapyd service
  
  After=network.target
  
  
  [Service]
  
  User=
  
  Group=
  
  WorkingDirectory=/any/directory/here
  
  ExecStart=/usr/local/bin/scrapyd
</code>

### Set FastAPI as a System Service
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
