ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --no-cache-dir telethon requests

COPY run.sh /run.sh
COPY app.py /app.py

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
