from flask import Flask, render_template, request, send_from_directory
from docx import Document
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/contracts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nazev_akce = request.form['nazev_akce']
        cislo_akce = request.form['cislo_akce']
        cislo_smlouvy = request.form['cislo_smlouvy']
        objednatel = request.form['objednatel']
        tds = request.form['tds']
        datum = request.form['datum']

        doc = Document('template.docx')
# Nahrazení v těle dokumentu
for p in doc.paragraphs:
    p.text = p.text.replace('{{nazev}}', nazev_akce)
    p.text = p.text.replace('{{cislo}}', cislo_akce)
    p.text = p.text.replace('{{ID_smlouvy}}', cislo_smlouvy)
    p.text = p.text.replace('{{objednatel}}', objednatel)
    p.text = p.text.replace('{{TDS}}', tds)
    p.text = p.text.replace('{{datum}}', datum)

# Nahrazení v zápatí (v každé sekci dokumentu)
for section in doc.sections:
    footer = section.footer
    for p in footer.paragraphs:
        p.text = p.text.replace('{{nazev}}', nazev_akce)
        p.text = p.text.replace('{{cislo}}', cislo_akce)
        p.text = p.text.replace('{{datum}}', datum)

        filename = f"smlouva_{uuid.uuid4().hex}.docx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        doc.save(filepath)

        return render_template('form.html', download_link=filepath)
    return render_template('form.html')
