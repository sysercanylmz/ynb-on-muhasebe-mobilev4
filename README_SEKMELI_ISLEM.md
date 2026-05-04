# Paket 5 - Sekmeli İşlem Ekranı

Bu güncellemede `İşlem` ekranı dört ayrı sekmeye bölündü:

- Gelir
- Gider
- Tahsilat
- Ödeme

## Güncellenecek ana dosya

Sadece bu dosyayı güncellemek yeterlidir:

```text
app/screens/islemler_screen.py
```

## İsteğe bağlı hızlandırma dosyaları

APK build süresini azaltmak için şu dosyalar da güncellenebilir:

```text
.github/workflows/build-apk.yml
buildozer.spec
```

`buildozer.spec` içinde mimari `arm64-v8a` olarak teklenmiştir.
Workflow dosyasında cache eklenmiştir ve build artık sadece manuel `Run workflow` ile çalışır.
