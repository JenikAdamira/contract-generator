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
        nazev_akce_final = verejna_zakazka if akce_count >= 2 and verejna_zakazka else (nazvy_akci[0] if nazvy_akci else "")
        cislo_akce_final = ", ".join(cisla_akci)

        vice_akci = ""
        if akce_count >= 2:
            vice_akci = "Tato zakázka se skládá ze dvou níže uvedených jednotlivých akcí:\n"
            for cislo, nazev in zip(cisla_akci, nazvy_akci):
                if cislo and nazev:
                    vice_akci += f"č. {cislo} {nazev}\n"

        seznam_akci = [{"cislo": cislo, "nazev": nazev} for cislo, nazev in zip(cisla_akci, nazvy_akci) if cislo and nazev and akce_count >= 2]

        bz_ne = request.form["bz"] == "NE"
        bz_text = (
            "Zhotovitel předložil objednateli v den podpisu smlouvy o dílo originál bankovní záruky za prove-dení díla podle ustanovení čl. 7 Bankovní záruka, odst. 7.1. Obchodních podmínek objednatele na zhotovení stavby ze dne 1. 1. 2024. Objednatel potvrzuje podpisem smlouvy převzetí listiny."
            if not bz_ne else
            "Objednatel nežádá zhotovitele o předložení bankovní záruky za provedení díla."
        )

        vyh_text = ""
        vyh_placeholder = ""
        vz1 = ""
        vz2 = ""
        if request.form["vyh"] == "ANO":
            vyh_text = "Smluvní strany se dohodly na vyhrazené změně závazku v souladu s ustanovením § 100 odst. 1 a § 222 odst. 2 zákona č. 134/2016 Sb., o zadávání veřejných zakázek, ve znění pozdějších předpisů, spočívající v tom, že pokud u položek uvedených v tabulce „Souhrn vyhrazených položek“ dojde k naměření jiného množství, než bylo předpokládáno výkazem výměr, platí pro účely fakturace naměřená hodnota, avšak maximálně do výše limitů stanovených jako 50 % víceprací a 50 % méněprací v rámci všech podle tohoto dokumentu označených položek výkazu výměr. Měření musí být evidováno ve formě Evidenčního listu vyhrazené změny, což je samostatný dokument obsahující přehled skutečně naměřených množství jednotlivých položek výkazu výměr, pokud se liší od původního předpokladu, přičemž vyhrazené změny lze uplatnit pouze v souladu s uvedenými limity."
            vyh_placeholder = "Do vygenerované smlouvy vlož Souhrn vyhrazených položek"
            vz1 = "(překročitelná jen při uplatnění vyhrazených změn v čl. 8.10. smlouvy a dále v režimu zákona)"
            vz2 = "(jedná se o cenu díla před aktivací změn vyhrazených v čl. 8.10. smlouvy)"
        else:
            vyh_text = "Vymaž tento odstavec"

        pd_map = {
            "zjednodusena": "zjednodušenou projektovou dokumentací",
            "provadeci": "projektovou dokumentací pro provedení stavby"
        }

        pds = []
        pd_count = int(request.form.get("pd_count", 1))
        for i in range(1, pd_count + 1):
            if i == 1:
                typ = request.form.get("pd")
                rok = request.form.get("pdrok")
                spolecnost = request.form.get("pdspolecnost")
                sidlo = request.form.get("pdsidlo")
                projektant = request.form.get("pdproj")
            else:
                typ = request.form.get(f"pd_{i}")
                rok = request.form.get(f"pdrok_{i}")
                spolecnost = request.form.get(f"pdspolecnost_{i}")
                sidlo = request.form.get(f"pdsidlo_{i}")
                projektant = request.form.get(f"pdproj_{i}")

            pd_typ_text = pd_map.get(typ, "")
            if all([pd_typ_text, rok, spolecnost, sidlo, projektant]):
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

        if request.form.get("neg_kaceni") == "ANO":
            kaceni_text = [
                "Zhotovitel se zavazuje k odkupu veškeré přebytečné dřevní hmoty v majetku objednatele vzniklé během realizace stavby a k jejímu vymístění mimo stavbu. Jedná se o přebytečné kmeny, křoví a větve z odstraňovaných stromů i keřů, pro které není dle projektové dokumentace jiné využití v místě stavby."
                "Cenu za odkup dřevní hmoty zhotovitel adekvátně ponížil o veškeré doprovodné náklady spojené s vymístěním dřevní hmoty ze stavby. Cenu za odkup zhotovitel vyjádřil adekvátním oceněním příslušné položky v objektu SO 2.7.1 - Oprava opevnění „Zisk objednatele za odkup přebytečné dřevní hmoty zhotovitelem“ v soupisu prací stavby."
        ]
        else:
            kaceni_text = ["Odstavec vymazat"]

        listiny = [request.form.get(f"listina_{i}") for i in range(1, int(request.form["listiny_count"]) + 1) if request.form.get(f"listina_{i}")]

        negace = []
        if request.form.get("neg_geom") == "NE":
            negace.append("čl. 2... písm. a)... body 4., 5.")
        cl_2_f_body = []
        if request.form.get("neg_kaceni") == "NE":
            cl_2_f_body.append("35")
        if request.form.get("neg_pruzkum") == "NE":
            cl_2_f_body.append("38")
        if request.form.get("neg_kzp") == "NE":
            cl_2_f_body.append("45")
        if cl_2_f_body:
            def spoj_body(b):
                if len(b) == 1:
                    return b[0]
                return ", ".join(b[:-1]) + " a " + b[-1]
            negace.append(f"čl. 2... písm. f)... body {spoj_body(cl_2_f_body)}")

        if bz_ne:
            negace.append("čl. 7. Bankovní záruka")

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
            negace.append(f"čl. 12... písm. {spoj_pismena(cl_12_pismena)}")

        if request.form.get("neg_dotace") == "NE":
            negace.append("čl. 14... odst. 14.3 a 14.4")

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
            "kaceni": kaceni_text,
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
