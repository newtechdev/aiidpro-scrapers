import time
import os

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from app.IdentityIQ.spiders.ident_iq import IdentIqSpider
from app.settings import get_settings

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


# user_id="123abc098xyz"
# username = "jbc895@gmail.com"
# password = "badcredit101"
# last_four_digits = "7733"

@app.get("/")
async def root():
    return { "message": "success", "model_version": "1.0.0" }


@app.post("/identity-iq")
async def predict(identity_iq_user: IdentityIqUser, bt: BackgroundTasks) -> str:
    print(identity_iq_user)

    current_time = time.time() * 1000
    # output_file_path = f"s3://{AWS_S3_BUCKET_NAME}/credit-reports/{identity_iq_user.user_id}/IdentityIQ/{current_time}_report.json"
    output_file_path = f"./scraper-output/{identity_iq_user.user_id}/IdentityIQ/{current_time}_report.json"

    feeds = { f'{output_file_path}': { 'format': 'json', 'encoding': 'utf8', 'store_empty': False, 'indent': 4, } }

    # settings = get_project_settings()
    settings = get_settings()
    settings["FEEDS"] = feeds

    # settings[ "FEEDS" ] = feeds
    # settings.setdefault("FEEDS", { }).update(feeds)

    print(settings)

    process = CrawlerProcess(settings)
    process.crawl(
            IdentIqSpider, user_id = identity_iq_user.user_id, http_user = identity_iq_user.username,
            http_pass = identity_iq_user.password, last_four_digits = identity_iq_user.last_four_digits
    )
    bt.add_task(process.start, stop_after_crawl = False)

    print("I'm here.")
    return "IDIQ Done!"
