from flask import Flask, render_template, request, send_from_directory
from docx import Document
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'static/contracts'
SABLONY_FOLDER = 'templates_word'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Smazání starých smluv
def smazat_stare_smlouvy(cesta, max_stari_dni=7):
    threshold = datetime.now() - timedelta(days=max_stari_dni)
    for filename in os.listdir(cesta):
        filepath = os.path.join(cesta, filename)
        if os.path.isfile(filepath):
            cas_zmeny = datetime.fromtimestamp(os.path.getmtime(filepath))
            if cas_zmeny < threshold:
                os.remove(filepath)

# Nahrazení ve formátovaných textech
def nahrad_v_paragrafech(paragraphs, nahrady):
    for p in paragraphs:
        for run in p.runs:
            for klic, hodnota in nahrady.items():
                if klic in run.text:
                    run.text = run.text.replace(klic, str(hodnota))  # Ensure replacement with string

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        smazat_stare_smlouvy(UPLOAD_FOLDER)

        # Načtení dat z formuláře
        nazev_akce = request.form['nazev_akce']
        cislo_akce = request.form['cislo_akce']
        vedouci = request.form['vedouci']
        tds = request.form['tds']
        datum_input = request.form['zahajeni']
        sablona = request.form['sablona']

        datum = datetime.strptime(datum_input, '%Y-%m-%d').strftime('%d. %m. %Y')

        nahrady = {
            '{{nazev_akce}}': nazev_akce,
            '{{cislo_akce}}': cislo_akce,
            '{{vedouci}}': vedouci,
            '{{TDS}}': tds,
            '{{zahajeni}}': datum
        }

        sablona_path = os.path.join(SABLONY_FOLDER, sablona + '.docx')
        if not os.path.exists(sablona_path):
            return "Šablona neexistuje.", 400

        doc = Document(sablona_path)
        nahrad_v_paragrafech(doc.paragraphs, nahrady)
        for section in doc.sections:
            nahrad_v_paragrafech(section.footer.paragraphs, nahrady)

        filename = f"{sablona}_{uuid.uuid4().hex}.docx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        doc.save(filepath)

        return render_template(
            'form.html',
            download_link='/' + filepath,
            data={
                'sablona': sablona,
                'nazev_akce': nazev_akce,
                'cislo_akce': cislo_akce,
                'vedouci': vedouci,
                'tds': tds,
                'zahajeni': datum_input
            }
        )

    return render_template('form.html')

@app.route('/static/contracts/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
