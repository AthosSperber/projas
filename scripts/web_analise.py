#!/usr/bin/env python3
"""
scripts/web_analise.py
Wrapper that runs scraper and sentiment, then writes analysis summary to Google Sheets (if available).
"""
import os, sys, json
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

SCRAPER = os.path.join(BASE_DIR, 'scripts', 'scraper.py')
SENTIMENT = os.path.join(BASE_DIR, 'scripts', 'sentiment.py')
OUT_JSON = os.path.join(BASE_DIR, 'data', 'relatorio.json')

def run_script(path):
    import subprocess
    if os.path.exists(path):
        subprocess.run(["python", path], cwd=BASE_DIR, check=True)

if __name__ == '__main__':
    try:
        run_script(SCRAPER)
    except Exception as e:
        print("Scraper failed:", e)
    try:
        run_script(SENTIMENT)
    except Exception as e:
        print("Sentiment failed:", e)
        raise
    # after sentiment finished, attempt sheets integration
    try:
        from sheets_handler import add_analysis
        if os.path.exists(OUT_JSON):
            with open(OUT_JSON,'r',encoding='utf-8') as f:
                data = json.load(f)
                items = data.get('items',[])
                pos = sum(1 for it in items if it.get('Sentimento')=='positivo')
                neu = sum(1 for it in items if it.get('Sentimento')=='neutro')
                neg = sum(1 for it in items if it.get('Sentimento')=='negativo')
                add_analysis(pos,neu,neg)
    except Exception as e:
        print("Sheets integration skipped or failed:", e)
    print("web_analise finished.")
