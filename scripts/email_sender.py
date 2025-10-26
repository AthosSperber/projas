#!/usr/bin/env python3
import os, smtplib
from email.message import EmailMessage
def send(path, to):
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT',587))
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    MAIL_FROM = os.environ.get('MAIL_FROM', SMTP_USER)
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        raise RuntimeError("SMTP not configured")
    msg = EmailMessage()
    msg['Subject']='Relatório ReclameAli+'
    msg['From']=MAIL_FROM; msg['To']=to
    msg.set_content('Segue em anexo o relatório.')
    with open(path,'rb') as f: msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(path))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(); s.login(SMTP_USER, SMTP_PASS); s.send_message(msg)
if __name__=='__main__':
    import sys
    send(sys.argv[1], sys.argv[2])
