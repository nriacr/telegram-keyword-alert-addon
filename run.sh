#!/usr/bin/with-contenv bashio

sed -i 's/PRICE_REGEX\.searchhtext/PRICE_REGEX.search(text/g' /app.py
sed -i 's/slug = data.get("slug") or data.get("hostname") or ""/slug = data.get("hostname") or data.get("slug") or ""/' /app.py
exec /opt/venv/bin/python -u /app.py
