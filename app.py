import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

# Diretório base e caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# =============== FLASK CONFIG ===================
app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# =============== GOOGLE SERVICE ACCOUNT CONFIG ===================
if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    svc_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    sa_path = os.path.join(BASE_DIR, "service_account.json")
    try:
        with open(sa_path, "w", encoding="utf-8") as f:
            f.write(svc_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
        print("✔️ Service Account JSON gravado em", sa_path)
    except Exception as e:
        print("❌ Erro ao gravar service_account.json:", e)

# =============== GOOGLE SHEETS HANDLER ===================
try:
    from sheets_handler import add_complaint, fetch_reclamacoes
    SHEETS_ENABLED = True
    print("✔️ Google Sheets habilitado.")
except Exception as e:
    print("⚠️ Falha ao importar sheets_handler:", e)
    SHEETS_ENABLED = False

# =============== ROTAS ===================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/complaints")
def complaints():
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
        print("Erro ao carregar reclamações:", e)
        return render_template("complaints.html", reclamacoes=[])

@app.route("/submit", methods=["POST"])
def submit():
    try:
        nome = request.form.get("nome")
        email = request.form.get("email")
        descricao = request.form.get("descricao")

        # Criação do item corrigida
        item = {
            "id": int(datetime.utcnow().timestamp() * 1000),
            "nome": nome,
            "email": email,
            "descricao": descricao,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        if SHEETS_ENABLED:
            add_complaint(nome, email, descricao)
        else:
            local_file = os.path.join(DATA_DIR, "reclamacoes.json")
            data = []
            if os.path.exists(local_file):
                with open(local_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data.append(item)
            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return jsonify({"status": "success", "message": "Reclamação registrada com sucesso."})
    except Exception as e:
        print("Erro ao salvar reclamação:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/report")
def relatorio():
    try:
        relatorio_path = os.path.join(DATA_DIR, "relatorio_latest.pdf")
        if os.path.exists(relatorio_path):
            return send_file(relatorio_path, as_attachment=True)
        return jsonify({"status": "error", "message": "Relatório não encontrado"}), 404
    except Exception as e:
        print("Erro ao enviar relatório:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/status")
def status():
    return jsonify({
        "sheets_enabled": SHEETS_ENABLED,
        "data_dir": DATA_DIR,
        "time": datetime.utcnow().isoformat() + "Z"
    })

# =============== MAIN ===================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
