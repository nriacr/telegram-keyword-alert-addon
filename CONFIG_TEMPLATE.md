# Configuration Template

Home Assistant add-on ayar ekranına girerken kullanman için kısa bir referans.

## Doldurulacak Alanlar

### Telegram

- `api_id`: `my.telegram.org` üzerinden alınır
- `api_hash`: `my.telegram.org` üzerinden alınır
- `phone_number`: `+905xxxxxxxxx`
- `verification_code`: sadece ilk girişte geçici olarak kullan

### Pushover

- `pushover_user_key`: Pushover hesabındaki `Your User Key`
- `pushover_api_token`: oluşturduğun uygulamanın `API Token/Key`

### Kanallar

Şu listeyi istersen doğrudan yeniden gir:

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

### Keyword Örneği

```text
iphone 16
airpods
dyson
ps5
```

### Exclude Keyword Örneği

```text
çekiliş
yorum yap
```

## Kurulum Sırası

1. `Ayarlar` > `Eklentiler` > `Add-on Store` ekranına gir.
2. Sağ üstteki üç nokta menüden `Repositories` seç.
3. Şu URL'yi ekle: `https://github.com/nriacr/telegram-keyword-alert-addon`
4. `Telegram Keyword Alert` eklentisini bulup `Install` et.
5. Alanları doldur ve `Save` de.
6. `Start` et.
7. Telegram'dan gelen kodu `verification_code` alanına gir.
8. `Restart` et.
9. Başarılı girişten sonra `verification_code` alanını temizle.
10. İstersen add-on sayfasında `Show in sidebar` seçeneğini aç.

## Kenar Çubuğu

`Show in sidebar` açıldığında sol menüde `Telegram Alert` görünür. Bu ekranda çalışma durumu, kanal sayısı, keyword sayısı, son kontrol, bildirim sayısı, susturulan tekrarlar ve hata sayısı görünür.

Hata sayısı yalnızca son 24 saati kapsar. 24 saatten eski hata kayıtları otomatik temizlenir.

## Versiyonlama

Bundan sonra sürümler `2.0`, `2.1`, `2.2` formatında ilerler.

## GitHub Yerleşimi

Home Assistant repository olarak okunacak yapı:

```text
repository.yaml
telegram_keyword_alert/config.json
telegram_keyword_alert/Dockerfile
telegram_keyword_alert/run.sh
telegram_keyword_alert/app.py
```
