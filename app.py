from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate
import io
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        context = {
            "cislo_akce": request.form["cislo_akce"],
            "nazev_akce": request.form["nazev_akce"],
            "vedouci": request.form["vedouci"],
            "dozor": request.form["dozor"],
            "zahajeni": request.form["zahajeni"],
        }

        doc = DocxTemplate("SOD_PS24.docx")
        doc.render(context)

        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        filename = f"Smlouva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        return send_file(output, as_attachment=True, download_name=filename)

    return render_template("form.html")
