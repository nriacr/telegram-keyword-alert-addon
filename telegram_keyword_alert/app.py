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
PRICE_REGEX = re.compile(r"((?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d{1,2})?)\s*(?:TL|₺)", re.IGNORECASE)
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
        json.dump(data, file)


def get_default_status():
    return {
        "status": "Başlatılıyor",
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
        log(f"Durum dosyası yazılamadı: {error}")


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
        log(f"Hata kaydı yazılamadı: {error}")


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
            slug = data.get("slug") or data.get("hostname") or ""
            if slug:
                ADDON_ID_CACHE = slug.replace("-", "_")
                return ADDON_ID_CACHE
        except Exception as error:
            log(f"Add-on kimliği Supervisor API'den okunamadı: {error}")

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
        update_status(status="Çalışıyor", last_check=now_text(), error_count_24h=get_error_count_24h())


def normalize_text(value):
    return (value or "").strip().lower()


def normalize_price(value):
    raw = (value or "").strip()
    if not raw:
        return None

    if "." in raw and "," in raw:
        normalized = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        left, right = raw.rsplit(",", 1)
        normalized = raw.replace(",", ".") if len(right) == 2 else raw.replace(",", "")
    elif "." in raw:
        left, right = raw.rsplit(".", 1)
        normalized = raw if len(right) == 2 else raw.replace(".", "")
    else:
        normalized = raw

    return normalized


def extract_price(text):
    match = PRICE_REGEX.searchhtext or "")
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
        payload["url_title"] = "Telegram'da aç"

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
    is_running = status_label.lower() == "çalışıyor"
    status_color = "#4ade80" if is_running else "#f59e0b"
    status_border = "#2f855a" if is_running else "#92400e"

    cards = [
        ("Durum", status_label, status_color, status_border),
        ("Telegram kanalları", status.get("channels_count", 0), "#f8fafc", "#303030"),
        ("Keyword sayısı", status.get("keywords_count", 0), "#f8fafc", "#303030"),
        ("Gönderilen bildirim", status.get("notifications_sent", 0), "#f8fafc", "#303030"),
        ("Susturulan tekrar", status.get("duplicates_suppressed", 0), "#f8fafc", "#303030"),
        ("Son kontrol", status.get("last_check") or "-", "#f8fafc", "#303030"),
        ("Son bildirim", status.get("last_notification") or "-", "#f8fafc", "#303030"),
        ("Hata sayısı", status.get("error_count_24h", 0), "#f8fafc", "#303030"),
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

    last_error = escape(status.get("last_error") or "Son 24 saatte kayıtlı hata yok.")
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
      <div class="badge"><span></span> Telegram fırsat alarmı</div>
      <h1>Telegram Keyword Alert</h1>
      <p class="lead">Bu sayfa Home Assistant kenar çubuğu için kısa durum ekranıdır. Telegram kanal dinleme arka planda devam eder.</p>
      <div class="actions">
        <button class="button primary" type="button" onclick="openAddonPage('logs')">Kayıtları Aç</button>
        <button class="button" type="button" onclick="openAddonPage('info')">Add-on Sayfasını Aç</button>
      </div>
      <div class="grid">{card_html}</div>
      <div class="note">Hata sayısı yalnızca son 24 saati kapsar. 24 saatten eski hata kayıtları otomatik silinir.<br>Son hata: {last_error}</div>
      <div class="foot">Sayfa 60 saniyede bir otomatik yenilenir.</div>
    </div>
  </main>
  <script>
    const ADDON_ID = "{addon_id}";

    function openAddonPage(page) {{
      window.top.location.href = `/hassio/addon/${{ADDON_ID}}/${{page}}`;
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
        record_error(f"Dashboard hatasi: {error}")
    finally:
        writer.close()
        await writer.wait_closed()


async def start_dashboard_server():
    try:
        server = await asyncio.start_server(handle_dashboard_client, "0.0.0.0", DASHBOARD_PORT)
        log(f"Sidebar arayüzü {DASHBOARD_PORT} portunda başladı.")
        async with server:
            await server.serve_forever()
    except Exception as error:
        log(f"Sidebar arayüzü başlatılamadı: {error}")
        record_error(f"Sidebar arayüzü başlatılamadı: {error}")


async def main():
    log("Telegram Keyword Alert add-on başladı.")
    update_status(status="Başlatılıyor", last_check=now_text(), error_count_24h=get_error_count_24h())
    asyncio.create_task(start_dashboard_server())

    try:
        config = load_config()
        log("Yapılandırma dosyası okundu.")
    except Exception as error:
        log(f"Yapılandırma okunamadı: {error}")
        record_error(f"Yapılandırma okunamadı: {error}")
        update_status(status="Hata", last_check=now_text())
        await wait_forever("Yapılandırma düzeltmesi bekleniyor...")
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
        await wait_forever("Eksik ayarın tamamlanması bekleniyor...")
        return

    if not pushover_user_key or not pushover_api_token:
        log("Pushover ayarları eksik.")
        record_error("Pushover ayarları eksik.")
        update_status(status="Hata", last_check=now_text())
        await wait_forever("Pushover ayarları bekleniyor...")
        return

    log("Telegram bağlantısı başlatılıyor...")

    client = TelegramClient(SESSION_PATH, int(api_id), api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        state = load_json_file(STATE_PATH, {})

        if not verification_code:
            log("Telegram girişi gerekiyor. Telefona bir kod gelecek.")
            result = await client.send_code_request(phone_number)
            state["phone_code_hash"] = result.phone_code_hash
            save_json_file(STATE_PATH, state)
            log("Kod gönderildi. Home Assistant ayarlarında verification_code alanına kodu yaz.")
            update_status(status="Giriş bekleniyor", last_check=now_text())
            await wait_forever("Doğrulama kodu bekleniyor...")
            return

        phone_code_hash = state.get("phone_code_hash")
        if not phone_code_hash:
            log("phone_code_hash bulunamadı. verification_code alanını boşaltıp tekrar kod isteyelim.")
            record_error("phone_code_hash bulunamadı.")
            update_status(status="Hata", last_check=now_text())
            await wait_forever("Doğrulama bilgisi bekleniyor...")
            return

        try:
            await client.sign_in(
                phone=phone_number,
                code=verification_code,
                phone_code_hash=phone_code_hash,
            )
            log("Kod ile giriş başarılı.")
        except SessionPasswordNeededError:
            log("İki adımlı doğrulama şifresi gerekiyor. Bunu sonraki adımda ekleyeceğiz.")
            record_error("İki adımlı doğrulama şifresi gerekiyor.")
            update_status(status="Hata", last_check=now_text())
            await wait_forever("2FA şifresi bekleniyor...")
            return
        except Exception as error:
            log(f"Giriş hatası: {error}")
            record_error(f"Giriş hatası: {error}")
            update_status(status="Hata", last_check=now_text())
            await wait_forever("Giriş düzeltmesi bekleniyor...")
            return

    me = await client.get_me()
    log(f"Giriş yapıldı: {me.first_name}")
    log(f"Kanal sayısı: {len(channels)}")
    log(f"Keyword sayısı: {len(keywords)}")
    update_status(status="Çalışıyor", channels_count=len(channels), keywords_count=len(keywords), last_check=now_text())

    if not channels:
        log("İzlenecek kanal yok.")
        record_error("İzlenecek kanal yok.")
        update_status(status="Hata", last_check=now_text())
        await wait_forever("Kanal listesi bekleniyor...")
        return

    if not keywords:
        log("Keyword listesi boş.")
        record_error("Keyword listesi boş.")
        update_status(status="Hata", last_check=now_text())
        await wait_forever("Keyword listesi bekleniyor...")
        return

    seen_messages = set(load_json_file(SEEN_PATH, []))
    today_key = datetime.now().strftime("%Y-%m-%d")
    seen_deals = prune_seen_deals(load_json_file(SEEN_DEALS_PATH, {}), today_key)
    seen_deals_lock = asyncio.Lock()
    save_json_file(SEEN_DEALS_PATH, seen_deals)

    @client.on(events.NewMessage(chats=channels))
    async def handle_new_message(event):
        try:
            update_status(status="Çalışıyor", last_check=now_text(), error_count_24h=get_error_count_24h())
            message_text = event.raw_text or ""
            matched, matched_keyword = message_matches(
                message_text,
                keywords,
                exclude_keywords,
            )

            if not matched:
                return

            message_key = f"{event.chat_id}:{event.id}"
            price = extract_price(message_text)
            deal_key = build_daily_deal_key(matched_keyword, price)
            current_day = datetime.now().strftime("%Y-%m-%d")

            async with seen_deals_lock:
                if message_key in seen_messages:
                    return

                if deal_key and seen_deals.get(deal_key) == current_day:
                    log(f"Aynı gün içinde aynı fiyatlı fırsat susturuldu. Keyword: {matched_keyword} Fiyat: {price}")
                    seen_messages.add(message_key)
                    save_json_file(SEEN_PATH, list(seen_messages))
                    status = load_json_file(STATUS_PATH, {})
                    update_status(duplicates_suppressed=int(status.get("duplicates_suppressed", 0)) + 1)
                    return

                seen_messages.add(message_key)
                save_json_file(SEEN_PATH, list(seen_messages))

                if deal_key:
                    seen_deals[deal_key] = current_day
                    save_json_file(SEEN_DEALS_PATH, seen_deals)

            chat = await event.get_chat()
            channel_name = getattr(chat, "title", None) or getattr(chat, "username", None) or "Telegram"

            message_link = ""
            username = getattr(chat, "username", None)
            if username:
                message_link = f"https://t.me/{username}/{event.id}"

            short_text = message_text.replace("\n", " ").strip()
            if len(short_text) > 300:
                short_text = short_text[:300] + "..."

            title = f"Fırsat alarmı: {matched_keyword}"
            body = f"Kanal: {channel_name}\n\n{short_text}"

            send_pushover(
                pushover_user_key,
                pushover_api_token,
                title,
                body,
                message_link,
            )

            status = load_json_file(STATUS_PATH, {})
            update_status(
                notifications_sent=int(status.get("notifications_sent", 0)) + 1,
                last_notification=now_text(),
                last_check=now_text(),
            )
            log(f"Bildirim gönderildi. Kanal: {channel_name} Keyword: {matched_keyword} Fiyat: {price or 'yok'}")
        except Exception as error:
            log(f"Mesaj işleme hatası: {error}")
            record_error(f"Mesaj işleme hatası: {error}")

    log("Kanal dinleme başladı.")
    update_status(status="Çalışıyor", last_check=now_text(), error_count_24h=get_error_count_24h())
    asyncio.create_task(heartbeat_loop())
    await client.run_until_disconnected()


asyncio.run(main())
