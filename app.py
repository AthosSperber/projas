import os
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file

# Basic paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

DATA_FILE = os.path.join(BASE_DIR, "complaints.json")
RELATORIO_JSON = os.path.join(DATA_DIR, 'relatorio.json')
RELATORIO_PDF = os.path.join(DATA_DIR, 'relatorio_latest.pdf')

# try to import sheets handler (optional). if not available, functions will still work locally.
try:
    from sheets_handler import add_complaint, add_analysis, fetch_recent_analyses
    SHEETS_AVAILABLE = True
except Exception:
    SHEETS_AVAILABLE = False
    def add_complaint(nome,email,descricao):
        try:
            complaints = []
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE,'r',encoding='utf-8') as f:
                    complaints = json.load(f)
        except Exception:
            complaints = []
        complaints.append({
            "id": int(datetime.utcnow().timestamp()*1000),
            "nome": nome, "email": email, "descricao": descricao,
            "created_at": datetime.utcnow().isoformat()+"Z"
        })
        with open(DATA_FILE,'w',encoding='utf-8') as f:
            json.dump(complaints,f,ensure_ascii=False,indent=2)
    def add_analysis(pos,neu,neg):
        analyses_file = os.path.join(DATA_DIR, 'analyses.json')
        try:
            arr = []
            if os.path.exists(analyses_file):
                with open(analyses_file,'r',encoding='utf-8') as f:
                    arr = json.load(f)
        except Exception:
            arr = []
        arr.append({"time": datetime.utcnow().isoformat()+"Z","pos":pos,"neu":neu,"neg":neg})
        with open(analyses_file,'w',encoding='utf-8') as f:
            json.dump(arr,f,ensure_ascii=False,indent=2)
    def fetch_recent_analyses(limit=10):
        analyses_file = os.path.join(DATA_DIR, 'analyses.json')
        try:
            if os.path.exists(analyses_file):
                with open(analyses_file,'r',encoding='utf-8') as f:
                    arr = json.load(f)
                    return arr[-limit:]
        except Exception:
            pass
        return []

# -----------------------------
# Helper functions
# -----------------------------
def load_complaints_local():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_complaints_local(complaints):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(complaints, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar complaints local: {e}")

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if not nome or not email or not descricao:
        flash('Preencha todos os campos obrigatórios!', 'danger')
        return redirect(url_for('index'))

    try:
        if SHEETS_AVAILABLE:
            add_complaint(nome, email, descricao)
        else:
            save_complaints_local(load_complaints_local() + [{
                "id": int(datetime.utcnow().timestamp() * 1000),
                "nome": nome, "email": email, "descricao": descricao,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }])
    except Exception as e:
        print("Error saving complaint:", e)
        save_complaints_local(load_complaints_local() + [{
            "id": int(datetime.utcnow().timestamp() * 1000),
            "nome": nome, "email": email, "descricao": descricao,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }])

    flash('Reclamação enviada com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/complaints')
def complaints_view():
    complaints = sorted(load_complaints_local(), key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('complaints.html', complaints=complaints)

@app.route('/api/complaints')
def api_complaints():
    return jsonify(load_complaints_local())

# Relatório page (frontend)
@app.route('/relatorio')
def relatorio_page():
    return render_template('relatorio.html')

@app.route('/api/relatorio-data')
def api_relatorio_data():
    if not os.path.exists(RELATORIO_JSON):
        return jsonify({'error': 'relatorio not generated', 'message': 'Execute a análise primeiro via /admin/run-analysis'}), 404
    with open(RELATORIO_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/admin/run-analysis', methods=['POST'])
def run_analysis():
    script_path = os.path.join(BASE_DIR, 'scripts', 'web_analise.py')
    if not os.path.exists(script_path):
        return "Script de análise não encontrado. Coloque scripts/web_analise.py no projeto.", 500
    try:
        proc = subprocess.run(["python", script_path], cwd=BASE_DIR, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            print("STDOUT:", proc.stdout)
            print("STDERR:", proc.stderr)
            return f"Erro executando o script de análise: see server logs", 500
    except subprocess.TimeoutExpired:
        return "Execução do script excedeu o tempo limite.", 500
    json_exists = os.path.exists(RELATORIO_JSON)
    pdf_exists = os.path.exists(RELATORIO_PDF)
    return jsonify({
        'json': json_exists,
        'pdf': pdf_exists,
        'json_path': RELATORIO_JSON,
        'pdf_path': RELATORIO_PDF
    })

@app.route('/download/relatorio')
def download_relatorio():
    if not os.path.exists(RELATORIO_PDF):
        return redirect(url_for('relatorio_page'))
    return send_file(RELATORIO_PDF, as_attachment=True)

@app.route('/send-report-email', methods=['POST'])
def send_report_email():
    import smtplib
    from email.message import EmailMessage

    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({"error": "E-mail não informado."}), 400

    if not os.path.exists(RELATORIO_PDF):
        return jsonify({"error": "Relatório não encontrado. Gere o relatório antes de enviar."}), 404

    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    MAIL_FROM = os.environ.get('MAIL_FROM', SMTP_USER)

    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return jsonify({"error": "SMTP não configurado no servidor."}), 500

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Relatório ReclameAli+'
        msg['From'] = MAIL_FROM
        msg['To'] = email
        msg.set_content("Segue em anexo o relatório gerado pelo ReclameAli+.")

        with open(RELATORIO_PDF, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(RELATORIO_PDF))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return jsonify({"success": True, "message": f"Relatório enviado para {email}!"})
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return jsonify({"error": "Falha ao enviar e-mail."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
