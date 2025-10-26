#!/usr/bin/env python3
import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
MAIL_FROM = os.environ.get('MAIL_FROM', SMTP_USER)

def send_pdf(path_pdf, to_email):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        raise RuntimeError("SMTP not configured")
    msg = EmailMessage()
    msg['Subject'] = 'Relatório ReclameAli+'
    msg['From'] = MAIL_FROM
    msg['To'] = to_email
    msg.set_content('Segue o relatório em anexo.')
    with open(path_pdf,'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(path_pdf))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    print("Sent report to", to_email)

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.dirname(__file__)),'data','relatorio_latest.pdf')
    send_pdf(path, os.environ.get('MAIL_TO','you@example.com'))
