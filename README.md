# Telegram Keyword Alert Add-on

Home Assistant OS uzerinde calisan, Telegram kanallarini dinleyip belirlenen keyword'ler gecince Pushover bildirimi gonderen custom add-on.

## Repo Yapisi

Bu repo ana klasorunde su dosyalar bulunur:

- `config.json`
- `Dockerfile`
- `run.sh`
- `app.py`
- `README.md`
- `REINSTALL_GUIDE_TR.md`
- `CONFIG_TEMPLATE.md`

## Home Assistant'ta Nereye Konur

Repo'daki add-on dosyalari Home Assistant cihazinda su klasore konur:

```text
/addons/local/telegram_keyword_alert
```

Son gorunum su olmali:

- `/addons/local/telegram_keyword_alert/config.json`
- `/addons/local/telegram_keyword_alert/Dockerfile`
- `/addons/local/telegram_keyword_alert/run.sh`
- `/addons/local/telegram_keyword_alert/app.py`

## Kurulum Ozeti

1. Bu repo'daki `config.json`, `Dockerfile`, `run.sh` ve `app.py` dosyalarini al.
2. Home Assistant cihazinda `/addons/local/telegram_keyword_alert` klasorunu olustur.
3. Bu 4 dosyayi bu klasorun icine koy.
4. Home Assistant icinde `Add-ons` sayfasinda `Reload` yap.
5. `Telegram Keyword Alert` eklentisini ac ve `Install` et.
6. `api_id`, `api_hash`, `phone_number`, `pushover_user_key`, `pushover_api_token`, `channels`, `keywords` alanlarini doldur.
7. Ilk giriste `verification_code` alanini gecici olarak kullan.

## Belgeler

- Ayrintili yeniden kurulum kilavuzu: `REINSTALL_GUIDE_TR.md`
- Hizli ayar ozeti: `CONFIG_TEMPLATE.md`

## Notlar

- `verification_code` giris tamamlandiktan sonra bos birakilabilir.
- `keywords` ve `exclude_keywords` listeleri Home Assistant arayuzunden yonetilir.
- `seen_messages.json` ayni mesaja tekrar bildirim gitmesini engeller.
