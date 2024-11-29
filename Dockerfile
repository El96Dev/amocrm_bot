FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /amocrm_bot

COPY ./bot /amocrm_bot
COPY ./.env /amocrm_bot/.env

RUN pip install --no-cache-dir --upgrade -r /amocrm_bot/requirements.txt