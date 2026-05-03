# Telegram Keyword Alert Yeniden Kurulum Kılavuzu

Bu kılavuz, Home Assistant OS'i yeniden kurduktan sonra `Telegram Keyword Alert` add-on'unu en hızlı şekilde tekrar kurmak için hazırlandı.

## 1. En Hızlı Kurulum Yöntemi

Bu repo Home Assistant'a doğrudan repository URL olarak eklenebilir.

Kullanacağın URL:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

Bu yöntemde Home Assistant üzerinde klasör oluşturman gerekmez.

## 2. Home Assistant'ta GitHub URL ile Kurulum

1. Home Assistant'ı kur.
2. `Ayarlar` > `Eklentiler` bölümüne gir.
3. `Add-on Store` ekranını aç.
4. Sağ üstteki üç nokta menüye bas.
5. `Repositories` seçeneğini aç.
6. Şu URL'yi ekle:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

7. Kaydet.
8. Add-on listesini yenile.
9. `Telegram Keyword Alert` eklentisini aç.
10. `Install` / `Yükle` düğmesine bas.

## 2.1 Bu Yöntemde GitHub'da Ne Var

Home Assistant'ın repository olarak okuyacağı yapı repo içinde hazır:

```text
repository.yaml
telegram_keyword_alert/
  config.json
  Dockerfile
  run.sh
  app.py
```

Yani yeniden kurulumda senin dosya taşıman gerekmez.

## 3. Add-on'u Home Assistant'a Göster

1. Repository URL'yi ekledikten sonra add-on listesinde `Telegram Keyword Alert` görünmeli.
2. Eklentiyi aç ve `Install` / `Yükle` düğmesine bas.

## 4. İlk Konfigürasyon

`Configuration` / `Yapılandırma` ekranında şu alanları doldur:

- `api_id`
- `api_hash`
- `phone_number`
- `pushover_user_key`
- `pushover_api_token`
- `channels`
- `keywords`
- `exclude_keywords` isteğe bağlı

`verification_code` alanı ilk giriş sırasında geçici olarak kullanılacak.

## 5. Telegram API Bilgilerini Nereden Alacaksın

1. Tarayıcıdan [my.telegram.org](https://my.telegram.org) sitesine gir.
2. Telegram telefon numaranla giriş yap.
3. `API development tools` bölümüne gir.
4. Gerekirse yeni uygulama oluştur.
5. Şu iki bilgiyi not al:

- `api_id`
- `api_hash`

## 6. Pushover Bilgilerini Nereden Alacaksın

1. [pushover.net](https://pushover.net) hesabına gir.
2. `Your User Key` değerini not al.
3. `Create an Application/API Token` ile uygulama oluştur.
4. `API Token/Key` değerini not al.

Kullanacağın alanlar:

- `pushover_user_key`
- `pushover_api_token`

## 7. Telefon Numarası Formatı

`phone_number` alanına numaranı şu formatta yaz:

```text
+905xxxxxxxxx
```

## 8. Kanal Listesi Nasıl Girilecek

`channels` alanına her bir kanalı ayrı öğe olarak ekle.

Örnek:

```text
@yaniyocom
@firsatz
@onual_firsat
```

Şu an kullandığın kanal listesi:

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

## 9. Keyword Listesi Nasıl Girilecek

`keywords` alanına takip etmek istediğin kelimeleri ekle.

Örnek:

```text
iphone 16
airpods
dyson
ps5
```

`exclude_keywords` alanına istemediğin eşleşmeleri koyabilirsin.

Örnek:

```text
çekiliş
yorum yap
```

## 10. İlk Telegram Girişi

1. Tüm alanları kaydet.
2. Eklentiyi `Start` et.
3. Log ekranında Telegram girişi istendiğini göreceksin.
4. Telegram uygulamanda gelen giriş kodunu kontrol et.
5. Bu kodu `verification_code` alanına yaz.
6. `Save` de.
7. Eklentiyi `Restart` et.

Başarılı olursa logda buna benzer satırlar görürsün:

```text
Kod ile giriş başarılı.
Giriş yapıldı: Nuri
Kanal dinleme başladı.
```

## 11. Giriş Sonrası

Giriş tamamlandıktan sonra:

1. `verification_code` alanını boşalt.
2. `Save` de.

Bu alanın dolu kalması gerekmez.

## 12. Kenar Çubuğu Durum Ekranı

Sürüm `2.0` ve sonrasında add-on'un kendi durum ekranı vardır.

1. Add-on sayfasına gir.
2. Add-on çalışıyorsa `Start` durumda kalsın.
3. `Show in sidebar` seçeneğini aç.
4. Sol menüde `Telegram Alert` görünür.
5. Bu ekranda çalışma durumu, kanal sayısı, keyword sayısı, son kontrol, son bildirim, susturulan tekrarlar ve hata sayısı görünür.

Hata sayısı yalnızca son 24 saati kapsar. 24 saatten eski hata kayıtları otomatik temizlenir.

## 13. Çalıştığını Nasıl Anlarsın

Log ekranında buna benzer satırlar görünmeli:

```text
Giriş yapıldı: Nuri
Kanal sayısı: 11
Keyword sayısı: 1
Kanal dinleme başladı.
```

Bir eşleşme geldiğinde logda şunu görürsün:

```text
Bildirim gönderildi. Kanal: ... Keyword: ...
```

## 14. Versiyonlama

Bundan sonra sürümler `2.0`, `2.1`, `2.2` formatında ilerler.

## 15. Önemli Not

Telegram oturum bilgisi ve görülmüş mesaj kaydı çalışırken add-on'un kendi veri alanında tutulur. Home Assistant'ı tamamen yeniden kurarsan, çoğu durumda Telegram girişini yeniden yapman gerekir.

## 16. Hata Olursa İlk Kontrol Listesi

1. `api_id` ve `api_hash` doğru mu?
2. `phone_number` `+90` ile mi yazıldı?
3. `pushover_user_key` ve `pushover_api_token` doğru mu?
4. `channels` listesi doğru mu?
5. `keywords` boş mu?
6. Log ekranında `Kanal dinleme başladı.` satırı var mı?
