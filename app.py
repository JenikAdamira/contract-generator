from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate
import io
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Rozhodnutí o bankovní záruce
        bz_choice = request.form["bz"]
        if bz_choice == "ANO":
            bz_text = (
                "6.1.\tZhotovitel předložil objednateli v den podpisu smlouvy o dílo originál bankovní "
                "záruky za provedení díla podle ustanovení čl. 7 Bankovní záruka, odst. 7.1. Obchodních podmínek "
                "objednatele na zhotovení stavby ze dne 1. 1. 2024. Objednatel potvrzuje podpisem smlouvy převzetí listiny."
            )
        else:
            bz_text = (
                "Objednatel nežádá zhotovitele o předložení bankovní záruky za provedení díla."
            )

        context = {
            "cislo_akce": request.form["cislo_akce"],
            "nazev_akce": request.form["nazev_akce"],
            "vedouci": request.form["vedouci"],
            "dozor": request.form["dozor"],
            "zahajeni": request.form["zahajeni"],
            "bz": bz_text,
            "poj": request.form["poj"]
        }

        doc = DocxTemplate("SOD_PS24.docx")
        doc.render(context)

        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        filename = f"Smlouva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        return send_file(output, as_attachment=True, download_name=filename)

    return render_template("form.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
