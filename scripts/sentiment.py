#!/usr/bin/env python3
import os, json
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

INPUT = os.path.join(DATA_DIR, 'scraped_comments.csv')
OUT_JSON = os.path.join(DATA_DIR, 'relatorio.json')
OUT_PDF = os.path.join(DATA_DIR, 'relatorio_latest.pdf')

def classify_vader(texts):
    try:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        import nltk
        nltk.download('vader_lexicon', quiet=True)
        sia = SentimentIntensityAnalyzer()
    except Exception as e:
        print("VADER unavailable:", e)
        return [{'label':'neutro','score':0.0} for _ in texts]
    res = []
    for t in texts:
        s = sia.polarity_scores(str(t))['compound']
        if s >= 0.25:
            lab = 'positivo'
        elif s <= -0.25:
            lab = 'negativo'
        else:
            lab = 'neutro'
        res.append({'label':lab,'score':float(s)})
    return res

def generate_pdf(df, out_pdf):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
    except Exception as e:
        print("ReportLab unavailable:", e)
        return False
    doc = SimpleDocTemplate(out_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Relatório de Sentimento", styles['Title']))
    elements.append(Paragraph(f"Gerado em {datetime.now().isoformat()}", styles['Normal']))
    elements.append(Spacer(1,12))
    summary = df['Sentimento'].value_counts().to_dict()
    total = len(df)
    table_data = [['Sentimento','Contagem','Percentual']]
    for k,v in summary.items():
        table_data.append([k, str(v), f"{(v/total*100):.2f}%"])
    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1E90FF')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    elements.append(t)
    elements.append(Spacer(1,12))
    rows = [['Comentário','Sentimento','Confiança']]
    for _,r in df.head(200).iterrows():
        rows.append([str(r.get('texto',''))[:150], r.get('Sentimento',''), str(r.get('Confianca',''))])
    t2 = Table(rows, colWidths=[300,80,80])
    t2.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.black),('FONTSIZE',(0,0),(-1,-1),8)]))
    elements.append(t2)
    try:
        doc.build(elements)
        return True
    except Exception as e:
        print("PDF build error:", e)
        return False

def main():
    if not os.path.exists(INPUT):
        print("Input CSV not found at", INPUT)
        return 1
    df = pd.read_csv(INPUT, engine='python', on_bad_lines='skip')
    text_col = None
    for c in ['texto','text','quote','Quote','reclamacao','comentario']:
        if c in df.columns:
            text_col = c
            break
    if text_col is None:
        text_col = df.columns[0]
    texts = df[text_col].astype(str).tolist()
    results = classify_vader(texts)
    labels = [r['label'] for r in results]
    scores = [r.get('score',0.0) for r in results]
    df['Sentimento'] = labels
    df['Confianca'] = scores
    df = df.rename(columns={text_col:'texto'})
    records = df.to_dict(orient='records')
    with open(OUT_JSON,'w',encoding='utf-8') as f:
        json.dump({'generated_at': datetime.now().isoformat(), 'total': len(records), 'items': records}, f, ensure_ascii=False, indent=2)
    ok = generate_pdf(df, OUT_PDF)
    if ok:
        print("PDF generated:", OUT_PDF)
    else:
        print("PDF generation failed.")
    # try write to sheets
    try:
        from sheets_handler import add_analysis
        pos = sum(1 for r in records if r.get('Sentimento')=='positivo')
        neu = sum(1 for r in records if r.get('Sentimento')=='neutro')
        neg = sum(1 for r in records if r.get('Sentimento')=='negativo')
        add_analysis(pos,neu,neg)
    except Exception as e:
        print("Sheets write skipped:", e)
    return 0

if __name__ == '__main__':
    exit(main())
