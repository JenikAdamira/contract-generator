from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate
import io
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        akce_count = int(request.form["akce_count"])
        nazvy_akci = [request.form.get(f"nazev_akce_{i}") for i in range(1, akce_count + 1) if request.form.get(f"nazev_akce_{i}")]
        cisla_akci = [request.form.get(f"cislo_akce_{i}") for i in range(1, akce_count + 1) if request.form.get(f"cislo_akce_{i}")]

        verejna_zakazka = request.form.get("verejna_zakazka", "").strip()

        if akce_count >= 2 and verejna_zakazka:
            nazev_akce_final = verejna_zakazka
        elif nazvy_akci:
            nazev_akce_final = nazvy_akci[0]
        else:
            nazev_akce_final = ""

        cislo_akce_final = ", ".join(cisla_akci)

        vice_akci = ""
        if akce_count >= 2:
            vice_akci = "která se skládá ze dvou níže uvedených jednotlivých akcí:\n"
            for cislo, nazev in zip(cisla_akci, nazvy_akci):
                if cislo and nazev:
                    vice_akci += f"č. {cislo} {nazev}\n"

        seznam_akci = [{"cislo": cislo, "nazev": nazev} for cislo, nazev in zip(cisla_akci, nazvy_akci) if cislo and nazev and akce_count >= 2]

        bz_ne = request.form["bz"] == "NE"
        bz_text = (
            "Zhotovitel předložil objednateli v den podpisu smlouvy o dílo originál bankovní záruky za provedení díla v souladu se zněním čl. 7. Bankovní záruka, odst. 7.1. Obchodních podmínek na zhotovení stavby ze dne 1. 1. 2024. Objednatel potvrzuje podpisem smlouvy převzetí listiny."
            if not bz_ne else
            "Objednatel nežádá zhotovitele o předložení bankovní záruky za provedení díla."
        )

        vyh_text = ""
        vyh_placeholder = ""
        vz1 = ""
        vz2 = ""
        if request.form["vyh"] == "ANO":
            vyh_text = "Smluvní strany se dohodly na vyhrazené změně závazku..."
            vyh_placeholder = "Do vygenerované smlouvy vlož Souhrn vyhrazených položek"
            vz1 = "(překročitelná jen při uplatnění vyhrazených změn...)"
            vz2 = "(jedná se o cenu díla před aktivací změn...)"
        else:
            vyh_text = "Vymaž tento odstavec"

        pd_map = {
            "zjednodusena": "zjednodušenou projektovou dokumentací",
            "provadeci": "projektovou dokumentací pro provedení stavby"
        }

        pds = []
        pd_count = int(request.form.get("pd_count", 1))
        for i in range(1, pd_count + 1):
            typ = request.form.get("pd" if i == 1 else f"pd_{i}")
            rok = request.form.get("pdrok" if i == 1 else f"pdrok_{i}")
            spolecnost = request.form.get("pdspolecnost" if i == 1 else f"pdspolecnost_{i}")
            sidlo = request.form.get("pdsidlo" if i == 1 else f"pdsidlo_{i}")
            projektant = request.form.get("pdproj" if i == 1 else f"pdproj_{i}")
            pd_typ_text = pd_map.get(typ, "")

            if pd_typ_text and rok and spolecnost and sidlo and projektant:
                pds.append({
                    "typ": pd_typ_text,
                    "rok": rok,
                    "spolecnost": spolecnost,
                    "sidlo": sidlo,
                    "projektant": projektant,
                    "akce": nazev_akce_final
                })

        projekt_parts = [
            f'{pd["typ"]} vypracovanou v roce {pd["rok"]} společností {pd["spolecnost"]}, se sídlem {pd["sidlo"]}, zodpovědný projektant {pd["projektant"]}'
            for pd in pds
        ]
        projekt_text = " a ".join(projekt_parts)

        if request.form["dokonceni_typ"] == "datum":
            datum_raw = request.form["dokonceni_datum"]
            try:
                parsed = datetime.strptime(datum_raw, "%Y-%m-%d")
                datum_cz = parsed.strftime("%d.%m.%Y")
                dokonceni = f"nejpozději do {datum_cz}"
            except ValueError:
                dokonceni = f"nejpozději do {datum_raw} (chybný formát data)"
        else:
            dokonceni = request.form["dokonceni_text"]

        listiny = [request.form.get(f"listina_{i}") for i in range(1, int(request.form["listiny_count"]) + 1) if request.form.get(f"listina_{i}")]

        negace = []

        if request.form.get("neg_geom") == "NE":
            negace.append("čl. 2. Všeobecné povinnosti zhotovitele, odst. 2.3., písm. a) Dokumentace, povodňové plány, geodetické práce, body 4., 5.")
        if request.form.get("neg_kaceni") == "NE":
            negace.append("čl. 2. Všeobecné povinnosti zhotovitele, odst. 2.3., písm. f) Ostatní podmínky, bod 35")
        if request.form.get("neg_pruzkum") == "NE":
            negace.append("čl. 2. Všeobecné povinnosti zhotovitele, odst. 2.3., písm. f) Ostatní podmínky, bod 38")
        if request.form.get("neg_kzp") == "NE":
            negace.append("čl. 2. Všeobecné povinnosti zhotovitele, odst. 2.3., písm. f) Ostatní podmínky, bod 45")

        if bz_ne:
            negace.append("čl. 7. Bankovní záruka")

        cl_12_pismena = []
        if request.form.get("neg_geom") == "NE":
            cl_12_pismena.append("c)")
        if request.form.get("neg_kzp") == "NE":
            cl_12_pismena.append("e)")
        if request.form.get("neg_reviz") == "NE":
            cl_12_pismena.append("m)")

cl_12_pismena = []
        if request.form.get("neg_geom") == "NE":
            cl_12_pismena.append("c)")
        if request.form.get("neg_kzp") == "NE":
            cl_12_pismena.append("e)")
        if request.form.get("neg_reviz") == "NE":
            cl_12_pismena.append("m)")

        if cl_12_pismena:
            def spoj_pismena(seznam):
                if len(seznam) == 1:
                    return seznam[0]
                return ", ".join(seznam[:-1]) + " a " + seznam[-1]
            pismena_text = spoj_pismena(cl_12_pismena)
            negace.append(f"čl. 12. Předání díla, odst. 12.2., písm. {pismena_text}")

        if request.form.get("neg_dotace") == "NE":
            negace.append("čl. 14. Odstoupení od smlouvy, odst. 14. 3. a 14. 4.")

        for i in range(1, int(request.form["negace_count"]) + 1):
            val = request.form.get(f"negace_{i}")
            if val:
                negace.append(val)

        context = {
            "nazev_akce": nazev_akce_final,
            "cislo_akce": cislo_akce_final,
            "vedouci": request.form["vedouci"],
            "dozor": request.form["dozor"],
            "zahajeni": request.form["zahajeni"],
            "bz": bz_text,
            "poj": request.form["poj"],
            "vyh_text": vyh_text,
            "vyh_placeholder": vyh_placeholder,
            "vz1": vz1,
            "vz2": vz2,
            "dokonceni": dokonceni,
            "listiny": listiny,
            "negace": negace,
            "vice_akci": vice_akci.strip(),
            "seznam_akci": seznam_akci,
            "pd_seznam": pds,
            "projekt": projekt_text,
        }

        sablona = request.form["sablona"]
        doc = DocxTemplate(sablona)
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
