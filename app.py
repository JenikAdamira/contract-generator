from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate
import io
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Bankovní záruka
        bz_text = (
            "Zhotovitel předložil objednateli v den podpisu smlouvy o dílo originál bankovní "
            "záruky za provedení díla podle ustanovení čl. 7 Bankovní záruka, odst. 7.1. Obchodních podmínek "
            "objednatele na zhotovení stavby ze dne 1. 1. 2024. Objednatel potvrzuje podpisem smlouvy převzetí listiny."
        ) if request.form["bz"] == "ANO" else (
            "Objednatel nežádá zhotovitele o předložení bankovní záruky za provedení díla."
        )

        # Vyhrazené položky
        vyh_text = ""
        vyh_rows = []
        vz1 = ""
        vz2 = ""
        if request.form["vyh"] == "ANO":
            vyh_text = (
                "Smluvní strany se dohodly na vyhrazené změně závazku v souladu s ustanovením § 100 odst. 1 a § 222 odst. 2 "
                "zákona č. 134/2016 Sb., o zadávání veřejných zakázek..."
            )
            vz1 = "(překročitelná jen při uplatnění vyhrazených změn v čl. 8.10. smlouvy a dále v režimu zákona)"
            vz2 = "(jedná se o cenu díla před aktivací změn vyhrazených v čl. 8.10. smlouvy)"

            count = int(request.form["vyh_count"])
            for i in range(1, count + 1):
                so = request.form.get(f"so_{i}")
                polozky = request.form.get(f"polozky_{i}")
                if so or polozky:
                    vyh_rows.append({"so": so, "polozky": polozky})

        # Projektová dokumentace typ
        pd_map = {
            "zjednodusena": "zjednodušenou projektovou dokumentací",
            "provadeci": "projektovou dokumentací pro provedení stavby"
        }
        pd_text = pd_map.get(request.form["pd"], "")

        # Termín dokončení díla
        if request.form["dokonceni_typ"] == "datum":
            dokonceni = f"nejpozději do {request.form['dokonceni_datum']}"
        else:
            dokonceni = request.form["dokonceni_text"]

        context = {
            "cislo_akce": request.form["cislo_akce"],
            "nazev_akce": request.form["nazev_akce"],
            "vedouci": request.form["vedouci"],
            "dozor": request.form["dozor"],
            "zahajeni": request.form["zahajeni"],
            "bz": bz_text,
            "poj": request.form["poj"],
            "vyh_text": vyh_text,
            "vyh_tabulka": vyh_rows,
            "vz1": vz1,
            "vz2": vz2,
            "pd": pd_text,
            "pdrok": request.form["pdrok"],
            "pdspolecnost": request.form["pdspolecnost"],
            "pdsidlo": request.form["pdsidlo"],
            "pdproj": request.form["pdproj"],
            "dokonceni": dokonceni
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
