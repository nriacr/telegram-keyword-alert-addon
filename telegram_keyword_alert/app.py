import asyncio
import json
import os
import re
import time
from datetime import datetime
from html import escape

import requests
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

CONFIG_PATH = "/data/options.json"
SESSION_PATH = "/data/telegram_keyword_alert"
STATE_PATH = "/data/login_state.json"
SEEN_PATH = "/data/seen_messages.json"
SEEN_DEALS_PATH = "/data/seen_deals.json"
STATUS_PATH = "/data/status.json"
ERROR_EVENTS_PATH = "/data/error_events.json"
PRICE_REGEX = re.compile(r"((?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d{1,2})?)\s*(?:TL|â‚º)", re.IGNORECASE)
HEARTBEAT_INTERVAL_SECONDS = 3600
DASHBOARD_PORT = 8099
ERROR_RETENTION_SECONDS = 24 * 60 * 60
ALLOWED_DASHBOARD_CLIENTS = {"172.30.32.2", "127.0.0.1", "::1"}
ADDON_ID_CACHE = ""


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message):
    print(f"[{now_text()}] {message}")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_json_file(path, default_value):
    if not os.path.exists(path):
        return default_value
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


def get_default_status():
    return {
        "status": "BaÅŸlatÄ±lÄ±yor",
        "channels_count": 0,
        "keywords_count": 0,
        "notifications_sent": 0,
        "duplicates_suppressed": 0,
        "last_check": "",
        "last_notification": "",
        "last_error": "",
        "error_count_24h": 0,
    }


def update_status(**values):
    try:
        status = get_default_status()
        status.update(load_json_file(STATUS_PATH, {}))
        status.update(values)
        save_json_file(STATUS_PATH, status)
    except Exception as error:
        log(f"Durum dosyasÄ± yazÄ±lamadÄ±: {error}")


def prune_error_events(events):
    cutoff = time.time() - ERROR_RETENTION_SECONDS
    return [event for event in events if event.get("time", 0) >= cutoff]


def record_error(message):
    try:
        events = prune_error_events(load_json_file(ERROR_EVENTS_PATH, []))
        events.append({"time": time.time(), "message": str(message), "created_at": now_text()})
        save_json_file(ERROR_EVENTS_PATH, events)
        update_status(error_count_24h=len(events), last_error=str(message))
    except Exception as error:
        log(f"Hata kaydÄ± yazÄ±lamadÄ±: {error}")


def get_error_count_24h():
    events = prune_error_events(load_json_file(ERROR_EVENTS_PATH, []))
    save_json_file(ERROR_EVENTS_PATH, events)
    return len(events)


def get_addon_id():
    global ADDON_ID_CACHE

    if ADDON_ID_CACHE:
        return ADDON_ID_CACHE

    supervisor_token = os.environ.get("SUPERVISOR_TOKEN", "")
    if supervisor_token:
        try:
            response = requests.get(
                "http://supervisor/addons/self/info",
                headers={"Authorization": f"Bearer {supervisor_token}"},
                timeout=8,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            slug = data.get("hostname") or data.get("slug") or ""
            if slug:
                ADDON_ID_CACHE = slug.replace("-", "_")
                return ADDON_ID_CACHE
        except Exception as error:
            log(f"Add-on kimliÄŸi Supervisor API'den okunamadÄ±: {error}")

    hostname = os.environ.get("HOSTNAME", "")
    if "telegram" in hostname:
        ADDON_ID_CACHE = hostname.replace("-", "_")
        return ADDON_ID_CACHE

    ADDON_ID_CACHE = "telegram_keyword_alert"
    return ADDON_ID_CACHE


async def wait_forever(message):
    while True:
        log(message)
        update_status(last_check=now_text(), error_count_24h=get_error_count_24h())
        await asyncio.sleep(60)


async def heartbeat_loop():
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
        log("Kanal dinleme devam ediyor.")
        update_status(status="Ã‡alÄ±ÅŸÄ±yor", last_check=now_text(), error_count_24h=get_error_count_24h())


def normalize_text(value):
    return (value or "").strip().lower()


def normalize_price(value):
    raw = (value or "").strip()
    if not raw:
        return None

    if "." in raw and "," in raw:
        normalized = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        _, right = raw.rsplit(",", 1)
        normalized = raw.replace(",", ".") if len(right) == 2 else raw.replace(",", "")
    elif "." in raw:
        _, right = raw.rsplit(".", 1)
        normalized = raw if len(right) == 2 else raw.replace(".", "")
    else:
        normalized = raw

    return normalized


def extract_price(text):
    match = PRICE_REGEX.search(text or "")
    if not match:
        return None
    return normalize_price(match.group(1))


def build_daily_deal_key(keyword, price):
    if not keyword or not price:
        return None
    return f"{normalize_text(keyword)}|{price}"


def prune_seen_deals(seen_deals, today_key):
    return {key: value for key, value in seen_deals.items() if value == today_key}


def message_matches(text, keywords, exclude_keywords):
    normalized = normalize_text(text)

    if not normalized:
        return False, None

    for exclude_keyword in exclude_keywords:
        if normalize_text(exclude_keyword) in normalized:
            return False, None

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if normalized_keyword and normalized_keyword in normalized:
            return True, keyword

    return False, None


def send_pushover(user_key, api_token, title, message, url=""):
    payload = {
        "token": api_token,
        "user": user_key,
        "title": title,
        "message": message[:1024],
    }

    if url:
        payload["url"] = url
        payload["url_title"] = "Telegram'da aÃ§"

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data=payload,
        timeout=15,
    )
    response.raise_for_status()


def render_dashboard():
    status = get_default_status()
    status.update(load_json_file(STATUS_PATH, {}))
    status["error_count_24h"] = get_error_count_24h()

    status_label = status.get("status") or "Bilinmiyor"
    is_running = status_label.lower() == "Ã§alÄ±ÅŸÄ±yor"
    status_color = "#4ade80" if is_running else "#f59e0b"
    status_border = "#2f855a" if is_running else "#92400e"

    cards = [
        ("Durum", status_label, status_color, status_border),
        ("Telegram kanallarÄ±", status.get("channels_count", 0), "#f8fafc", "#303030"),
        ("Keyword sayÄ±sÄ±", status.get("keywords_count", 0), "#f8fafc", "#303030"),
        ("GÃ¶nderilen bildirim", status.get("notifications_sent", 0), "#f8fafc", "#303030"),
        ("Susturulan tekrar", status.get("duplicates_suppressed", 0), "#f8fafc", "#303030"),
        ("Son kontrol", status.get("last_check") or "-", "#f8fafc", "#303030"),
        ("Son bildirim", status.get("last_notification") or "-", "#f8fafc", "#303030"),
        ("Hata sayÄ±sÄ±", status.get("error_count_24h", 0), "#f8fafc", "#303030"),
    ]

    card_html = "\n".join(
        f"""
        <section class="card" style="border-color:{border}">
          <div class="label">{escape(str(label))}</div>
          <div class="value" style="color:{color}">{escape(str(value))}</div>
        </section>
        """
        for label, value, color, border in cards
    )

    last_error = escape(status.get("last_error") or "Son 24 saatte kayÄ±tlÄ± hata yok.")
    addon_id = escape(get_addon_id())

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="60">
  <title>Telegram Keyword Alert</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #101010;
      --panel: #191919;
      --card: #151515;
      --line: #303030;
      --text: #f4f4f5;
      --muted: #b7b7bb;
      --accent: #ff9f0a;
      --accent-soft: #3a2a1c;
      --blue: #229ed9;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      min-height: 100vh;
      padding: clamp(12px, 1.8vw, 24px);
      background:
        radial-gradient(circle at top left, rgba(34, 158, 217, .16), transparent 32rem),
        linear-gradient(135deg, #181818 0%, #111111 54%, #16120e 100%);
    }}
    .shell {{
      max-width: 980px;
      margin: 0 auto;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: rgba(25, 25, 25, .88);
      padding: clamp(18px, 2vw, 24px);
      box-shadow: 0 24px 80px rgba(0, 0, 0, .34);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 15px;
      border-radius: 999px;
      background: linear-gradient(135deg, #ff9f0a, #ffb340);
      color: #111;
      font-weight: 800;
      font-size: 13px;
    }}
    .badge span {{
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--blue);
      box-shadow: 0 0 0 4px rgba(34, 158, 217, .24);
    }}
    h1 {{
      margin: 22px 0 10px;
      font-size: clamp(24px, 2.4vw, 32px);
      line-height: 1.08;
      letter-spacing: 0;
    }}
    .lead {{
      margin: 0 0 20px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 20px;
    }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      padding: 0 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: transparent;
      color: var(--text);
      text-decoration: none;
      font-weight: 800;
      font-size: 13px;
      font-family: inherit;
      cursor: pointer;
    }}
    .button.primary {{
      background: linear-gradient(135deg, #ff9f0a, #ffc04d);
      color: #111;
      border: none;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .card {{
      min-height: 86px;
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px 16px;
      background: rgba(18, 18, 18, .84);
    }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 9px;
    }}
    .value {{
      font-size: clamp(18px, 1.6vw, 21px);
      line-height: 1.05;
      font-weight: 900;
      overflow-wrap: anywhere;
    }}
    .note {{
      margin-top: 18px;
      border-left: 6px solid var(--accent);
      border-radius: 12px;
      background: var(--accent-soft);
      padding: 12px 16px;
      color: #d4d4d8;
      font-size: 13px;
      line-height: 1.45;
    }}
    .foot {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 620px) {{
      main {{ padding: 12px; }}
      .shell {{ border-radius: 18px; padding: 16px; }}
      .grid {{ grid-template-columns: 1fr; }}
      h1 {{ margin-top: 20px; }}
      .button {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <main>
    <div class="shell">
      <div class="badge"><span></span> Telegram fÄ±rsat alarmÄ±</div>
      <h1>Telegram Keyword Alert</h1>
      <p class="lead">Bu sayfa Home Assistant kenar Ã§ubuÄŸu iÃ§in kÄ±sa durum ekranÄ±dÄ±r. Telegram kanal dinleme arka planda devam eder.</p>
      <div class="actions">
        <button class="button primary" type="button" onclick="openAddonPage('logs')">LOG</button>
        <button class="button" type="button" onclick="openAddonPage('config')">Config</button>
      </div>
      <div class="grid">{card_html}</div>
      <div class="note">Hata sayÄ±sÄ± yalnÄ±zca son 24 saati kapsar. 24 saatten eski hata kayÄ±tlarÄ± otomatik silinir.<br>Son hata: {last_error}</div>
      <div class="foot">Sayfa 60 saniyede bir otomatik yenilenir.</div>
    </div>
  </main>
  <script>
    const ADDON_ID = "{addon_id}";

    function openAddonPage(page) {{
      window.top.location.href = `/config/app/${{ADDON_ID}}/${{page}}`;
    }}
  </script>
</body>
</html>"""


async def handle_dashboard_client(reader, writer):
    try:
        peer = writer.get_extra_info("peername")
        peer_host = peer[0] if peer else ""
        if peer_host not in ALLOWED_DASHBOARD_CLIENTS:
            body = b"Forbidden"
            header = (
                "HTTP/1.1 403 Forbidden\r\n"
                "Content-Type: text/plain; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("utf-8")
            writer.write(header + body)
            await writer.drain()
            return

        request = await reader.read(4096)
        if not request:
            writer.close()
            await writer.wait_closed()
            return

        body = render_dashboard().encode("utf-8")
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Cache-Control: no-store\r\n"
            "Connection: close\r\n\r\n"
        ).encode("utf-8")
        writer.write(header + body)
        await writer.drain()
    except Exception as error:
        record_error(f"Dashboard hatasÄ±: {error}")
    finally:
        writer.close()
        await writer.wait_closed()


async def start_dashboard_server():
    try:
        server = await asyncio.start_server(handle_dashboard_client, "0.0.0.0", DASHBOARD_PORT)
        log(f"Sidebar arayÃ¼zÃ¼ {DASHBOARD_PORT} portunda baÅŸladÄ±.")
        async with server:
            await server.serve_forever()
    except Exception as error:
        log(f"Sidebar arayÃ¼zÃ¼ baÅŸlatÄ±lamadÄ±: {error}")
        record_error(f"Sidebar arayÃ¼zÃ¼ baÅŸlatÄ±lamadÄ±: {error}")


async def main():
    log("Telegram Keyword Alert add-on baÅŸladÄ±.")
    update_status(status="BaÅŸlatÄ±lÄ±yor", last_check=now_text(), error_count_24h=get_error_count_24h())
    asyncio.create_task(start_dashboard_server())

    try:
        config = load_config()
        log("YapÄ±landÄ±rma dosyasÄ± okundu.")
    except Exception as error:
        log(f"YapÄ±landÄ±rma okunamadÄ±: {error}")
        record_error(f"YapÄ±landÄ±rma okunamadÄ±: {error}")
        update_status(status="Hata", last_check=now_text())
        await wait_forever("YapÄ±landÄ±rma dÃ¼zeltmesi bekleniyor...")
        return

    api_id = config.get("api_id")
    api_hash = config.get("api_hash")
    phone_number = config.get("phone_number")
    verification_code = config.get("verification_code", "").strip()
    channels = config.get("channels", [])
    keywords = config.get("keywords", [])
    exclude_keywords = config.get("exclude_keywords", [])
    pushover_user_key = config.get("pushover_user_key", "").strip()
    pushover_api_token = config.get("pushover_api_token", "").strip()

    update_status(channels_count=len(channels), keywords_count=len(keywords), last_check=now_text())

    if not api_id or not api_hash or not phone_number:
        log("api_id, api_hash veya phone_number eksik.")
        record_error("api_id, api_hash veya phone_number eksik.")
        update_status(status="Hata", last_check=now_text())
        await wait_forever("Eksik ayarÄ±n tamamlanmasÄ± bekleniyor...")
        return

    if not pushover_user_key or not pushover_api_token:
        log("Pushover ayarlarÄ± eksik.")
        record_error("Pushover ayarlarÄ± eksik.")
        update_status(status="Hata", last_check=now_text())
        await wait_forever("Pushover ayarlarÄ± bekleniyor...")
        return

    log("Telegram baÄŸlantÄ±sÄ± baÅŸlatÄ±lÄ±yor...")

    client = TelegramClient(SESSION_PATH, int(api_id), api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        state = load_json_file(STATE_PATH, {})

        if not verification_code:
            log("Telegram giriÅŸi gerekiyor. Telefona bir kod gelecek.")
            result = await client.send_code_request(phone_number)
            state["phone_code_hash"] = result.phone_code_hash
            save_json_file(STATE_PATH, state)
            log("Kod gÃ¶nderildi. Home Assistant ayarlarÄ±nda verification_code alanÄ±na kodu yaz.")
            update_status(status="GiriÅŸ bekleniyor", last_check=now_text())
            await wait_forever("DoÄŸrulama kodu bekleniyor...")
            return

        phone_code_hash = state.get("phone_code_hash")
        if not phone_code_hash:
            log("phone_code_hash bulunamadÄ±. verification_code alanÄ±nÄ± boÅŸaltÄ±p tekrar kod isteyelim.")
            record_error("phone_code_hash bulunamadÄ±.")
            update_status(status="Hata", last_check=now_text())
            await wait_forever("DoÄŸrulama bilgisi bekleniyor...")
            return

        try:
            await client.sign_in(
                phone=phone_number,
                code=verification_code,
                phone_code_hash=phone_code_hash,
            )
            log("Kod ile giriÅŸ baÅŸarÄ±lÄ±.")
        except SessionPasswordNeededError:
            log("Ä°ki adÄ±mlÄ± doÄŸrulama ÅŸifresi gerekiyor. BunÔÍ½¹É…­¤…“Åµ‘„•­±•å•—}¥è¸ˆ¤(€€€€€€€€€€€É•½É‘}•ÉÉ½È ‹Á­¤…“Åµ³Ä‘¿}ÉÕ±…µ„ƒ}¥™É•Í¤•É•­¥å½È¸ˆ¤(€€€€€€€€€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡ÍÑ…ÑÕÌô‰!…Ñ„ˆ°±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤¤(€€€€€€€€€€€…İ…¥Ğİ…¥Ñ}™½É•Ù•È ˆÉƒ}¥™É•Í¤‰•­±•¹¥å½È¸¸¸ˆ¤(€€€€€€€€€€€É•ÑÕÉ¸(€€€€€€€•á•ÁĞá•ÁÑ¥½¸…Ì•ÉÉ½Èè(€€€€€€€€€€€±½œ¡˜‰¥É§|¡…Ñ…ÏÄèí•ÉÉ½Éôˆ¤(€€€€€€€€€€€É•½É‘}•ÉÉ½È¡˜‰¥É§|¡…Ñ…ÏÄèí•ÉÉ½Éôˆ¤(€€€€€€€€€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡ÍÑ…ÑÕÌô‰!…Ñ„ˆ°±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤¤(€€€€€€€€€€€…İ…¥Ğİ…¥Ñ}™½É•Ù•È ‰¥É§|“ñé•±Ñµ•Í¤‰•­±•¹¥å½È¸¸¸ˆ¤(€€€€€€€€€€€É•ÑÕÉ¸((€€€µ”€ô…İ…¥Ğ±¥•¹Ğ¹•Ñ}µ” ¤(€€€±½œ¡˜‰¥É§|å…ÃÅ±“Äèíµ”¹™¥ÉÍÑ}¹…µ•ôˆ¤(€€€±½œ¡˜‰-…¹…°Í…çÅÏÄèí±•¸¡¡…¹¹•±Ì¥ôˆ¤(€€€±½œ¡˜‰-•åİ½ÉÍ…çÅÏÄèí±•¸¡­•åİ½É‘Ì¥ôˆ¤(€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡ÍÑ…ÑÕÌô‹…³ÇÅå½Èˆ°¡…¹¹•±Í}½Õ¹Ğõ±•¸¡¡…¹¹•±Ì¤°­•åİ½É‘Í}½Õ¹Ğõ±•¸¡­•åİ½É‘Ì¤°±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤¤((€€€¥˜¹½Ğ¡…¹¹•±Ìè(€€€€€€€±½œ ‹Áé±•¹••¬­…¹…°å½¬¸ˆ¤(€€€€€€€É•½É‘}•ÉÉ½È ‹Áé±•¹••¬­…¹…°å½¬¸ˆ¤(€€€€€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡ÍÑ…ÑÕÌô‰!…Ñ„ˆ°±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤¤(€€€€€€€…İ…¥Ğİ…¥Ñ}™½É•Ù•È ‰-…¹…°±¥ÍÑ•Í¤‰•­±•¹¥å½È¸¸¸ˆ¤(€€€€€€€É•ÑÕÉ¸((€€€¥˜¹½Ğ­•åİ½É‘Ìè(€€€€€€€±½œ ‰-•åİ½É±¥ÍÑ•Í¤‰¿|¸ˆ¤(€€€€€€€É•½É‘}•ÉÉ½È ‰-•åİ½É±¥ÍÑ•Í¤‰¿|¸ˆ¤(€€€€€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡ÍÑ…ÑÕÌô‰!…Ñ„ˆ°±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤¤(€€€€€€€…İ…¥Ğİ…¥Ñ}™½É•Ù•È ‰-•åİ½É±¥ÍÑ•Í¤‰•­±•¹¥å½È¸¸¸ˆ¤(€€€€€€€É•ÑÕÉ¸((€€€Í••¹}µ•ÍÍ…•Ì€ôÍ•Ğ¡±½…‘}©Í½¹}™¥±”¡M9}AQ °mt¤¤(€€€Ñ½‘…å}­•ä€ô‘…Ñ•Ñ¥µ”¹¹½Ü ¤¹ÍÑÉ™Ñ¥µ” ˆ•d´•´´•ˆ¤(€€€Í••¹}‘•…±Ì€ôÁÉÕ¹•}Í••¹}‘•…±Ì¡±½…‘}©Í½¹}™¥±”¡M9}1M}AQ °íô¤°Ñ½‘…å}­•ä¤(€€€Í••¹}‘•…±Í}±½¬€ô…Íå¹¥¼¹1½¬ ¤(€€€Í…Ù•}©Í½¹}™¥±”¡M9}1M}AQ °Í••¹}‘•…±Ì¤((€€€±¥•¹Ğ¹½¸¡•Ù•¹ÑÌ¹9•İ5•ÍÍ…”¡¡…ÑÌõ¡…¹¹•±Ì¤¤(€€€…Íå¹Œ‘•˜¡…¹‘±•}¹•İ}µ•ÍÍ…”¡•Ù•¹Ğ¤è(€€€€€€€ÑÉäè(€€€€€€€€€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡ÍÑ…ÑÕÌô‹…³ÇÅå½Èˆ°±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤°•ÉÉ½É}½Õ¹Ñ|ÈÑ õ•Ñ}•ÉÉ½É}½Õ¹Ñ|ÈÑ  ¤¤(€€€€€€€€€€€µ•ÍÍ…•}Ñ•áĞ€ô•Ù•¹Ğ¹É…İ}Ñ•áĞ½È€ˆˆ(€€€€€€€€€€€µ…Ñ¡•°µ…Ñ¡•‘}­•åİ½É€ôµ•ÍÍ…•}µ…Ñ¡•Ì (€€€€€€€€€€€€€€€µ•ÍÍ…•}Ñ•áĞ°(€€€€€€€€€€€€€€€­•åİ½É‘Ì°(€€€€€€€€€€€€€€€•á±Õ‘•}­•åİ½É‘Ì°(€€€€€€€€€€€€¤((€€€€€€€€€€€¥˜¹½Ğµ…Ñ¡•è(€€€€€€€€€€€€€€€É•ÑÕÉ¸((€€€€€€€€€€€µ•ÍÍ…•}­•ä€ô˜‰í•Ù•¹Ğ¹¡…Ñ}¥‘ôéí•Ù•¹Ğ¹¥‘ôˆ(€€€€€€€€€€€ÁÉ¥”€ô•áÑÉ…Ñ}ÁÉ¥”¡µ•ÍÍ…•}Ñ•áĞ¤(€€€€€€€€€€€‘•…±}­•ä€ô‰Õ¥±‘}‘…¥±å}‘•…±}­•ä¡µ…Ñ¡•‘}­•åİ½É°ÁÉ¥”¤(€€€€€€€€€€€ÕÉÉ•¹Ñ}‘…ä€ô‘…Ñ•Ñ¥µ”¹¹½Ü ¤¹ÍÑÉ™Ñ¥µ” ˆ•d´•´´•ˆ¤((€€€€€€€€€€€…Íå¹Œİ¥Ñ Í••¹}‘•…±Í}±½¬è(€€€€€€€€€€€€€€€¥˜µ•ÍÍ…•}­•ä¥¸Í••¹}µ•ÍÍ…•Ìè(€€€€€€€€€€€€€€€€€€€É•ÑÕÉ¸((€€€€€€€€€€€€€€€¥˜‘•…±}­•ä…¹Í••¹}‘•…±Ì¹•Ğ¡‘•…±}­•ä¤€ôôÕÉÉ•¹Ñ}‘…äè(€€€€€€€€€€€€€€€€€€€±½œ¡˜‰å»ÄŸñ¸§¥¹‘”…å»Ä™¥å…Ñ³Ä›ÅÉÍ…ĞÍÕÍÑÕÉÕ±‘Ô¸-•åİ½Éèíµ…Ñ¡•‘}­•åİ½É‘ô¥å…ĞèíÁÉ¥•ôˆ¤(€€€€€€€€€€€€€€€€€€€Í••¹}µ•ÍÍ…•Ì¹…‘¡µ•ÍÍ…•}­•ä¤(€€€€€€€€€€€€€€€€€€€Í…Ù•}©Í½¹}™¥±”¡M9}AQ °±¥ÍĞ¡Í••¹}µ•ÍÍ…•Ì¤¤(€€€€€€€€€€€€€€€€€€€ÍÑ…ÑÕÌ€ô±½…‘}©Í½¹}™¥±”¡MQQUM}AQ °íô¤(€€€€€€€€€€€€€€€€€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡‘ÕÁ±¥…Ñ•Í}ÍÕÁÁÉ•ÍÍ•õ¥¹Ğ¡ÍÑ…ÑÕÌ¹•Ğ ‰‘ÕÁ±¥…Ñ•Í}ÍÕÁÁÉ•ÍÍ•ˆ°€À¤¤€¬€Ä¤(€€€€€€€€€€€€€€€€€€€É•ÑÕÉ¸((€€€€€€€€€€€€€€€Í••¹}µ•ÍÍ…•Ì¹…‘¡µ•ÍÍ…•}­•ä¤(€€€€€€€€€€€€€€€Í…Ù•}©Í½¹}™¥±”¡M9}AQ °±¥ÍĞ¡Í••¹}µ•ÍÍ…•Ì¤¤((€€€€€€€€€€€€€€€¥˜‘•…±}­•äè(€€€€€€€€€€€€€€€€€€€Í••¹}‘•…±Ím‘•…±}­•åt€ôÕÉÉ•¹Ñ}‘…ä(€€€€€€€€€€€€€€€€€€€Í…Ù•}©Í½¹}™¥±”¡M9}1M}AQ °Í••¹}‘•…±Ì¤((€€€€€€€€€€€¡…Ğ€ô…İ…¥Ğ•Ù•¹Ğ¹•Ñ}¡…Ğ ¤(€€€€€€€€€€€¡…¹¹•±}¹…µ”€ô•Ñ…ÑÑÈ¡¡…Ğ°€‰Ñ¥Ñ±”ˆ°9½¹”¤½È•Ñ…ÑÑÈ¡¡…Ğ°€‰ÕÍ•É¹…µ”ˆ°9½¹”¤½È€‰Q•±•É…´ˆ((€€€€€€€€€€€µ•ÍÍ…•}±¥¹¬€ô€ˆˆ(€€€€€€€€€€€ÕÍ•É¹…µ”€ô•Ñ…ÑÑÈ¡¡…Ğ°€‰ÕÍ•É¹…µ”ˆ°9½¹”¤(€€€€€€€€€€€¥˜ÕÍ•É¹…µ”è(€€€€€€€€€€€€€€€µ•ÍÍ…•}±¥¹¬€ô˜‰¡ÑÑÁÌè¼½Ğ¹µ”½íÕÍ•É¹…µ•ô½í•Ù•¹Ğ¹¥‘ôˆ((€€€€€€€€€€€Í¡½ÉÑ}Ñ•áĞ€ôµ•ÍÍ…•}Ñ•áĞ¹É•Á±…” ‰q¸ˆ°€ˆ€ˆ¤¹ÍÑÉ¥À ¤(€€€€€€€€€€€¥˜±•¸¡Í¡½ÉÑ}Ñ•áĞ¤€ø€ÌÀÀè(€€€€€€€€€€€€€€€Í¡½ÉÑ}Ñ•áĞ€ôÍ¡½ÉÑ}Ñ•áÑlèÌÀÁt€¬€ˆ¸¸¸ˆ((€€€€€€€€€€€Ñ¥Ñ±”€ô˜‰ÅÉÍ…Ğ…±…É·Äèíµ…Ñ¡•‘}­•åİ½É‘ôˆ(€€€€€€€€€€€‰½‘ä€ô˜‰-…¹…°èí¡…¹¹•±}¹…µ•õq¹q¹íÍ¡½ÉÑ}Ñ•áÑôˆ((€€€€€€€€€€€Í•¹‘}ÁÕÍ¡½Ù•È (€€€€€€€€€€€€€€€ÁÕÍ¡½Ù•É}ÕÍ•É}­•ä°(€€€€€€€€€€€€€€€ÁÕÍ¡½Ù•É}…Á¥}Ñ½­•¸°(€€€€€€€€€€€€€€€Ñ¥Ñ±”°(€€€€€€€€€€€€€€€‰½‘ä°(€€€€€€€€€€€€€€€µ•ÍÍ…•}±¥¹¬°(€€€€€€€€€€€€¤((€€€€€€€€€€€ÍÑ…ÑÕÌ€ô±½…‘}©Í½¹}™¥±”¡MQQUM}AQ °íô¤(€€€€€€€€€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ (€€€€€€€€€€€€€€€¹½Ñ¥™¥…Ñ¥½¹Í}Í•¹Ğõ¥¹Ğ¡ÍÑ…ÑÕÌ¹•Ğ ‰¹½Ñ¥™¥…Ñ¥½¹Í}Í•¹Ğˆ°€À¤¤€¬€Ä°(€€€€€€€€€€€€€€€±…ÍÑ}¹½Ñ¥™¥…Ñ¥½¸õ¹½İ}Ñ•áĞ ¤°(€€€€€€€€€€€€€€€±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤°(€€€€€€€€€€€€¤(€€€€€€€€€€€±½œ¡˜‰	¥±‘¥É¥´ŸÙ¹‘•É¥±‘¤¸-…¹…°èí¡…¹¹•±}¹…µ•ô-•åİ½Éèíµ…Ñ¡•‘}­•åİ½É‘ô¥å…ĞèíÁÉ¥”½È€å½¬ôˆ¤(€€€€€€€•á•ÁĞá•ÁÑ¥½¸…Ì•ÉÉ½Èè(€€€€€€€€€€€±½œ¡˜‰5•Í…¨§}±•µ”¡…Ñ…ÏÄèí•ÉÉ½Éôˆ¤(€€€€€€€€€€€É•½É‘}•ÉÉ½È¡˜‰5•Í…¨§}±•µ”¡…Ñ…ÏÄèí•ÉÉ½Éôˆ¤((€€€±½œ ‰-…¹…°‘¥¹±•µ”‰‡}±…“Ä¸ˆ¤(€€€ÕÁ‘…Ñ•}ÍÑ…ÑÕÌ¡ÍÑ…ÑÕÌô‹…³ÇÅå½Èˆ°±…ÍÑ}¡•¬õ¹½İ}Ñ•áĞ ¤°•ÉÉ½É}½Õ¹Ñ|ÈÑ õ•Ñ}•ÉÉ½É}½Õ¹Ñ|ÈÑ  ¤¤(€€€…Íå¹¥¼¹É•…Ñ•}Ñ…Í¬¡¡•…ÉÑ‰•…Ñ}±½½À ¤¤(€€€…İ…¥Ğ±¥•¹Ğ¹ÉÕ¹}Õ¹Ñ¥±}‘¥Í½¹¹•Ñ• ¤(()…Íå¹¥¼¹ÉÕ¸¡µ…¥¸ ¤¤(