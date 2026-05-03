# Telegram Keyword Alert Add-on

Home Assistant OS uzerinde calisan, Telegram kanallarini dinleyip belirlenen keyword'ler gecince Pushover bildirimi gonderen custom add-on.

## Kolay Kurulum

Bu repo, Home Assistant'a dogrudan repository URL olarak eklenebilecek sekilde hazirlandi.

Kullanacagin URL:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

## Home Assistant Icinde Kurulum

1. `Ayarlar` > `Eklentiler` sayfasina gir.
2. `Add-on Store` ekranini ac.
3. Sag ustteki 3 nokta menuden `Repositories` sec.
4. Su URL'yi ekle:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

5. Kaydet.
6. Add-on listesinde `Telegram Keyword Alert` gorunecek.
7. Eklentiyi ac ve `Install` et.
8. `api_id`, `api_hash`, `phone_number`, `pushover_user_key`, `pushover_api_token`, `channels`, `keywords` alanlarini doldur.
9. Ilk giriste `verification_code` alanini gecici olarak kullan.

## Kenar Cubugu Arayuzu

Surum `1.1.0` ile add-on icinde Home Assistant kenar cubugu icin durum ekrani eklendi.

1. Add-on'u `Start` et.
2. Add-on sayfasinda `Show in sidebar` secenegini ac.
3. Sol menude `Telegram Alert` gorunur.
4. Bu ekranda calisma durumu, kanal sayisi, keyword sayisi, son kontrol, bildirim sayisi, susturulan tekrarlar ve hata sayisi gorunur.

Hata sayisi yalnizca son 24 saati kapsar. 24 saatten eski hata kayitlari otomatik temizlenir.

## Repo Yapisi

Home Assistant'in repository olarak okuyacagi dosyalar:

- `repository.yaml`
- `telegram_keyword_alert/config.json`
- `telegram_keyword_alert/Dockerfile`
- `telegram_keyword_alert/run.sh`
- `telegram_keyword_alert/app.py`

## Belgeler

- Ayrintili yeniden kurulum kilavuzu: `REINSTALL_GUIDE_TR.md`
- Hizli ayar ozeti: `CONFIG_TEMPLATE.md`

## Notlar

- `verification_code` giris tamamlandiktan sonra bos birakilabilir.
- `keywords` ve `exclude_keywords` listeleri Home Assistant arayuzunden yonetilir.
- `seen_messages.json` ayni mesaja tekrar bildirim gitmesini engeller.
- `seen_deals.json` ayni gun icinde ayni keyword ve ayni fiyat icin tekrar bildirim gitmesini engeller.
