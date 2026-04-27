# Telegram Keyword Alert Add-on

Home Assistant OS uzerinde calisan, Telegram kanallarini dinleyip belirlenen keyword'ler gecince Pushover bildirimi gonderen custom add-on.

## Dosyalar

- `config.json`: Add-on tanimi ve ayar semasi
- `Dockerfile`: Add-on image yapisi
- `run.sh`: Baslatma komutu
- `app.py`: Telegram dinleme ve Pushover bildirimi

## Kurulum

1. Bu klasoru Home Assistant cihazinda `/addons/local/telegram_keyword_alert` altina kopyala.
2. Home Assistant icinde Add-ons sayfasinda `Reload` yap.
3. `Telegram Keyword Alert` eklentisini ac.
4. `api_id`, `api_hash`, `phone_number`, `pushover_user_key`, `pushover_api_token` alanlarini doldur.
5. `keywords` alanina aramak istedigin kelimeleri ekle.
6. Ilk giriste `verification_code` alanini gecici olarak kullan.

## Notlar

- `verification_code` giris tamamlandiktan sonra bos birakilabilir.
- `keywords` ve `exclude_keywords` listeleri Home Assistant arayuzunden yonetilir.
- `seen_messages.json` ayni mesaja tekrar bildirim gitmesini engeller.
