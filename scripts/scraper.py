#!/usr/bin/env python3
import os, requests, bs4
import BeautifulSoup
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,'data')
os.makedirs(DATA_DIR, exist_ok=True)
OUT = os.path.join(DATA_DIR, 'scraped_comments.csv')
URL = os.environ.get('SCRAPER_SOURCE', 'http://localhost:5000/')

try:
    resp = requests.get(URL, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []
    for el in soup.select('.reclamacao-item'):
        items.append({'texto': el.get_text(separator=' ', strip=True)})
    if not items:
        for p in soup.find_all('p'):
            items.append({'texto': p.get_text(strip=True)})
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['texto'])
        writer.writeheader()
        for it in items:
            writer.writerow(it)
    print("Scraped", len(items), "items")
except Exception as e:
    print("Scraper error (continuing):", e)
