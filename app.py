import os, json, subprocess, sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

REL_JSON = os.path.join(DATA_DIR, "relatorio.json")
REL_PDF = os.path.join(DATA_DIR, "relatorio_latest.pdf")
COMPLAINTS_FILE = os.path.join(BASE_DIR, "complaints.json")

# Optional Google Sheets integration
try:
    from sheets_handler import add_complaint, add_analysis, fetch_reclamacoes
    SHEETS = True
except Exception:
    SHEETS = False

def load_local_complaints():
    if not os.path.exists(COMPLAINTS_FILE):
        return []
    try:
        with open(COMPLAINTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_local_complaint(c):
    arr = load_local_complaints()
    arr.append(c)
    with open(COMPLAINTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome','').strip()
    email = request.form.get('email','').strip()
    descricao = request.form.get('descricao','').strip()
    if not nome or not email or not descricao:
        flash('Preencha todos os campos', 'danger')
        return redirect(url_for('index'))
    item = {"id": int(datetime.utcnow().timestamp()*1000), "nome": nome, "email": email, "descricao": descricao, "created_at": datetime.utcnow().isoformat()+"Z"}
    try:
        if SHEETS:
            add_complaint(nome, email, descricao)
        else:
            save_local_complaint(item)
    except Exception as e:
        print("Erro saving:", e)
        save_local_complaint(item)
    flash('Reclamação registrada. Obrigado!', 'success')
    return redirect(url_for('index'))

@app.route('/complaints')
def complaints():
    items = []
    if SHEETS:
        try:
            items = fetch_reclamacoes()
        except Exception as e:
            print("Sheets fetch error:", e)
            items = load_local_complaints()
    else:
        items = load_local_complaints()
    return render_template('complaints.html', complaints=items)

@app.route('/api/complaints-json')
def api_complaints_json():
    items = []
    if SHEETS:
        try:
            items = fetch_reclamacoes()
        except Exception as e:
            print("Sheets fetch error:", e)
            items = load_local_complaints()
    else:
        items = load_local_complaints()
    return jsonify(items)

@app.route('/relatorio')
def relatorio():
    return render_template('report.html')

@app.route('/admin/run-analysis', methods=['POST'])
def run_analysis():
    script = os.path.join(BASE_DIR, 'scripts', 'reconcile_and_run.py')
    if not os.path.exists(script):
        return jsonify({"error":"script not found"}), 500
    try:
        proc = subprocess.run([sys.executable, script], cwd=BASE_DIR, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            print("STDOUT:", proc.stdout)
            print("STDERR:", proc.stderr)
            return jsonify({"error":"analysis failed", "stdout": proc.stdout, "stderr": proc.stderr}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error":"timeout"}), 500
    exists_json = os.path.exists(REL_JSON)
    exists_pdf = os.path.exists(REL_PDF)
    # attempt to push summary to sheets if available
    try:
        if SHEETS and exists_json:
            with open(REL_JSON,'r',encoding='utf-8') as f:
                data = json.load(f)
            items = data.get('items',[])
            pos = sum(1 for it in items if it.get('Sentimento')=='positivo')
            neu = sum(1 for it in items if it.get('Sentimento')=='neutro')
            neg = sum(1 for it in items if it.get('Sentimento')=='negativo')
            add_analysis(pos, neu, neg)
    except Exception as e:
        print("Failed to write analysis to sheets:", e)
    return jsonify({"json": exists_json, "pdf": exists_pdf})

@app.route('/api/relatorio-data')
def api_relatorio_data():
    if not os.path.exists(REL_JSON):
        return jsonify({"error":"not generated"}), 404
    with open(REL_JSON,'r',encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/download/relatorio')
def download_relatorio():
    if not os.path.exists(REL_PDF):
        flash('Relatório ainda não gerado', 'warning')
        return redirect(url_for('relatorio'))
    return send_file(REL_PDF, as_attachment=True)

@app.route('/send-report-email', methods=['POST'])
def send_report_email():
    from email.message import EmailMessage
    import smtplib
    data = request.get_json() or {}
    to = data.get('email')
    if not to:
        return jsonify({"error":"email missing"}), 400
    if not os.path.exists(REL_PDF):
        return jsonify({"error":"report missing"}), 404
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    MAIL_FROM = os.environ.get('MAIL_FROM', SMTP_USER)
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return jsonify({"error":"smtp not configured"}), 500
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Relatório ReclameAli+'
        msg['From'] = MAIL_FROM
        msg['To'] = to
        msg.set_content('Segue em anexo o relatório gerado pelo ReclameAli+.')
        with open(REL_PDF, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(REL_PDF))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return jsonify({"success": True})
    except Exception as e:
        print("Email send error:", e)
        return jsonify({"error":"send failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
