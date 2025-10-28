# ======================================
# app.py — Aplicação principal Flask
# Sistema: ReclameAli+
# ======================================

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

# ================== CONFIGURAÇÕES ==================

# BASE_DIR → Caminho da pasta onde o app.py está localizado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DATA_DIR → Caminho da pasta "data" (usada para armazenar arquivos locais)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Cria a pasta se não existir

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Habilita CORS (permite comunicação entre domínios diferentes, ex: frontend separado)
CORS(app)

# Define a chave secreta usada para sessões Flask
# Se não houver uma variável de ambiente, usa "dev_secret_key" como padrão
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# ================== CONFIGURAÇÃO DA GOOGLE SERVICE ACCOUNT ==================

# cria um arquivo "service_account.json" temporário com as credenciais
# da conta de serviço do Google (usadas para acessar o Google Sheets).
if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    sa_path = os.path.join(BASE_DIR, "service_account.json")
    try:
        with open(sa_path, "w", encoding="utf-8") as f:
            # Grava o conteúdo da variável de ambiente no arquivo local
            f.write(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
        print("✔️ Service Account JSON gravado em", sa_path)
    except Exception as e:
        print("❌ Erro ao gravar service_account.json:", e)

# ================== INTEGRAÇÃO COM GOOGLE SHEETS ==================

try:
    # Importa funções auxiliares do módulo sheets_handler.py
    from sheets_handler import add_complaint, fetch_reclamacoes
    SHEETS_ENABLED = True
    print("✔️ Google Sheets habilitado.")
except Exception as e:
    # Caso o módulo não funcione, desativa a integração
    print("⚠️ Google Sheets indisponível:", e)
    SHEETS_ENABLED = False

# ================== ROTAS PRINCIPAIS ==================

@app.route("/")
def index():
    
    """
    Página inicial do sistema.
    Normalmente contém o formulário de envio de reclamações.
    Renderiza o arquivo 'templates/index.html'.
    """

    return render_template("index.html")

@app.route("/report")
def report():
    
    """
    Página de relatório de análise de sentimento.
    Renderiza o arquivo 'templates/report.html'.
    """

    return render_template("report.html")


@app.route("/complaints")
def complaints():
    
    """
    Exibe a lista de reclamações registradas.
    Se o Google Sheets estiver ativo, busca diretamente da planilha.
    Caso contrário, lê de um arquivo JSON local (data/reclamacoes.json).
    """

    try:
        if SHEETS_ENABLED:
            data = fetch_reclamacoes()
        else:
            local_file = os.path.join(DATA_DIR, "reclamacoes.json")
            if os.path.exists(local_file):
                with open(local_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []
        return render_template("complaints.html", reclamacoes=data)
    except Exception as e:
        print("❌ Erro ao carregar reclamações:", e)
        return render_template("complaints.html", reclamacoes=[])


@app.route("/add_complaint", methods=["POST"])
def add_complaint_route():
    
    """
    Adiciona uma nova reclamação.
    Essa rota é chamada pelo frontend via POST (JSON).
    """

    try:
        data = request.get_json()  # Lê os dados enviados do formulário
        print("📩 Dados recebidos:", data)

        # Validação básica dos campos obrigatórios
        if not data or "nome" not in data or "descricao" not in data:
            return jsonify({"status": "error", "message": "Dados incompletos."}), 400

        # Adiciona data e hora atuais
        data["data_envio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if SHEETS_ENABLED:
            # Envia a reclamação para o Google Sheets
            add_complaint(data)
        else:
            # Salva localmente em um arquivo JSON
            local_file = os.path.join(DATA_DIR, "reclamacoes.json")
            if os.path.exists(local_file):
                with open(local_file, "r", encoding="utf-8") as f:
                    reclamacoes = json.load(f)
            else:
                reclamacoes = []

            reclamacoes.append(data)
            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(reclamacoes, f, indent=4, ensure_ascii=False)

        return jsonify({"status": "success", "message": "Reclamação adicionada com sucesso!"})

    except Exception as e:
        print("❌ Erro ao adicionar reclamação:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/report/<filename>")
def download_report(filename):
    
    """
    Rota responsável por fazer o download de relatórios gerados pelo sistema.
    """

    try:
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"message": "Relatório não encontrado", "status": "error"}), 404
    except Exception as e:
        print("❌ Erro ao enviar relatório:", e)
        return jsonify({"message": str(e), "status": "error"}), 500


@app.route("/health")
def health_check():

    """
    Endpoint de verificação simples (usado por Render, Docker, etc.)
    Serve para checar se o servidor está rodando corretamente.
    """

    return jsonify({"status": "ok", "message": "Servidor ativo e saudável!"})


# ================== EXECUÇÃO LOCAL ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
