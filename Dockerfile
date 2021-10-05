# Synobot Docker build
# docker build -t synobot:0.13 .

FROM python:3.9.6-buster
MAINTAINER Acidpop <https://github.com/acidpop>

WORKDIR /synobot

ENV TG_NOTY_ID 12345678,87654321
ENV TG_BOT_TOKEN 186547547:AAEXOA9ld1tlsJXvEVBt4MZYq3bHA1EsJow
ENV TG_VALID_USER 12345678,87654321
ENV TG_DSM_PW_ID 12345678
ENV DSM_ID your_dsm_id
#ENV DSM_PW your_dsm_password
ENV LOG_MAX_SIZE 50
ENV LOG_COUNT 5
ENV DSM_URL https://DSM_IP_OR_URL
ENV DS_PORT 8000
ENV DSM_CERT 1
ENV DSM_RETRY_LOGIN 10
ENV DSM_AUTO_DEL 0
ENV TG_LANG ko_kr
ENV DSM_WATCH torrent_watch_path
ENV DSM_PW=""
ENV DSM_OTP_SECRET=""
ENV TZ Asia/Seoul
ENV DOCKER_LOG 1

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#RUN apt-get python3-dev libffi-dev gcc && pip3 install --upgrade pip 
RUN apt-get update && apt-get install -y libffi-dev gcc

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./*.py ./
COPY ./*.json ./

CMD [ "python", "./main.py" ]

