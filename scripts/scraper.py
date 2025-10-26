#!/usr/bin/env python3
import os, csv, sys, requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
OUT = os.path.join(DATA_DIR, 'scraped_comments.csv')

# Try sheets_handler fetch_reclamacoes first
try:
    from sheets_handler import fetch_reclamacoes
    rows = fetch_reclamacoes()
    if rows:
        with open(OUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['texto'])
            writer.writeheader()
            for r in rows:
                texto = str(r.get('Descricao') or r.get('Descrição') or r.get('texto') or r.get('comentario') or '').strip()
                if texto:
                    writer.writerow({'texto': texto})
        print("Wrote CSV from Google Sheets:", OUT)
        sys.exit(0)
except Exception as e:
    print("Sheets not available:", e)

# fallback: scrape URL (default app complaints page)
URL = os.environ.get('SCRAPER_SOURCE', 'http://127.0.0.1:5000/complaints')
try:
    resp = requests.get(URL, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []
    for tr in soup.select('table tbody tr'):
        cols = [td.get_text(strip=True) for td in tr.select('td')]
        if len(cols) >= 3:
            items.append(cols[2])
    if not items:
        for el in soup.select('.compl-text, .reclamacao-item, .compl-item'):
            items.append(el.get_text(strip=True))
    if not items:
        for p in soup.find_all('p'):
            t = p.get_text(strip=True)
            if len(t) > 20:
                items.append(t)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['texto'])
        writer.writeheader()
        for t in items:
            writer.writerow({'texto': t})
    print("Scraped", len(items), "items from", URL)
except Exception as e:
    print("Scraper error:", e)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['texto'])
        writer.writeheader()
    sys.exit(0)
