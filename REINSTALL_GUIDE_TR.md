# Telegram Keyword Alert Yeniden Kurulum Kilavuzu

Bu kilavuz, Home Assistant OS'i yeniden kurduktan sonra `Telegram Keyword Alert` add-on'unu tekrar ayağa kaldirmak icin hazirlandi.

## 1. Gerekli Dosyalar

Yeni kurulumdan sonra Home Assistant cihazinda su klasor yapisi olmalidir:

- `/addons/local/telegram_keyword_alert/config.json`
- `/addons/local/telegram_keyword_alert/Dockerfile`
- `/addons/local/telegram_keyword_alert/run.sh`
- `/addons/local/telegram_keyword_alert/app.py`

Bu dosyalar bu klasorde hazir duruyor:

- [config.json](/Users/nuriacar/Documents/Codex/2026-04-19-telegram-hesab-mdan-takip-etti-im/telegram_keyword_alert_addon/config.json)
- [Dockerfile](/Users/nuriacar/Documents/Codex/2026-04-19-telegram-hesab-mdan-takip-etti-im/telegram_keyword_alert_addon/Dockerfile)
- [run.sh](/Users/nuriacar/Documents/Codex/2026-04-19-telegram-hesab-mdan-takip-etti-im/telegram_keyword_alert_addon/run.sh)
- [app.py](/Users/nuriacar/Documents/Codex/2026-04-19-telegram-hesab-mdan-takip-etti-im/telegram_keyword_alert_addon/app.py)

## 1.1 Klasoru Nasil Kopyalayacaksin

Buradaki kaynak klasorun adi:

- `telegram_keyword_alert_addon`

Ama Home Assistant icindeki hedef klasorun adi su olmali:

- `telegram_keyword_alert`

Yani en guvenli yontem su:

1. Home Assistant cihazinda su klasoru olustur:

```sh
/addons/local/telegram_keyword_alert
```

2. Buradaki `telegram_keyword_alert_addon` klasorunun icindeki dosyalari alip, Home Assistant'taki `telegram_keyword_alert` klasorunun icine koy.

Son durum su olmali:

- `/addons/local/telegram_keyword_alert/config.json`
- `/addons/local/telegram_keyword_alert/Dockerfile`
- `/addons/local/telegram_keyword_alert/run.sh`
- `/addons/local/telegram_keyword_alert/app.py`

Onemli:

- Home Assistant tarafinda klasor adini `telegram_keyword_alert_addon` yapma
- `slug` ile uyumlu olmasi icin hedef klasor adi `telegram_keyword_alert` olmali

## 2. Home Assistant Icinde Klasoru Hazirla

1. Home Assistant'i kur.
2. `SSH & Web Terminal` eklentisini kur ve ac.
3. Terminalde su komutu calistir:

```sh
mkdir -p /addons/local/telegram_keyword_alert
```

4. Bu klasorde bulunan 4 ana dosyayi yeni sistemde `/addons/local/telegram_keyword_alert` altina kopyala.

## 2.1 GitHub Kullanacaksan

Eger bu projeyi GitHub'da sakliyorsan, repo icinde en temiz yapi su olur:

```text
telegram-keyword-alert-addon/
  config.json
  Dockerfile
  run.sh
  app.py
  README.md
  REINSTALL_GUIDE_TR.md
  CONFIG_TEMPLATE.md
```

Yani GitHub'da bu dosyalar repo ana klasorunde durabilir. Ek bir alt klasor zorunlu degil.

Yeniden kurulumda GitHub'dan alirken yapacagin sey:

1. GitHub repo'nu ac.
2. Repo icindeki su dosyalari indir ya da kopyala:
   - `config.json`
   - `Dockerfile`
   - `run.sh`
   - `app.py`
3. Home Assistant cihazinda su klasoru olustur:

```sh
mkdir -p /addons/local/telegram_keyword_alert
```

4. GitHub'dan aldigin bu 4 dosyayi Home Assistant'ta su klasorun icine koy:

```text
/addons/local/telegram_keyword_alert
```

Son gorunum su olmali:

- `/addons/local/telegram_keyword_alert/config.json`
- `/addons/local/telegram_keyword_alert/Dockerfile`
- `/addons/local/telegram_keyword_alert/run.sh`
- `/addons/local/telegram_keyword_alert/app.py`

Kisa ozet:

- GitHub'da dosyalar repo ana klasorunde olabilir
- Home Assistant'ta ise ayni dosyalar mutlaka `/addons/local/telegram_keyword_alert` altinda olmali

## 3. Add-on'u Home Assistant'a Goster

1. Home Assistant arayuzunde `Ayarlar` > `Eklentiler` bolumune gir.
2. Sag ustten `Reload` / `Yeniden Yukle` yap.
3. Listede `Telegram Keyword Alert` gorunmeli.
4. Eklentiyi ac ve `Install` / `Yukle` dugmesine bas.

## 4. Ilk Konfigurasyon

`Configuration` / `Yapilandirma` ekraninda su alanlari doldur:

- `api_id`
- `api_hash`
- `phone_number`
- `pushover_user_key`
- `pushover_api_token`
- `channels`
- `keywords`
- `exclude_keywords` istege bagli

`verification_code` alani ilk giris sirasinda gecici olarak kullanilacak.

## 5. Telegram API Bilgilerini Nereden Alacaksin

1. Tarayicidan [my.telegram.org](https://my.telegram.org) sitesine gir.
2. Telegram telefon numaranla giris yap.
3. `API development tools` bolumune gir.
4. Gerekirse yeni uygulama olustur.
5. Su iki bilgiyi not al:

- `api_id`
- `api_hash`

## 6. Pushover Bilgilerini Nereden Alacaksin

1. [pushover.net](https://pushover.net) hesabina gir.
2. `Your User Key` degerini not al.
3. `Create an Application/API Token` ile uygulama olustur.
4. `API Token/Key` degerini not al.

Kullanacagin alanlar:

- `pushover_user_key`
- `pushover_api_token`

## 7. Telefon Numarasi Formati

`phone_number` alanina numarani su formatta yaz:

```text
+905xxxxxxxxx
```

## 8. Kanal Listesi Nasil Girilecek

`channels` alanina her bir kanali ayri oge olarak ekle.

Ornek:

```text
@yaniyocom
@firsatz
@onual_firsat
```

Su an kullandigin kanal listesi:

- `@yaniyocom`
- `@firsatz`
- `@onual_firsat`
- `@onual_ekstra`
- `@butcedostu`
- `@depoindirim`
- `@uygunfiyatdedektifi`
- `@tasarrufluharca`
- `@depourunleri`
- `@evEkonomi`
- `@firsatavi`

## 9. Keyword Listesi Nasil Girilecek

`keywords` alanina takip etmek istedigin kelimeleri ekle.

Ornek:

```text
iphone 16
airpods
dyson
ps5
```

`exclude_keywords` alanina istemedigin eslesmeleri koyabilirsin.

Ornek:

```text
cekilis
yorum yap
```

## 10. Ilk Telegram Girisi

1. Tum alanlari kaydet.
2. Eklentiyi `Start` et.
3. Log ekraninda Telegram girisi istendigini goreceksin.
4. Telegram uygulamanda gelen giris kodunu kontrol et.
5. Bu kodu `verification_code` alanina yaz.
6. `Save` de.
7. Eklentiyi `Restart` et.

Basarili olursa logda buna benzer satirlar gorursun:

```text
Kod ile giris basarili.
Giris yapildi: Nuri
Kanal dinleme basladi.
```

## 11. Giris Sonrasi

Giris tamamlandiktan sonra:

1. `verification_code` alanini bosalt.
2. `Save` de.

Bu alanin dolu kalmasi gerekmez.

## 12. Calistigini Nasil Anlarsin

Log ekraninda buna benzer satirlar gorunmeli:

```text
Giris yapildi: Nuri
Kanal sayisi: 11
Keyword sayisi: 1
Kanal dinleme basladi.
```

Bir eslesme geldiginde logda sunu gorursun:

```text
Bildirim gonderildi. Kanal: ... Keyword: ...
```

## 13. Onemli Not

Telegram oturum bilgisi ve gorulmus mesaj kaydi calisirken add-on'in kendi veri alaninda tutulur. Home Assistant'i tamamen yeniden kurarsan, cogu durumda Telegram girisini yeniden yapman gerekir.

## 14. Hata Olursa Ilk Kontrol Listesi

1. `api_id` ve `api_hash` dogru mu?
2. `phone_number` `+90` ile mi yazildi?
3. `pushover_user_key` ve `pushover_api_token` dogru mu?
4. `channels` listesi dogru mu?
5. `keywords` bos mu?
6. Log ekraninda `Kanal dinleme basladi.` satiri var mi?
