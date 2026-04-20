# Sources — arXiv Daily Digest

> Bu dosya, Routine'in her gün taraması gereken arXiv kategorilerini,
> anahtar kelimeleri ve API sorgu stratejisini içerir.
> Routine sadece burada tanımlanan kategoriler ve anahtar kelimeler üzerinden çalışır.

---

## Birincil Erişim: arXiv API

arXiv HTML sayfalarına scraping ile erişim rate limit riski taşır.
Bunun yerine **arXiv'in resmi API'si** kullanılır.

**Endpoint:** `http://export.arxiv.org/api/query`

**Avantajları:**
- Yapılandırılmış Atom/XML cevabı (başlık, yazarlar, özet, kategoriler, tarih)
- Rate limit toleransı yüksek, günde 1 sorgu için sıfır risk
- `submittedDate` filtresi ile son 24 saat hassas seçilebilir
- Cross-list'leri ana sonuçlarla birlikte döner

**Sorgu parametreleri:**
- `search_query`: Kategoriler + anahtar kelimeler (aşağıda detay)
- `sortBy=submittedDate&sortOrder=descending`
- `max_results=200` (güvenli üst sınır; günlük hacim genelde bunun altında)

---

## Takip Edilen Kategoriler (11 Kanal)

| Kategori | Adı | Neden? |
|---|---|---|
| cs.AI | Artificial Intelligence | Oyun AI, PCG, ajan mimarisi |
| cs.HC | Human-Computer Interaction | Gamification, hibrit app araştırması |
| cs.GT | Computer Science and Game Theory | Oyun teorisi, mekanik, ödül sistemi |
| cs.CY | Computers and Society | Platform ekonomisi, girişimcilik |
| cs.MA | Multiagent Systems | AI ajanlar, otonom sistemler |
| cs.CL | Computation and Language | NLP, dil modelleri, LLM'ler |
| cs.LG | Machine Learning | Genel ML trendleri |
| cs.SE | Software Engineering | LLM destekli kod üretimi, agent workflows |
| cs.IR | Information Retrieval | RAG, semantic search, recommendation |
| cs.SI | Social and Information Networks | Platform dinamikleri, kullanıcı davranışı |
| econ.GN | General Economics | Fintech, dijital pazarlar, startup ekonomisi |

arXiv API sorgusunda kategori filtresi formatı:
```
cat:cs.AI OR cat:cs.HC OR cat:cs.GT OR cat:cs.CY OR cat:cs.MA OR cat:cs.CL OR cat:cs.LG OR cat:cs.SE OR cat:cs.IR OR cat:cs.SI OR cat:econ.GN
```

---

## Anahtar Kelime Listesi (3 Eksen)

Her anahtar kelime **tam ifade** olarak aranır — yani "game design" sorgusu "game" ve "design" kelimelerinin ayrı ayrı geçtiği makaleleri değil, "game design" ifadesinin bütünsel olarak geçtiği makaleleri yakalar.

### Eksen 1: Oyun & Gamification — Gevşek Mod

**Arama alanı:** `all:` (başlık + özet + kategori notları)
**Sebep:** Oyun geliştirme makaleleri genellikle başlıkta "game" kelimesini içermez; özette detay verir. Gevşek mod kaçırma riskini azaltır.

Anahtar kelimeler:
- `game design`
- `game development`
- `gameplay`
- `video game`
- `procedural content generation`
- `PCG`
- `level generation`
- `NPC`
- `game AI`
- `player behavior`
- `gamification`
- `game mechanics`
- `engagement loop`
- `reward system`
- `player retention`

### Eksen 2: LLM'ler, Ajanlar, AI Araçları — Sıkı Mod

**Arama alanı:** `ti:` (sadece başlık)
**Sebep:** LLM/agent makaleleri zaten çok fazla; sıkı mod sadece gerçekten bu konuya **özel** olanları yakalar. Özette geçen dolaylı bahsetmeleri filtreler.

Anahtar kelimeler:
- `LLM agent`
- `agentic`
- `multi-agent`
- `tool use`
- `RAG`
- `prompt engineering`
- `autonomous agent`
- `workflow automation`
- `AI assistant`
- `copilot`
- `code generation`

### Eksen 3: Girişimcilik & Dijital Ekonomi — Sıkı Mod

**Arama alanı:** `ti:` (sadece başlık)
**Sebep:** Ekonomi terimleri genel geçerlidir; "startup" özette birçok yerde anlamsız geçebilir. Sıkı mod, ana konu **bu olan** makaleleri yakalar.

Anahtar kelimeler:
- `platform economy`
- `two-sided market`
- `marketplace`
- `network effect`
- `creator economy`
- `digital labor`
- `gig economy`
- `fintech`
- `digital payment`
- `startup`
- `monetization`
- `subscription`
- `user acquisition`
- `product-market fit`

---

## arXiv API Sorgu Formatı

Tek bir HTTP GET isteği ile tüm eksenler birden taranır. Sorgu yapısı:

```
(kategori_filtresi) AND ((eksen1_kelimeleri) OR (eksen2_kelimeleri) OR (eksen3_kelimeleri))
```

### Örnek Sorgu Yapısı

```
search_query=
  (cat:cs.AI OR cat:cs.HC OR cat:cs.GT OR cat:cs.CY OR cat:cs.MA
   OR cat:cs.CL OR cat:cs.LG OR cat:cs.SE OR cat:cs.IR OR cat:cs.SI
   OR cat:econ.GN)
  AND
  (
    all:"game design" OR all:"game development" OR all:"gameplay"
    OR all:"video game" OR all:"procedural content generation"
    OR all:"PCG" OR all:"level generation" OR all:"NPC"
    OR all:"game AI" OR all:"player behavior" OR all:"gamification"
    OR all:"game mechanics" OR all:"engagement loop"
    OR all:"reward system" OR all:"player retention"
    OR ti:"LLM agent" OR ti:"agentic" OR ti:"multi-agent"
    OR ti:"tool use" OR ti:"RAG" OR ti:"prompt engineering"
    OR ti:"autonomous agent" OR ti:"workflow automation"
    OR ti:"AI assistant" OR ti:"copilot" OR ti:"code generation"
    OR ti:"platform economy" OR ti:"two-sided market"
    OR ti:"marketplace" OR ti:"network effect"
    OR ti:"creator economy" OR ti:"digital labor"
    OR ti:"gig economy" OR ti:"fintech" OR ti:"digital payment"
    OR ti:"startup" OR ti:"monetization" OR ti:"subscription"
    OR ti:"user acquisition" OR ti:"product-market fit"
  )
&sortBy=submittedDate&sortOrder=descending
&max_results=200
```

### Pratik Uygulama

API cevabı bir Atom feed'dir. Her entry şunları içerir:
- `<id>` — arXiv abs URL'i (örn: `http://arxiv.org/abs/2603.12345v1`)
- `<title>` — Makale başlığı
- `<summary>` — Makale özeti (abstract)
- `<author>` — Yazar isimleri
- `<category>` — Ana kategori ve cross-list'ler
- `<published>` — İlk submission tarihi
- `<updated>` — Son güncelleme tarihi

Routine her entry için:
1. `<published>` tarihini kontrol eder (zaman aralığına uygun mu?)
2. Başlık + özeti girişimci lens'inden değerlendirir (Katman 2)
3. Seçilenleri yüzeysel özet + "neden ilgilenmelisin" cümlesi ile sunar

---

## Zaman Aralığı Stratejisi

arXiv hafta sonu yayın yapmaz. Routine Pazartesi-Cuma çalışır.

| Çalıştığı Gün | Hangi Submissions? | `submittedDate` Aralığı (Eastern Time) |
|---|---|---|
| Pazartesi | Cuma akşamından Pazartesi öğlenine | Son 72 saat |
| Salı | Pazartesi öğleden Salı sabahına | Son 24 saat |
| Çarşamba | Salı'dan Çarşamba'ya | Son 24 saat |
| Perşembe | Çarşamba'dan Perşembe'ye | Son 24 saat |
| Cuma | Perşembe'den Cuma sabahına | Son 24 saat |

**Not:** arXiv'in "yeni submission" batch'i her gece 14:00 ET civarında (TR saatiyle sabaha karşı) yayınlanır. Routine TR saatiyle sabah 09:00 civarında çalıştırılırsa o günün batch'i hazır olur.

---

## Son Notlar

- Eğer bir eksen haftalarca sonuç vermezse veya çok fazla gürültü üretirse, anahtar kelime listesi burada güncellenebilir.
- Yeni bir ilgi alanı eklenirse, yeni bir eksen eklenir (mevcut eksenlere kelime sıkıştırmak yerine).
- API sorgusu URL-encode gerektirir; routine bunu otomatik yapmalı.

---

*Son güncelleme: 2026-04-20 (İlk kurulum)*
