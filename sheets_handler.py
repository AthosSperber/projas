import os
import json
import gspread  # Biblioteca usada para conectar e editar planilhas do Google
from google.oauth2.service_account import Credentials

# ================== CONFIGURAÇÕES ==================

# Escopos de permissão exigidos pela API do Google Sheets
# Eles permitem ler e escrever nas planilhas associadas à conta de serviço.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ID da planilha (copiado da URL do Google Sheets)
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")

# Nome da aba dentro da planilha
SHEET_NAME = os.environ.get("GOOGLE_SHEET_NAME", "Reclamacoes")

# ================== AUTENTICAÇÃO ==================

def get_client():
    
    """
    Cria e retorna um cliente gspread autenticado com a conta de serviço.
    Ele usa o arquivo service_account.json (gerado no app.py).
    """

    try:
        creds = Credentials.from_service_account_file(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print("❌ Erro ao autenticar no Google Sheets:", e)
        raise

# ================== FUNÇÕES DE OPERAÇÃO ==================

def fetch_reclamacoes():
    
    """
    Busca todas as reclamações existentes na planilha.
    Retorna uma lista de dicionários (cada linha da planilha vira um registro JSON).
    """

    try:
        client = get_client()
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        
        # Obtém todas as linhas da planilha
        records = sheet.get_all_records()
        print(f"📊 {len(records)} reclamações carregadas do Google Sheets.")
        return records

    except Exception as e:
        print("❌ Erro ao carregar dados do Google Sheets:", e)
        return []


def add_complaint(data):
    
    """
    Adiciona uma nova reclamação à planilha do Google Sheets.
    Espera receber um dicionário 'data' com as chaves:
      - nome
      - email (opcional)
      - descricao
      - data_envio
    """

    try:
        client = get_client()
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

        # Extrai os dados esperados
        nome = data.get("nome", "")
        email = data.get("email", "")
        descricao = data.get("descricao", "")
        data_envio = data.get("data_envio", "")

        # Adiciona nova linha à planilha
        sheet.append_row([nome, email, descricao, data_envio])
        print(f"✅ Reclamação adicionada com sucesso: {nome}")

    except Exception as e:
        print("❌ Erro ao adicionar reclamação no Google Sheets:", e)
        raise


