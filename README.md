# TIFF → PDF (Windows)

Toplu TIFF dosyalarını PDF’e dönüştüren küçük bir masaüstü uygulaması. Dönüşüm motoru olarak [LibTIFF](https://libtiff.gitlab.io/libtiff/) `tiff2pdf` aracı kullanılır.

## Özellikler

- Girdi ve çıktı klasörü seçimi (Gözat)
- Alt klasörler dahil özyinelemeli TIFF taraması (`.tif` / `.tiff`)
- Genel ve geçerli dosya ilerleme göstergeleri
- Başlat / İptal
- Çıktıda klasör yapısını koruma (`in/a/x.tif` → `out/a/x.pdf`)
- Aynı isimde PDF varsa sor (üzerine yaz / atla / iptal; tümüne uygula)
- Hataları `errors.log` dosyasına yazma

## Geliştirme (Python 3.10+)

```bash
cd "tiff2pdf"
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### `tiff2pdf` ikilisi

Windows’ta `vendor/` içine `tiff2pdf.exe` ve gerekli DLL’leri koyun (bkz. [vendor/README.txt](vendor/README.txt)).

Linux’ta geliştirme için sistemde `tiff2pdf` yeterlidir (`apt install libtiff-tools` vb.).

## Windows sürümü derleme

1. `vendor/tiff2pdf.exe` ve DLL’leri yerleştirin.
2. Proje kökünde:

```bat
build.bat
```

3. Dağıtım: **`dist/Tiff2Pdf` klasörünün tamamını** kopyalayın (yalnızca `.exe` değil).

## Hazır Windows sürümü (GitHub Release)

[Releases](https://github.com/Zaferturan/tiff2pdf/releases) sayfasından `Tiff2Pdf-Windows.zip` indirin; zip içindeki klasörün tamamını bir yere çıkarın ve `Tiff2Pdf.exe` çalıştırın.

## Test

```bash
pip install pytest
pytest tests/
```

## Lisans

Uygulama kaynağı proje sahibine aittir. `tiff2pdf` ve LibTIFF için bkz. [THIRD_PARTY.md](THIRD_PARTY.md).
