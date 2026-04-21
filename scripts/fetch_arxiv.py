#!/usr/bin/env python3
"""
arXiv Daily Fetch Script (v2)
------------------------------
GitHub Actions tarafından her sabah çalıştırılır.
arXiv API'den ilgili makaleleri çeker, data/ klasörüne XML olarak kaydeder.

v2 değişiklikleri:
- Tek büyük sorgu yerine eksen başına 3 ayrı sorgu (429 hatasını önlemek için)
- İstekler arası 5 saniye bekleme (arXiv rate limit politikası)
- 3 retry, artan bekleme süreleri (30s, 60s, 120s)
- Sonuçlar birleştirilerek tek XML dosyasına yazılır

Kullanım:
    python scripts/fetch_arxiv.py

Çıktı:
    data/arxiv-YYYY-MM-DD.xml
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import sys
import time
from datetime import datetime, timezone

# === KATEGORİLER ===
CATEGORIES = [
    "cs.AI", "cs.HC", "cs.GT", "cs.CY", "cs.MA",
    "cs.CL", "cs.LG", "cs.SE", "cs.IR", "cs.SI",
    "econ.GN"
]

CAT_FILTER = " OR ".join(f"cat:{c}" for c in CATEGORIES)

# === EKSEN BAZLI SORGULAR ===
AXES = {
    "axis1_game": {
        "field": "all",
        "keywords": [
            "game design", "game development", "gameplay",
            "video game", "procedural content generation",
            "PCG", "level generation", "NPC",
            "game AI", "player behavior", "gamification",
            "game mechanics", "engagement loop",
            "reward system", "player retention"
        ]
    },
    "axis2_llm": {
        "field": "ti",
        "keywords": [
            "LLM agent", "agentic", "multi-agent",
            "tool use", "RAG", "prompt engineering",
            "autonomous agent", "workflow automation",
            "AI assistant", "copilot", "code generation"
        ]
    },
    "axis3_econ": {
        "field": "ti",
        "keywords": [
            "platform economy", "two-sided market",
            "marketplace", "network effect",
            "creator economy", "digital labor",
            "gig economy", "fintech", "digital payment",
            "startup", "monetization", "subscription",
            "user acquisition", "product-market fit"
        ]
    }
}

MAX_RESULTS_PER_AXIS = 100
API_URL = "http://export.arxiv.org/api/query"
DELAY_BETWEEN_REQUESTS = 5  # saniye


def build_axis_query(axis_config):
    """Tek bir eksen için sorgu oluşturur."""
    field = axis_config["field"]
    kw_parts = [f'{field}:"{kw}"' for kw in axis_config["keywords"]]
    kw_filter = " OR ".join(kw_parts)
    query = f"({CAT_FILTER}) AND ({kw_filter})"
    return query


def fetch_single(query, axis_name, max_retries=3):
    """Tek bir sorguyu çalıştırır, retry mantığıyla."""
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": MAX_RESULTS_PER_AXIS
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    headers = {
        "User-Agent": "BugfixGames-arXiv-Digest/2.0 (cemhaspolat@bugfix.games)"
    }
    req = urllib.request.Request(url, headers=headers)

    retry_delays = [30, 60, 120]

    for attempt in range(max_retries):
        try:
            print(f"  [{axis_name}] Fetching (attempt {attempt + 1})...")
            response = urllib.request.urlopen(req, timeout=60)
            data = response.read()
            print(f"  [{axis_name}] Success! {len(data)} bytes")
            return data
        except urllib.error.HTTPError as e:
            delay = retry_delays[min(attempt, len(retry_delays) - 1)]
            print(f"  [{axis_name}] HTTP {e.code}: {e.reason}")
            if attempt < max_retries - 1:
                print(f"  [{axis_name}] Waiting {delay}s before retry...")
                time.sleep(delay)
            else:
                print(f"  [{axis_name}] All retries failed.")
                return None
        except Exception as e:
            delay = retry_delays[min(attempt, len(retry_delays) - 1)]
            print(f"  [{axis_name}] Error: {e}")
            if attempt < max_retries - 1:
                print(f"  [{axis_name}] Waiting {delay}s before retry...")
                time.sleep(delay)
            else:
                print(f"  [{axis_name}] All retries failed.")
                return None


def merge_results(xml_responses):
    """Birden fazla XML cevabını tek bir XML'e birleştirir, duplicate'leri eler."""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    seen_ids = set()
    all_entries = []

    for xml_data in xml_responses:
        if xml_data is None:
            continue
        try:
            root = ET.fromstring(xml_data)
            entries = root.findall("atom:entry", ns)
            for entry in entries:
                entry_id = entry.find("atom:id", ns)
                if entry_id is not None and entry_id.text not in seen_ids:
                    seen_ids.add(entry_id.text)
                    all_entries.append(entry)
        except ET.ParseError as e:
            print(f"  XML parse error: {e}")
            continue

    print(f"\nTotal unique entries: {len(all_entries)} (from {len(seen_ids)} unique IDs)")

    # Yeni bir Atom feed oluştur
    feed = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom")

    title = ET.SubElement(feed, "title")
    title.text = "arXiv Daily Digest - Combined Results"

    updated = ET.SubElement(feed, "updated")
    updated.text = datetime.now(timezone.utc).isoformat()

    total = ET.SubElement(feed, "{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    total.text = str(len(all_entries))

    for entry in all_entries:
        feed.append(entry)

    return ET.tostring(feed, encoding="unicode", xml_declaration=True)


def save_xml(xml_string, output_dir="data"):
    """XML string'i dosyaya kaydeder."""
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"arxiv-{today}.xml"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_string)

    print(f"Saved to {filepath}")
    return filepath


def main():
    print("=== arXiv Daily Fetch v2 ===\n")
    print(f"Categories: {len(CATEGORIES)}")
    print(f"Axes: {len(AXES)}")
    print(f"Delay between requests: {DELAY_BETWEEN_REQUESTS}s\n")

    # İlk istek öncesi 3 saniye bekle (arXiv politikası)
    print("Initial delay (3s)...")
    time.sleep(3)

    xml_responses = []
    axis_names = list(AXES.keys())

    for i, (axis_name, axis_config) in enumerate(AXES.items()):
        query = build_axis_query(axis_config)
        kw_count = len(axis_config["keywords"])
        print(f"\n[{i+1}/{len(AXES)}] {axis_name} ({kw_count} keywords, {len(query)} chars)")

        data = fetch_single(query, axis_name)
        xml_responses.append(data)

        # Son sorgu değilse bekle
        if i < len(AXES) - 1:
            print(f"  Waiting {DELAY_BETWEEN_REQUESTS}s before next axis...")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # Başarılı cevap var mı kontrol et
    successful = sum(1 for r in xml_responses if r is not None)
    print(f"\nSuccessful fetches: {successful}/{len(AXES)}")

    if successful == 0:
        print("ERROR: No data fetched from any axis. Exiting.")
        sys.exit(1)

    # Birleştir ve kaydet
    merged_xml = merge_results(xml_responses)
    filepath = save_xml(merged_xml)
    print(f"\nDone. Output: {filepath}")


if __name__ == "__main__":
    main()
