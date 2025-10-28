
import os, subprocess, sys
from email_sender import send

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPER = os.path.join(BASE, 'scripts', 'scraper.py')
SENT = os.path.join(BASE, 'scripts', 'sentiment.py')
PDF = os.path.join(BASE, 'data', 'relatorio_latest.pdf')

def run_step(name, path):
    print(f"\n=== Executando {name} ===")
    res = subprocess.run([sys.executable, path], cwd=BASE)
    if res.returncode != 0:
        print(f"❌ {name} falhou com código {res.returncode}")
        sys.exit(res.returncode)
    print(f"✅ {name} concluído com sucesso.")

if __name__ == "__main__":
    run_step("scraper", SCRAPER)
    run_step("sentiment", SENT)

    if os.path.exists(PDF):
        print(f"\n📤 Enviando relatório: {PDF}")
        try:
            send(PDF, os.environ.get("REPORT_EMAIL", "seuemail@empresa.com"))
            print("✅ Relatório enviado com sucesso.")
        except Exception as e:
            print("⚠️ Falha ao enviar e-mail:", e)
    else:
        print("⚠️ Relatório PDF não encontrado.")
