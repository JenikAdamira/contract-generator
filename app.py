from flask import Flask, render_template, request, send_from_directory
from docx import Document
import os
import uuid

app = Flask(__name__)

# Složka, kam se ukládají smlouvy
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

        # Načtení šablony a nahrazení značek
        doc = Document('template.docx')

        # Tělo dokumentu
        for p in doc.paragraphs:
            p.text = p.text.replace('{{nazev}}', nazev_akce)
            p.text = p.text.replace('{{cislo}}', cislo_akce)
            p.text = p.text.replace('{{ID_smlouvy}}', cislo_smlouvy)
            p.text = p.text.replace('{{objednatel}}', objednatel)
            p.text = p.text.replace('{{TDS}}', tds)
            p.text = p.text.replace('{{datum}}', datum)

        # Zápatí (pro všechny sekce dokumentu)
        for section in doc.sections:
            footer = section.footer
            for p in footer.paragraphs:
                p.text = p.text.replace('{{nazev}}', nazev_akce)
                p.text = p.text.replace('{{cislo}}', cislo_akce)
                p.text = p.text.replace('{{datum}}', datum)

        # Uložení dokumentu s unikátním názvem
        filename = f"smlouva_{uuid.uuid4().hex}.docx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        doc.save(filepath)

        return render_template('form.html', download_link='/' + filepath)

    return render_template('form.html')


# Pro stahování souboru
@app.route('/static/contracts/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
