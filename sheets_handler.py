"""
sheets_handler.py
Handles optional Google Sheets persistence using a service account file.
"""
import os
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception as e:
    raise

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = os.environ.get('SHEET_NAME', 'reclameali_data')
SERVICE_ACCOUNT_PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')

def _open_sheet():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME)

def add_complaint(nome, email, descricao):
    sh = _open_sheet()
    try:
        ws = sh.worksheet("Reclamacoes")
    except Exception:
        ws = sh.add_worksheet("Reclamacoes", rows=1000, cols=10)
        ws.append_row(['ID','Nome','Email','Descricao','Data'])
    ws.append_row([int(datetime.utcnow().timestamp()), nome, email, descricao, datetime.utcnow().isoformat()])

def add_analysis(pos, neu, neg):
    sh = _open_sheet()
    try:
        ws = sh.worksheet("Analises")
    except Exception:
        ws = sh.add_worksheet("Analises", rows=1000, cols=10)
        ws.append_row(['Data','Positivo','Neutro','Negativo'])
    ws.append_row([datetime.utcnow().isoformat(), pos, neu, neg])

def fetch_recent_analyses(limit=10):
    sh = _open_sheet()
    try:
        ws = sh.worksheet("Analises")
        rows = ws.get_all_records()
        return rows[-limit:]
    except Exception:
        return []
