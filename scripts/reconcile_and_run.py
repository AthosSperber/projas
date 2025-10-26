#!/usr/bin/env python3
import os, subprocess, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPER = os.path.join(BASE, 'scripts', 'scraper.py')
SENT = os.path.join(BASE, 'scripts', 'sentiment.py')
print("Running scraper...")
subprocess.run([sys.executable, SCRAPER], cwd=BASE)
print("Running sentiment...")
subprocess.run([sys.executable, SENT], cwd=BASE)
print("Done.")
