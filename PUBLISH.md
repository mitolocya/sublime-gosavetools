# Package Control'de (Sublime Text) yayınlama

Paket hazır ve test edildi (`python -m unittest discover -s tests` → 7 test OK). Package Control (packagecontrol.io) paketleri GitHub'daki etiketli (tag) sürümlerden indirir; listeye girmek için `wbond/package_control_channel` deposuna küçük bir Pull Request açılır.

## 1. Hesap

Sadece GitHub hesabı gerekir (mevcut `mitolocya`). packagecontrol.io'da ayrı hesap yok.

## 2. Önce kendi Sublime Text'inde dene

**Preferences → Browse Packages…** ile açılan klasöre bu klasörü `GoSaveTool` adıyla kopyala (`tests/` ve `PUBLISH.md` gerekmez). Sublime'ı yeniden başlatmaya gerek yok. Komut paletinde "GoSaveTool" yaz, bir .srt dosyasında **Subtitles to WebVTT** dene.

## 3. GitHub deposu ve sürüm etiketi

1. https://github.com/new → `mitolocya/sublime-gosavetool`, Public, açıklama: aşağıdaki kısa açıklama, website: `https://www.gosavetool.com/`.
2. Bu klasörün içeriğini kök dizine yükle (`.gitattributes` ve `.python-version` dahil; gizli dosyaları görmek için Windows Gezgini'nde "Gizli öğeler" açık olmalı).
3. **Releases → Draft a new release** → Tag `1.0.0` (başında "v" olmadan; Package Control semver etiketleri okur) → **Publish release**.
4. Topics: `sublime-text`, `sublime-package`, `subtitles`, `srt`, `webvtt`, `word-count`.

## 4. Package Control kanalına başvuru

1. https://github.com/wbond/package_control_channel → **Fork**.
2. Fork'ta `repository/g.json` dosyasını aç (**Edit**). `"packages": [` listesinde alfabetik yere (G harfi, "GoSaveTool" sırası) şu girdiyi ekle:

```json
{
    "name": "GoSaveTool",
    "details": "https://github.com/mitolocya/sublime-gosavetools",
    "labels": ["subtitles", "text manipulation", "formatting", "word count"],
    "releases": [
        {
            "sublime_text": ">=4107",
            "tags": true
        }
    ]
}
```

3. **Commit changes** → **Contribute → Open pull request**. Başlık: `Add GoSaveTool`. Açıklamada PR şablonundaki soruları yanıtla (paketin ne yaptığı, benzer paketlerden farkı: "SRT/WebVTT conversion, shift and repair plus word counter with social media limits in one package, no dependencies").
4. Otomatik kontrol (CI) yeşil olmalı; bakımcı inceleyip birleştirir (birkaç gün ile birkaç hafta). Birleşince **Install Package → GoSaveTool** ile kurulabilir ve https://packagecontrol.io/packages/GoSaveTool sayfası açılır.

## Listeleme metinleri

packagecontrol.io sayfası README.md ve GitHub depo açıklamasından oluşur.

- **Ad:** GoSaveTool
- **Kısa açıklama (GitHub "About"):** Convert SRT and WebVTT, shift and repair subtitles, live word count with social media limits, and case changes for Sublime Text.
- **Etiketler (labels):** subtitles, text manipulation, formatting, word count
- **Uzun açıklama:** README.md

## Sonraki sürümler

Değişiklikleri depoya yükle, yeni bir release etiketi aç (`1.0.1`). Package Control yeni etiketi birkaç saat içinde kendisi bulur; yeni PR gerekmez.
