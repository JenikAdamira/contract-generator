from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate
import io
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        bz_choice = request.form["bz"]
        vyh_choice = request.form["vyh"]
        pojistka = request.form["poj"]

        # Bankovní záruka
        bz_text = (
            "Zhotovitel předložil objednateli v den podpisu smlouvy o dílo originál bankovní "
            "záruky za provedení díla podle ustanovení čl. 7 Bankovní záruka, odst. 7.1. Obchodních podmínek "
            "objednatele na zhotovení stavby ze dne 1. 1. 2024. Objednatel potvrzuje podpisem smlouvy převzetí listiny."
        ) if bz_choice == "ANO" else (
            "Objednatel nežádá zhotovitele o předložení bankovní záruky za provedení díla."
        )

        # Vyhrazené změny – text a tabulka
        vyh_text = ""
        vyh_rows = []
        vz1 = ""
        vz2 = ""

        if vyh_choice == "ANO":
            vyh_text = (
                "Smluvní strany se dohodly na vyhrazené změně závazku v souladu s ustanovením § 100 odst. 1 a § 222 odst. 2 "
                "zákona č. 134/2016 Sb., o zadávání veřejných zakázek, ve znění pozdějších předpisů, spočívající v tom, že pokud u položek "
                "uvedených v tabulce „Souhrn vyhrazených položek“ dojde k naměření jiného množství, než bylo předpokládáno výkazem výměr, platí "
                "pro účely fakturace naměřená hodnota, avšak maximálně do výše limitů stanovených jako 50 % víceprací a 50 % méněprací v rámci všech podle tohoto dokumentu označených položek výkazu výměr. "
                "Měření musí být evidováno ve formě Evidenčního listu vyhrazené změny, což je samostatný dokument obsahující přehled skutečně naměřených množství jednotlivých položek výkazu výměr, pokud se liší od původního předpokladu, přičemž vyhrazené změny lze uplatnit pouze v souladu s uvedenými limity."
            )
            vz1 = "(překročitelná jen při uplatnění vyhrazených změn v čl. 8.10. smlouvy a dále v režimu zákona)"
            vz2 = "(jedná se o cenu díla před aktivací změn vyhrazených v čl. 8.10. smlouvy)"

            count = int(request.form["vyh_count"])
            for i in range(1, count + 1):
                so = request.form.get(f"so_{i}")
                polozky = request.form.get(f"polozky_{i}")
                if so or polozky:
                    vyh_rows.append({
                        "so": so,
                        "polozky": polozky
                    })

        context = {
            "cislo_akce": request.form["cislo_akce"],
            "nazev_akce": request.form["nazev_akce"],
            "vedouci": request.form["vedouci"],
            "dozor": request.form["dozor"],
            "zahajeni": request.form["zahajeni"],
            "bz": bz_text,
            "poj": pojistka,
            "vyh_text": vyh_text,
            "vyh_tabulka": vyh_rows,
            "vz1": vz1,
            "vz2": vz2
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
