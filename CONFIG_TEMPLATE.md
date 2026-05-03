# Configuration Template

Home Assistant add-on ayar ekranina girerken kullanman icin kisa bir referans.

## Doldurulacak Alanlar

### Telegram

- `api_id`: `my.telegram.org` uzerinden alinir
- `api_hash`: `my.telegram.org` uzerinden alinir
- `phone_number`: `+905xxxxxxxxx`
- `verification_code`: sadece ilk giriste gecici olarak kullan

### Pushover

- `pushover_user_key`: Pushover hesabindaki `Your User Key`
- `pushover_api_token`: olusturdugun uygulamanin `API Token/Key`

### Kanallar

Su listeyi istersen dogrudan yeniden gir:

```text
@yaniyocom
@firsatz
@onual_firsat
@onual_ekstra
@butcedostu
@depoindirim
@uygunfiyatdedektifi
@tasarrufluharca
@depourunleri
@evEkonomi
@firsatavi
```

### Keyword Ornegi

```text
iphone 16
airpods
dyson
ps5
```

### Exclude Keyword Ornegi

```text
cekilis
yorum yap
```

## Kurulum Sirasi

1. `Ayarlar` > `Eklentiler` > `Add-on Store` ekranina gir.
2. Sag ustteki 3 nokta menuden `Repositories` sec.
3. Su URL'yi ekle: `https://github.com/nriacr/telegram-keyword-alert-addon`
4. `Telegram Keyword Alert` eklentisini bulup `Install` et.
5. Alanlari doldur ve `Save` de.
6. `Start` et.
7. Telegram'dan gelen kodu `verification_code` alanina gir.
8. `Restart` et.
9. Basarili giristen sonra `verification_code` alanini temizle.
10. Istersen add-on sayfasinda `Show in sidebar` secenegini ac.

## Kenar Cubugu

`Show in sidebar` acildiginda sol menude `Telegram Alert` gorunur. Bu ekranda calisma durumu, kanal sayisi, keyword sayisi, son kontrol, bildirim sayisi, susturulan tekrarlar ve hata sayisi gorunur.

Hata sayisi yalnizca son 24 saati kapsar. 24 saatten eski hata kayitlari otomatik temizlenir.

## GitHub Yerlesimi

Home Assistant repository olarak okunacak yapi:

```text
repository.yaml
telegram_keyword_alert/config.json
telegram_keyword_alert/Dockerfile
telegram_keyword_alert/run.sh
telegram_keyword_alert/app.py
```
