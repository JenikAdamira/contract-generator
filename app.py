from flask import Flask, render_template, request, send_from_directory
from docx import Document
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'static/contracts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def nahrad_v_paragrafech(paragraphs, nahrady):
    for p in paragraphs:
        for run in p.runs:
            for klic, hodnota in nahrady.items():
                if klic in run.text:
                    run.text = run.text.replace(klic, hodnota)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nazev_akce = request.form['nazev_akce']
        cislo_akce = request.form['cislo_akce']
        cislo_smlouvy = request.form['cislo_smlouvy']
        objednatel = request.form['objednatel']
        tds = request.form['tds']
        datum = request.form['datum']

        nahrady = {
            '{{nazev}}': nazev_akce,
            '{{cislo}}': cislo_akce,
            '{{ID_smlouvy}}': cislo_smlouvy,
            '{{objednatel}}': objednatel,
            '{{TDS}}': tds,
            '{{datum}}': datum
        }

        doc = Document('template.docx')

        # Nahrazení v textu dokumentu se zachováním formátu
        nahrad_v_paragrafech(doc.paragraphs, nahrady)

        for section in doc.sections:
            nahrad_v_paragrafech(section.footer.paragraphs, nahrady)

        filename = f"smlouva_{uuid.uuid4().hex}.docx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        doc.save(filepath)

        return render_template('form.html', download_link='/' + filepath)

    return render_template('form.html')


@app.route('/static/contracts/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
