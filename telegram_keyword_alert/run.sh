#!/usr/bin/with-contenv bashio

sed -i 's/PRICE_REGEX\.searchhtext/PRICE_REGEX.search(text/g' /app.py
exec /opt/venv/bin/python -u /app.py
