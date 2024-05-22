import time
import os
import json

from scrapyd_api import ScrapydAPI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

scrapyd = ScrapydAPI('http://localhost:6800')

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")

print(AWS_ACCESS_KEY_ID)
print(AWS_SECRET_ACCESS_KEY)
print(AWS_S3_BUCKET_NAME)
print(AWS_REGION_NAME)

class IdentityIqUser(BaseModel):
    user_id: str
    username: str
    password: str
    last_four_digits: str


app = FastAPI()

@app.get("/")
async def root():
    return { "message": "success", "model_version": "1.0.0" }


@app.post("/identity-iq")
async def predict(identity_iq_user: IdentityIqUser) -> str:
    print(identity_iq_user)

    current_time = time.time() * 1000
    output_file_path = f"s3://{AWS_S3_BUCKET_NAME}/credit-reports/{identity_iq_user.user_id}/IdentityIQ/{current_time}_report.json"
    # output_file_path = f"./scraper-output/{identity_iq_user.user_id}/IdentityIQ/{current_time}_report.json"

    feeds = { f'{output_file_path}': { 'format': 'json', 'encoding': 'utf8', 'store_empty': False, 'indent': 4, } }
    settings = {
        "FEEDS": json.dumps(feeds),
    	"AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
	    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY
    }
    
    job_id = scrapyd.schedule('IdentityIQ', 'ident_iq', settings = settings, user_id = identity_iq_user.user_id, http_user = identity_iq_user.username, http_pass = identity_iq_user.password, last_four_digits = identity_iq_user.last_four_digits)

    print(f'Scheduled job with ID: {job_id}')
    return f'IDIQ Done! Scheduled job with ID: {job_id}'
