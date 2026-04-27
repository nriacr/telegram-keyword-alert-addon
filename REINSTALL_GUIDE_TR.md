# Telegram Keyword Alert Yeniden Kurulum Kilavuzu

Bu kilavuz, Home Assistant OS'i yeniden kurduktan sonra `Telegram Keyword Alert` add-on'unu tekrar ayaga kaldirmak icin hazirlandi.

## 1. Gerekli Dosyalar

Yeni kurulumdan sonra Home Assistant cihazinda su klasor yapisi olmalidir:

- `/addons/local/telegram_keyword_alert/config.json`
- `/addons/local/telegram_keyword_alert/Dockerfile`
- `/addons/local/telegram_keyword_alert/run.sh`
- `/addons/local/telegram_keyword_alert/app.py`

Bu dosyalar repo ana klasorunde bulunur:

- `config.json`
- `Dockerfile`
- `run.sh`
- `app.py`

## 1.1 Klasoru Nasil Kopyalayacaksin

GitHub repo icindeki dosyalari dogrudan Home Assistant'ta su hedef klasore koyacaksin:

- `telegram_keyword_alert`

Yani en guvenli yontem su:

1. Home Assistant cihazinda su klasoru olustur:

```sh
mkdir -p /addons/local/telegram_keyword_alert
```

2. GitHub repo ana klasorundeki `config.json`, `Dockerfile`, `run.sh` ve `app.py` dosyalarini alip, Home Assistant'taki `telegram_keyword_alert` klasorunun icine koy.

Son durum su olmali:

- `/addons/local/telegram_keyword_alert/config.json`
- `/addons/local/telegram_keyword_alert/Dockerfile`
- `/addons/local/telegram_keyword_alert/run.sh`
- `/addons/local/telegram_keyword_alert/app.py`

Onemli:

- Home Assistant tarafinda klasor adini farkli yapma
- `slug` ile uyumlu olmasi icin hedef klasor adi `telegram_keyword_alert` olmali

## 2. Home Assistant Icinde Klasoru Hazirla

1. Home Assistant'i kur.
2. `SSH & Web Terminal` eklentisini kur ve ac.
3. Terminalde su komutu calistir:

```sh
mkdir -p /addons/local/telegram_keyword_alert
```

4. GitHub repo ana klasorunden `config.json`, `Dockerfile`, `run.sh` ve `app.py` dosyalarini alip bu klasore koy.

## 2.1 GitHub Kullanacaksan

Bu projede repo yapisi su sekilde tutulur:

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

Yeniden kurulumda GitHub'dan alirken yapacagin sey:

1. GitHub repo'nu ac.
2. Repo icindeki su dosyalari indir:
   - `config.json`
   - `Dockerfile`
   - `run.sh`
   - `app.py`
3. Home Assistant cihazinda su klasoru olustur:

```sh
mkdir -p /addons/local/telegram_keyword_alert
```

4. Indirdigin bu 4 dosyayi Home Assistant'ta su klasorun icine koy:

```text
/addons/local/telegram_keyword_alert
```

5. Gerekirse repo'daki `REINSTALL_GUIDE_TR.md` ve `CONFIG_TEMPLATE.md` dosyalarini da referans olarak sakla.

Kisa ozet:

- GitHub'da dosyalar repo ana klasorunde durur
- Home Assistant'ta ise ayni dosyalar mutlaka `/addons/local/telegram_keyword_alert` altinda olmali

## 2.2 Home Assistant Add-on Uzerinden Kolay GitHub Geri Kurulum

En kolay geri kurulum yontemi genelde `SSH & Web Terminal` eklentisiyle dosyalari yerlestirmektir.

1. Home Assistant'ta `SSH & Web Terminal` eklentisini kur.
2. Eklentiyi ac.
3. `/addons/local/telegram_keyword_alert` klasorunu olustur.
4. GitHub repo'ndaki 4 ana dosyayi bu klasore kopyala.
5. Home Assistant'ta `Reload` yap.
6. `Telegram Keyword Alert` add-on'unu `Install` et.

Not:

- Bu repo'yu Home Assistant'in add-on listesine harici repo olarak eklemiyorsun
- Buradaki mantik, repo'yu yedek olarak tutup add-on dosyalarini `/addons/local/telegram_keyword_alert` altina geri koymak

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
