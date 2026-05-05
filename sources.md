# Sources — arXiv Daily Digest

> Bu dosya, Routine'in her gün kullanacağı veri kaynağını ve anahtar kelime
> yapısını tanımlar.
> 
> **ÖNEMLİ:** arXiv API'ye routine'in sandbox ortamından erişim yok
> (`host_not_allowed`). Bunun yerine bir GitHub Actions workflow her sabah
> 08:00'de (TR) arXiv API'den veriyi çekip `data/arxiv-YYYY-MM-DD.xml`
> olarak repo'ya commit'ler. Routine bu dosyayı okur.

---

## Veri Akışı

```
07:00 TR — GitHub Actions çalışır
         → scripts/fetch_arxiv.py arXiv API'den veri çeker
         → data/arxiv-YYYY-MM-DD.xml olarak repo'ya commit'ler

10:00 TR — Claude Code Routine çalışır
         → data/arxiv-YYYY-MM-DD.xml dosyasını repo'dan okur
         → Semantik filtreleme yapar
         → Digest hazırlar, Gmail draft + archive commit
```

---

## Veri Dosyası

- **Konum:** `data/arxiv-YYYY-MM-DD.xml`
- **Format:** Atom/XML (arXiv API'nin standart çıktısı)
- **Oluşturan:** GitHub Actions workflow (`fetch-arxiv.yml`)
- **Routine ne yapmalı:** Bugünün tarihine uygun dosyayı oku. Dosya yoksa
  (Actions çalışmamış veya başarısız olmuş) execution summary'de belirt ve dur.

### XML Entry Yapısı

Her `<entry>` şunları içerir:
- `<id>` — arXiv abs URL'i (örn: `http://arxiv.org/abs/2603.12345v1`)
- `<title>` — Makale başlığı
- `<summary>` — Makale özeti (abstract)
- `<author>` — Yazar isimleri
- `<category>` — Ana kategori ve cross-list'ler
- `<published>` — İlk submission tarihi (ISO 8601)
- `<updated>` — Son güncelleme tarihi

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

---

## Anahtar Kelime Listesi (3 Eksen)

### Eksen 1: Oyun & Gamification — Gevşek Mod

**Arama alanı:** `all:` (başlık + özet)

- game design, game development, gameplay, video game
- procedural content generation, PCG, level generation
- NPC, game AI, player behavior
- gamification, game mechanics, engagement loop
- reward system, player retention

### Eksen 2: LLM'ler, Ajanlar, AI Araçları — Sıkı Mod

**Arama alanı:** `ti:` (sadece başlık)

- LLM agent, agentic, multi-agent, tool use
- RAG, prompt engineering, autonomous agent
- workflow automation, AI assistant, copilot, code generation

### Eksen 3: Girişimcilik & Dijital Ekonomi — Sıkı Mod

**Arama alanı:** `ti:` (sadece başlık)

- platform economy, two-sided market, marketplace
- network effect, creator economy, digital labor
- gig economy, fintech, digital payment
- startup, monetization, subscription
- user acquisition, product-market fit

> **Not:** Bu anahtar kelimeler `scripts/fetch_arxiv.py`'de de tanımlıdır.
> Bir kelime eklemek/çıkarmak istersen **hem bu dosyayı hem script'i** güncelle.

---

## Zaman Aralığı Stratejisi

arXiv hafta sonu yayın yapmaz. Hem Actions hem Routine Pazartesi-Cuma çalışır.

| Gün | Hangi Submissions? | Zaman Aralığı |
|---|---|---|
| Pazartesi | Cuma batch'i dahil | Son 72 saat |
| Salı-Cuma | Önceki günün batch'i | Son 24 saat |

Zaman filtresi routine tarafında uygulanır (XML'deki `<published>` alanına bakarak).

---

*Son güncelleme: 2026-04-20 (GitHub Actions fetch mimarisi)*
