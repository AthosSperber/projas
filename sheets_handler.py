import os
from datetime import datetime
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception as e:
    raise

SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS','service_account.json')
SHEET_NAME = os.environ.get('SHEET_NAME','reclameali_data')

def _open():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME)

def add_complaint(nome, email, descricao):
    sh = _open()
    try:
        ws = sh.worksheet('Reclamacoes')
    except Exception:
        ws = sh.add_worksheet('Reclamacoes', rows=1000, cols=10)
        ws.append_row(['ID','Nome','Email','Descricao','Data'])
    ws.append_row([int(datetime.utcnow().timestamp()), nome, email, descricao, datetime.utcnow().isoformat()])

def fetch_reclamacoes():
    sh = _open()
    try:
        ws = sh.worksheet('Reclamacoes')
        return ws.get_all_records()
    except Exception as e:
        print("fetch_reclamacoes error:", e)
        return []

def add_analysis(pos, neu, neg):
    sh = _open()
    try:
        ws = sh.worksheet('Analises')
    except Exception:
        ws = sh.add_worksheet('Analises', rows=1000, cols=10)
        ws.append_row(['Data','Positivo','Neutro','Negativo'])
    ws.append_row([datetime.utcnow().isoformat(), pos, neu, neg])
