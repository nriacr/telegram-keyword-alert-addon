import asyncio
import json
import os
import re
from datetime import datetime

import requests
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

CONFIG_PATH = "/data/options.json"
SESSION_PATH = "/data/telegram_keyword_alert"
STATE_PATH = "/data/login_state.json"
SEEN_PATH = "/data/seen_messages.json"
SEEN_DEALS_PATH = "/data/seen_deals.json"
PRICE_REGEX = re.compile(r"((?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d{1,2})?)\s*(?:TL|₺)", re.IGNORECASE)
HEARTBEAT_INTERVAL_SECONDS = 3600


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


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


async def wait_forever(message):
    while True:
        log(message)
        await asyncio.sleep(60)


async def heartbeat_loop():
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
        log("Kanal dinleme devam ediyor.")


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
        payload["url_title"] = "Telegram'da ac"

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data=payload,
        timeout=15,
    )
    response.raise_for_status()


async def main():
    log("Telegram Keyword Alert add-on basladi.")

    try:
        config = load_config()
        log("Yapilandirma dosyasi okundu.")
    except Exception as error:
        log(f"Yapilandirma okunamadi: {error}")
        await wait_forever("Yapilandirma duzeltmesi bekleniyor...")
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

    if not api_id or not api_hash or not phone_number:
        log("api_id, api_hash veya phone_number eksik.")
        await wait_forever("Eksik ayar tamamlanmasi bekleniyor...")
        return

    if not pushover_user_key or not pushover_api_token:
        log("Pushover ayarlari eksik.")
        await wait_forever("Pushover ayarlari bekleniyor...")
        return

    log("Telegram baglantisi baslatiliyor...")

    client = TelegramClient(SESSION_PATH, int(api_id), api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        state = load_json_file(STATE_PATH, {})

        if not verification_code:
            log("Telegram girisi gerekiyor. Telefona bir kod gelecek.")
            result = await client.send_code_request(phone_number)
            state["phone_code_hash"] = result.phone_code_hash
            save_json_file(STATE_PATH, state)
            log("Kod gonderildi. Home Assistant ayarlarinda verification_code alanina kodu yaz.")
            await wait_forever("Dogrulama kodu bekleniyor...")
            return

        phone_code_hash = state.get("phone_code_hash")
        if not phone_code_hash:
            log("phone_code_hash bulunamadi. verification_code alanini bosaltip tekrar kod isteyelim.")
            await wait_forever("Dogrulama bilgisi bekleniyor...")
            return

        try:
            await client.sign_in(
                phone=phone_number,
                code=verification_code,
                phone_code_hash=phone_code_hash,
            )
            log("Kod ile giris basarili.")
        except SessionPasswordNeededError:
            log("Iki adimli dogrulama sifresi gerekiyor. Bunu sonraki adimda ekleyecegiz.")
            await wait_forever("2FA sifresi bekleniyor...")
            return
        except Exception as error:
            log(f"Giris hatasi: {error}")
            await wait_forever("Giris duzeltmesi bekleniyor...")
            return

    me = await client.get_me()
    log(f"Giris yapildi: {me.first_name}")
    log(f"Kanal sayisi: {len(channels)}")
    log(f"Keyword sayisi: {len(keywords)}")

    if not channels:
        log("Izlenecek kanal yok.")
        await wait_forever("Kanal listesi bekleniyor...")
        return

    if not keywords:
        log("Keyword listesi bos.")
        await wait_forever("Keyword listesi bekleniyor...")
        return

    seen_messages = set(load_json_file(SEEN_PATH, []))
    today_key = datetime.now().strftime("%Y-%m-%d")
    seen_deals = prune_seen_deals(load_json_file(SEEN_DEALS_PATH, {}), today_key)
    save_json_file(SEEN_DEALS_PATH, seen_deals)

    @client.on(events.NewMessage(chats=channels))
    async def handle_new_message(event):
        try:
            message_text = event.raw_text or ""
            matched, matched_keyword = message_matches(
                message_text,
                keywords,
                exclude_keywords,
            )

            if not matched:
                return

            message_key = f"{event.chat_id}:{event.id}"
            if message_key in seen_messages:
                return

            price = extract_price(message_text)
            deal_key = build_daily_deal_key(matched_keyword, price)
            current_day = datetime.now().strftime("%Y-%m-%d")

            if deal_key and seen_deals.get(deal_key) == current_day:
                log(f"Ayni gun icinde ayni fiyatli firsat susturuldu. Keyword: {matched_keyword} Fiyat: {price}")
                seen_messages.add(message_key)
                save_json_file(SEEN_PATH, list(seen_messages))
                return

            seen_messages.add(message_key)
            save_json_file(SEEN_PATH, list(seen_messages))

            chat = await event.get_chat()
            channel_name = getattr(chat, "title", None) or getattr(chat, "username", None) or "Telegram"

            message_link = ""
            username = getattr(chat, "username", None)
            if username:
                message_link = f"https://t.me/{username}/{event.id}"

            short_text = message_text.replace("\n", " ").strip()
            if len(short_text) > 300:
                short_text = short_text[:300] + "..."

            title = f"Firsat alarmi: {matched_keyword}"
            body = f"Kanal: {channel_name}\n\n{short_text}"

            send_pushover(
                pushover_user_key,
                pushover_api_token,
                title,
                body,
                message_link,
            )

            if deal_key:
                seen_deals[deal_key] = current_day
                save_json_file(SEEN_DEALS_PATH, seen_deals)

            log(f"Bildirim gonderildi. Kanal: {channel_name} Keyword: {matched_keyword} Fiyat: {price or 'yok'}")
        except Exception as error:
            log(f"Mesaj isleme hatasi: {error}")

    log("Kanal dinleme basladi.")
    asyncio.create_task(heartbeat_loop())
    await client.run_until_disconnected()


asyncio.run(main())
