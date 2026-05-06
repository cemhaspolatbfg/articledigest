# Output Format — arXiv Daily Digest

> Bu dosya, Claude'un hazırladığı günlük arXiv özetinin nasıl formatlanacağını,
> nereye gönderileceğini ve nasıl arşivleneceğini tanımlar.

---

## Teslimat Kanalı

- **Kanal:** Gmail connector
- **Gönderim modu:** **Taslak oluştur** (`gmail_create_draft`). Manuel "Send" gerekiyor.
- **Alıcı:** cemhaspolat@bugfix.games
- **Konu satırı:** `📚 arXiv Digest — DD/MM/YYYY`
- Sadece yukarıda belirtilen adrese gönder, başka alıcı ekleme
- CC veya BCC kullanma

> **Not:** Direct-send tool henüz expose edilmedi; Gmail taslaklara girip Send'e basmak gerekiyor. Routine draft oluşturduktan sonra iş biter.

---

## Format

- **Dil:** Türkçe (makale başlıkları hariç, onlar orijinal İngilizce kalır)
- **Uzunluk:** Makale sayısına bağlı; tipik olarak 300-600 kelime
- **Body type:** HTML (Markdown değil)

### Neden HTML?

Gmail connector'a Markdown body verildiğinde `**bold**` ve `[link](url)` sözdizimi düz metin olarak görünür. HTML body verildiğinde tıklanabilir linkler ve başlıklar düzgün render olur.

---

## HTML Mail Şablonu

Aşağıdaki şablonu kullan. Köşeli parantez içindeki yer tutucuları içerikle doldur. Yapıyı bozma — başlık seviyeleri (h2, h3) ve liste yapısı sabittir.

```html
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 680px; line-height: 1.6;">

  <h2 style="margin-bottom: 4px;">📚 arXiv Günlük Digest — [DD/MM/YYYY]</h2>
  <p>İşte bugün ilgi alanlarınla eşleşen makaleler:</p>

  <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

  <h3>🎮 Oyun & Gamification</h3>
  <ul>
    <li>
      <strong>[Makale Başlığı]</strong> — [1-2 cümle ne yapıyor]. (<a href="[arXiv URL]">arXiv</a>)<br>
      <em>Neden ilgilenmelisin:</em> [1 cümle, profile göre değerlendirme]
    </li>
    <!-- Her makale için tekrarla -->
  </ul>

  <h3>🤖 LLM'ler, Ajanlar, AI Araçları</h3>
  <ul>
    <li>
      <strong>[Makale Başlığı]</strong> — [1-2 cümle ne yapıyor]. (<a href="[arXiv URL]">arXiv</a>)<br>
      <em>Neden ilgilenmelisin:</em> [1 cümle, profile göre değerlendirme]
    </li>
  </ul>

  <h3>💼 Girişimcilik & Dijital Ekonomi</h3>
  <ul>
    <li>
      <strong>[Makale Başlığı]</strong> — [1-2 cümle ne yapıyor]. (<a href="[arXiv URL]">arXiv</a>)<br>
      <em>Neden ilgilenmelisin:</em> [1 cümle, profile göre değerlendirme]
    </li>
  </ul>

  <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

  <p>☕ İyi araştırmalar!</p>

  <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0 12px;">

  <p style="color: #888; font-size: 12px;">
    <strong>Execution Summary:</strong><br>
    Tarih: [YYYY-MM-DD] ([GÜN_ADI])<br>
    XML toplam: [N] · Dedupe sonrası: [M] · Dahil edilen: [K]<br>
    Eksen dağılımı: 🎮 [X] · 🤖 [Y] · 💼 [Z]<br>
    Çalışma süresi: [T]
  </p>

</div>
```

### Boş Eksen Kuralı

Bir eksen için makale yoksa `<li>` içinde italik olarak şunu yaz:

```html
<li><em>Bugün bu eksende dikkat çeken bir şey yok.</em></li>
```

Asla uydurma içerik ekleme.

### Hiç Makale Yok Durumu

Semantik filtre sonrası **hiç** makale kalmadıysa, şablonu yine oluştur ama üç eksende de boş eksen kuralını uygula. Mail gövdesinin en üstünde, "İşte bugün..." cümlesinin yerine şunu yaz:

```html
<p>Bugün ilgi alanlarınla eşleşen yeni makale bulunamadı. Bu normaldir — arXiv'de her gün her konuda makale çıkmaz.</p>
```

---

## Link Kuralları

- Makale linkleri: arXiv abs sayfası (`https://arxiv.org/abs/XXXX.XXXXX`)
- Link metni: tam olarak `arXiv` (başka bir şey değil)
- arXiv PDF linki verme (okuyucu isterse abs sayfasından PDF'e gider)

---

## Arşivleme

- Her oluşturulan özeti repo'daki `archive/` klasörüne commit'le
- Dosya adı formatı: `archive/YYYY-MM-DD-digest.md`
- Örnek: `archive/2026-04-20-digest.md`
- Commit mesajı: `digest: YYYY-MM-DD`
- Arşivdeki dosya **Markdown** formatında olacak (mail HTML, arşiv Markdown)
- Aynı tarihli dosya zaten varsa üzerine yaz (rerun durumu kabul)

### Arşiv Markdown Şablonu

```markdown
# arXiv Digest — YYYY-MM-DD

## 🎮 Oyun & Gamification

- **[Makale Başlığı](arXiv URL)** — [1-2 cümle ne yapıyor].
  - *Neden ilgilenmelisin:* [1 cümle]

## 🤖 LLM'ler, Ajanlar, AI Araçları

- **[Makale Başlığı](arXiv URL)** — [1-2 cümle ne yapıyor].
  - *Neden ilgilenmelisin:* [1 cümle]

## 💼 Girişimcilik & Dijital Ekonomi

- **[Makale Başlığı](arXiv URL)** — [1-2 cümle ne yapıyor].
  - *Neden ilgilenmelisin:* [1 cümle]

---

## Execution Summary

- Tarih: YYYY-MM-DD (GÜN_ADI)
- XML toplam: N · Dedupe sonrası: M · Dahil edilen: K
- Eksen dağılımı: 🎮 X · 🤖 Y · 💼 Z
- Çalışma süresi: T
```

---

## Hata Durumları

- **arXiv API hatası:** Mail gövdesinde belirtme; execution summary'ye yaz ("API retry ile kurtarıldı" veya "API başarısız, digest boş")
- **Gmail draft başarısız:** Digest'i yine arşive commit'le. Commit mesajına `(MAIL FAILED: <kısa hata>)` ekle.
- **Hiç makale kalmadı:** "Hiç Makale Yok Durumu" bölümündeki şablonu kullan, boş mail uydurma.

---

*Son güncelleme: 2026-04-20 (İlk kurulum)*
