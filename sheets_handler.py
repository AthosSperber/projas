import os
from datetime import datetime

# Tenta importar o gspread e google-auth
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
    print("✔️ gspread disponível.")
except Exception as e:
    print("⚠️ gspread/google-auth indisponível:", e)
    GSPREAD_AVAILABLE = False

# Escopos e caminho de credenciais
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")
SHEET_NAME = os.environ.get("SHEET_NAME", "reclameali_data")

def _open():
    """Abre a planilha no Google Sheets"""
    if not GSPREAD_AVAILABLE:
        raise RuntimeError("Biblioteca gspread não disponível.")
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME)

def add_complaint(nome, email, descricao):
    """Adiciona uma nova reclamação na planilha"""
    if not GSPREAD_AVAILABLE:
        print("⚠️ gspread não disponível — salvamento ignorado.")
        return False
    try:
        sheet = _open().sheet1
        sheet.append_row([datetime.utcnow().isoformat(), nome, email, descricao])
        print(f"✔️ Reclamação adicionada no Google Sheets: {nome}")
        return True
    except Exception as e:
        print("❌ Erro ao adicionar reclamação:", e)
        return False

def fetch_reclamacoes():
    """Busca todas as reclamações do Google Sheets"""
    if not GSPREAD_AVAILABLE:
        print("⚠️ gspread não disponível — retornando lista vazia.")
        return []
    try:
        sheet = _open().sheet1
        records = sheet.get_all_records()
        print(f"✔️ {len(records)} reclamações carregadas do Google Sheets.")
        return records
    except Exception as e:
        print("❌ Erro ao buscar reclamações:", e)
        return []
