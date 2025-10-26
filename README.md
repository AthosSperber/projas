# ReclameAli+ (v4) 

## Como usar localmente
1. Crie virtualenv e ative:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) Google Sheets: coloque `service_account.json` na raiz `reclameali/` ou configure como Secret File no Render e compartilhe a planilha com o `client_email`.
4. Rode:
   ```bash
   python app.py
   ```
5. Abra http://localhost:5000

## Deploy no Render (resumo)
1. Crie Web Service apontando para este repositório.
2. Build: `pip install --upgrade pip && pip install -r requirements.txt`
3. Start: `gunicorn app:app`
4. Faça o primeiro deploy.
5. Em **Environment → Secret Files** adicione `service_account.json` com o conteúdo do JSON da conta de serviço (se usar Sheets).
6. Em **Environment Variables** adicione:
   - `GOOGLE_APPLICATION_CREDENTIALS=/opt/render/project/src/service_account.json`
   - `SHEET_NAME=reclameali_data`
   - `SMTP_HOST=smtp.gmail.com`
   - `SMTP_PORT=587`
   - `SMTP_USER=seu-email@gmail.com`
   - `SMTP_PASS=senha_de_app`
   - `MAIL_FROM=seu-email@gmail.com`


## Observações e troubleshooting
- Se o Sheets não gravar: confirme que o `client_email` da conta de serviço tem permissão de editor na planilha; confira logs no Render.
- Para Gmail, use senha de app (2FA ativado) e coloque em `SMTP_PASS`.
- Se precisar de ajuda para adaptar o seu `web e analise.py` original, cole-o na pasta `scripts/` e eu integro mantendo o formato do PDF.
