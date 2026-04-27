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

1. Dosyalari `/addons/local/telegram_keyword_alert` altina koy.
2. Buradaki kaynak klasorun adi `telegram_keyword_alert_addon` olsa da, Home Assistant tarafindaki hedef klasor adini `telegram_keyword_alert` yap.
3. Home Assistant'ta `Reload` yap.
4. Add-on'u `Install` et.
5. Alanlari doldur ve `Save` de.
6. `Start` et.
7. Telegram'dan gelen kodu `verification_code` alanina gir.
8. `Restart` et.
9. Basarili giristen sonra `verification_code` alanini temizle.

## GitHub Yerlesimi

GitHub repo kullanacaksan, dosyalari repo ana klasorunde tutabilirsin:

```text
config.json
Dockerfile
run.sh
app.py
README.md
REINSTALL_GUIDE_TR.md
CONFIG_TEMPLATE.md
```

Ama Home Assistant tarafinda bu dosyalar mutlaka su klasore yerlestirilmeli:

```text
/addons/local/telegram_keyword_alert
```
