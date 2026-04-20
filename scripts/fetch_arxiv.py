#!/usr/bin/env python3
"""
arXiv Daily Fetch Script
-------------------------
GitHub Actions tarafından her sabah çalıştırılır.
arXiv API'den ilgili makaleleri çeker, data/ klasörüne XML olarak kaydeder.

Kullanım:
    python scripts/fetch_arxiv.py

Çıktı:
    data/arxiv-YYYY-MM-DD.xml
"""

import urllib.request
import urllib.parse
import os
import sys
from datetime import datetime, timezone

# === KATEGORİLER ===
CATEGORIES = [
    "cs.AI", "cs.HC", "cs.GT", "cs.CY", "cs.MA",
    "cs.CL", "cs.LG", "cs.SE", "cs.IR", "cs.SI",
    "econ.GN"
]

# === ANAHTAR KELİMELER ===
# Eksen 1: Oyun & Gamification (all: = başlık + özet)
AXIS1_KEYWORDS = [
    'all:"game design"', 'all:"game development"', 'all:"gameplay"',
    'all:"video game"', 'all:"procedural content generation"',
    'all:"PCG"', 'all:"level generation"', 'all:"NPC"',
    'all:"game AI"', 'all:"player behavior"', 'all:"gamification"',
    'all:"game mechanics"', 'all:"engagement loop"',
    'all:"reward system"', 'all:"player retention"'
]

# Eksen 2: LLM'ler, Ajanlar, AI Araçları (ti: = sadece başlık)
AXIS2_KEYWORDS = [
    'ti:"LLM agent"', 'ti:"agentic"', 'ti:"multi-agent"',
    'ti:"tool use"', 'ti:"RAG"', 'ti:"prompt engineering"',
    'ti:"autonomous agent"', 'ti:"workflow automation"',
    'ti:"AI assistant"', 'ti:"copilot"', 'ti:"code generation"'
]

# Eksen 3: Girişimcilik & Dijital Ekonomi (ti: = sadece başlık)
AXIS3_KEYWORDS = [
    'ti:"platform economy"', 'ti:"two-sided market"',
    'ti:"marketplace"', 'ti:"network effect"',
    'ti:"creator economy"', 'ti:"digital labor"',
    'ti:"gig economy"', 'ti:"fintech"', 'ti:"digital payment"',
    'ti:"startup"', 'ti:"monetization"', 'ti:"subscription"',
    'ti:"user acquisition"', 'ti:"product-market fit"'
]

MAX_RESULTS = 200
API_URL = "http://export.arxiv.org/api/query"


def build_query():
    """sources.md'deki sorgu yapısını oluşturur."""
    cat_filter = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    all_keywords = AXIS1_KEYWORDS + AXIS2_KEYWORDS + AXIS3_KEYWORDS
    kw_filter = " OR ".join(all_keywords)
    query = f"({cat_filter}) AND ({kw_filter})"
    return query


def fetch_arxiv(query, max_retries=2):
    """arXiv API'den veri çeker. Başarısız olursa retry yapar."""
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": MAX_RESULTS
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    headers = {
        "User-Agent": "BugfixGames-arXiv-Digest/1.0 (cemhaspolat@bugfix.games)"
    }
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(max_retries):
        try:
            print(f"Fetching arXiv API (attempt {attempt + 1})...")
            response = urllib.request.urlopen(req, timeout=60)
            data = response.read()
            print(f"Success! Received {len(data)} bytes")
            return data
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                print("Waiting 30 seconds before retry...")
                time.sleep(30)

    print("All attempts failed.")
    sys.exit(1)


def save_xml(data, output_dir="data"):
    """XML verisini data/ klasörüne kaydeder."""
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"arxiv-{today}.xml"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(data)

    print(f"Saved to {filepath}")
    return filepath


def main():
    query = build_query()
    print(f"Query length: {len(query)} chars")
    print(f"Categories: {len(CATEGORIES)}")
    print(f"Keywords: {len(AXIS1_KEYWORDS) + len(AXIS2_KEYWORDS) + len(AXIS3_KEYWORDS)}")

    data = fetch_arxiv(query)
    filepath = save_xml(data)
    print(f"Done. Output: {filepath}")


if __name__ == "__main__":
    main()
