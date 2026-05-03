# Telegram Keyword Alert Yeniden Kurulum Kilavuzu

Bu kilavuz, Home Assistant OS'i yeniden kurduktan sonra `Telegram Keyword Alert` add-on'unu en hizli sekilde tekrar kurmak icin hazirlandi.

## 1. En Hizli Kurulum Yontemi

Bu repo artik Home Assistant'a dogrudan repository URL olarak eklenebilir.

Kullanacagin URL:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

Bu yontemde Home Assistant uzerinde klasor olusturman gerekmez.

## 2. Home Assistant'ta GitHub URL ile Kurulum

1. Home Assistant'i kur.
2. `Ayarlar` > `Eklentiler` bolumune gir.
3. `Add-on Store` ekranini ac.
4. Sag ustteki 3 nokta menuye bas.
5. `Repositories` secenegini ac.
6. Su URL'yi ekle:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

7. Kaydet.
8. Add-on listesini yenile.
9. `Telegram Keyword Alert` eklentisini ac.
10. `Install` / `Yukle` dugmesine bas.

## 2.1 Bu Yontemde GitHub'da Ne Var

Home Assistant'in repository olarak okuyacagi yapi repo icinde hazir:

```text
repository.yaml
telegram_keyword_alert/
  config.json
  Dockerfile
  run.sh
  app.py
```

Yani yeniden kurulumda senin dosya tasimana gerek yok.

## 3. Add-on'u Home Assistant'a Goster

1. Repository URL'yi ekledikten sonra add-on listesinde `Telegram Keyword Alert` gorunmeli.
2. Eklentiyi ac ve `Install` / `Yukle` dugmesine bas.

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

## 12. Kenar Cubugu Durum Ekrani

Surum `1.1.0` ve sonrasinda add-on'un kendi durum ekrani vardir.

1. Add-on sayfasina gir.
2. Add-on calisiyorsa `Start` durumda kalsin.
3. `Show in sidebar` secenegini ac.
4. Sol menude `Telegram Alert` gorunur.
5. Bu ekranda calisma durumu, kanal sayisi, keyword sayisi, son kontrol, son bildirim, susturulan tekrarlar ve hata sayisi gorunur.

Hata sayisi yalnizca son 24 saati kapsar. 24 saatten eski hata kayitlari otomatik temizlenir.

## 13. Calistigini Nasil Anlarsin

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

## 14. Onemli Not

Telegram oturum bilgisi ve gorulmus mesaj kaydi calisirken add-on'in kendi veri alaninda tutulur. Home Assistant'i tamamen yeniden kurarsan, cogu durumda Telegram girisini yeniden yapman gerekir.

## 15. Hata Olursa Ilk Kontrol Listesi

1. `api_id` ve `api_hash` dogru mu?
2. `phone_number` `+90` ile mi yazildi?
3. `pushover_user_key` ve `pushover_api_token` dogru mu?
4. `channels` listesi dogru mu?
5. `keywords` bos mu?
6. Log ekraninda `Kanal dinleme basladi.` satiri var mi?
