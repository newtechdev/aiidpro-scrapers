# AIIDpro Backend
## Overview
This project includes scrapy spider named with "IdentityIQ" and fastAPI to schedule spider using json API.
## Requirements
Python 3.10+

Works on Linux (Ubuntu)
## Install
### Clone Repository and install packages
<pre><code>git clone
cd app
pip install -r requirements.txt
</code></pre>
### Set ScrapyD as a System Service
<pre><code>sudo nano /lib/systemd/system/scrapyd.service</code></pre>
<p>Then copy-paste following</p>
<pre><code>[Unit]
Description=Scrapyd service
After=network.target
<br>
[Service]
User=&lt;YOUR-USER&gt;
Group=&lt;USER-GROUP&gt;
WorkingDirectory=/app
ExecStart=/usr/local/bin/scrapyd
<br>
[Install]
WantedBy=multi-user.target
</code></pre>
<p>Then enable service</p>
<pre><code>systemctl enable scrapyd.service
</code></pre>
<p>Then start service</p>
<pre><code>systemctl start scrapyd.service</code></pre>

### Deploy IdentityIQ scrapy project
<pre><code>scrapyd-deploy default</code></pre>

### Set FastAPI as a System Service
<pre><code>sudo nano /lib/systemd/system/aiidpro-backend.service</code></pre>
<p>Then copy-paste following</p>
<pre><code>[Unit]
Description=AIIDpro backend service
After=network.target
<br>
[Service]
User=&lt;YOUR-USER&gt;
Group=&lt;USER-GROUP&gt;
WorkingDirectory=/app
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 80
<br>
[Install]
WantedBy=multi-user.target
</code></pre>
<p>Then enable service</p>

### Thank you for reading...
<pre><code>systemctl enable aiidpro-backend.service
</code></pre>
<p>Then start service</p>
<pre><code>systemctl start aiidpro-backend.service</code></pre>
