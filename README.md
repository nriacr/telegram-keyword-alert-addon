# Telegram Keyword Alert Add-on

Home Assistant OS üzerinde çalışan, Telegram kanallarını dinleyip belirlenen keyword'ler geçince Pushover bildirimi gönderen custom add-on.

## Kolay Kurulum

Bu repo, Home Assistant'a doğrudan repository URL olarak eklenebilecek şekilde hazırlandı.

Kullanacağın URL:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

## Home Assistant İçinde Kurulum

1. `Ayarlar` > `Eklentiler` sayfasına gir.
2. `Add-on Store` ekranını aç.
3. Sağ üstteki üç nokta menüden `Repositories` seç.
4. Şu URL'yi ekle:

```text
https://github.com/nriacr/telegram-keyword-alert-addon
```

5. Kaydet.
6. Add-on listesinde `Telegram Keyword Alert` görünecek.
7. Eklentiyi aç ve `Install` et.
8. `api_id`, `api_hash`, `phone_number`, `pushover_user_key`, `pushover_api_token`, `channels`, `keywords` alanlarını doldur.
9. İlk girişte `verification_code` alanını geçici olarak kullan.

## Kenar Çubuğu Arayüzü

Sürüm `2.0` ile kenar çubuğu arayüzü daha küçük ölçekli hale getirildi, Türkçe metinler düzeltildi ve `Kayıtları Aç` / `Add-on Sayfasını Aç` butonları add-on kimliğini otomatik bulacak şekilde güncellendi.

1. Add-on'u `Start` et.
2. Add-on sayfasında `Show in sidebar` seçeneğini aç.
3. Sol menüde `Telegram Alert` görünür.
4. Bu ekranda çalışma durumu, kanal sayısı, keyword sayısı, son kontrol, bildirim sayısı, susturulan tekrarlar ve hata sayısı görünür.

Hata sayısı yalnızca son 24 saati kapsar. 24 saatten eski hata kayıtları otomatik temizlenir.

## Versiyonlama

Bundan sonra sürümler `2.0`, `2.1`, `2.2` formatında ilerler.

## Repo Yapısı

Home Assistant'ın repository olarak okuyacağı dosyalar:

- `repository.yaml`
- `telegram_keyword_alert/config.json`
- `telegram_keyword_alert/Dockerfile`
- `telegram_keyword_alert/run.sh`
- `telegram_keyword_alert/app.py`

## Belgeler

- Ayrıntılı yeniden kurulum kılavuzu: `REINSTALL_GUIDE_TR.md`
- Hızlı ayar özeti: `CONFIG_TEMPLATE.md`

## Notlar

- `verification_code` giriş tamamlandıktan sonra boş bırakılabilir.
- `keywords` ve `exclude_keywords` listeleri Home Assistant arayüzünden yönetilir.
- `seen_messages.json` aynı mesaja tekrar bildirim gitmesini engeller.
- `seen_deals.json` aynı gün içinde aynı keyword ve aynı fiyat için tekrar bildirim gitmesini engeller.
