git clone
cd app
python3 -m venv venv
pip install -r requirements.txt
nohup scrapyd &
scrapyd-deploy default
nohup uvicorn main:app --host 0.0.0.0 --port 80
