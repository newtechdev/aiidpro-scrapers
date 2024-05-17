FROM tiangolo/uvicorn-gunicorn:python3.11

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN playwright install chromium

COPY ./app /app/app

EXPOSE 80