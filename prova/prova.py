"""
Pagina di prova: renderizza il guscio con contenuto finto, senza Flask e
senza agganciare un'app.

    python3 prova/prova.py

Scrive prova/uscita/lite.html e prova/uscita/master.html, da aprire nel
browser. Oltre a farli vedere, controlla le cose che a occhio non si
notano: il <nav class="menu"> assente in lite, il blocco avviso che
sparisce quando lo slot e' vuoto, il blocco legale sempre presente.
"""

import pathlib
import sys

from jinja2 import Environment, FileSystemLoader

RADICE = pathlib.Path(__file__).resolve().parent.parent
USCITA = RADICE / "prova" / "uscita"


# Il guscio chiede all'app il proprio marchio sotto un nome fisso. Qui
# l'app finta e' allergeni-calc: le prendiamo i file veri da disco, cosi'
# la prova mostra anche che la convenzione sui nomi regge.
APP_FINTA = RADICE.parent / "allergeni-calc" / "static"


def url_for(endpoint, filename=""):
    """Sostituto di quello di Flask: qui gli statici si leggono da disco."""
    if endpoint == "cosmetech_ui.static":
        return f"../../cosmetech_ui/static/{filename}"
    if endpoint == "static":
        return f"../../../allergeni-calc/static/{filename}"
    raise AssertionError(f"endpoint inatteso nel guscio: {endpoint}")


# Il riquadro tratteggiato del prototipo: e' scenografia della prova, non
# fa parte del guscio, quindi vive qui e passa dallo slot `testa`.
STILE_PROVA = """
  <style>
    .slot {
      border:2px dashed var(--filetto); border-radius: var(--radius);
      background: var(--tenue); min-height:330px;
      display:flex; align-items:center; justify-content:center;
      text-align:center; color: var(--testo-tenue);
    }
    .slot strong { display:block; font-family: var(--font-titoli);
                   font-size:20px; color: var(--c4-titoli); margin-bottom:8px; }
    .slot span { font-size:14px; }
  </style>
"""

# La riga che un'app vera scriverebbe nel proprio foglio: solo le quattro.
PALETTE_VERDE = """
  <style>
    :root { --c1-fondo:#1d4d3b; --c2-menu:#153a2c;
            --c3-pulsante:#2f8f68; --c4-titoli:#1d4d3b; }
  </style>
"""

CONTENUTO = """
      <div class="slot">
        <div>
          <strong>Contenuto dell'app</strong>
          <span>Larghezza piena fino a 1180px, oppure colonna centrale da 880px.<br>
          Card, pulsanti, campi e filetti arrivano gia' dal container.</span>
        </div>
      </div>
"""

FOOTER_APP = (
    "Slot dell'app — qui allergeni-calc mette cio' che le serve: versione "
    "del dizionario delle sostanze, riferimenti normativi, note di metodo, "
    "limiti dello strumento."
)

PAGINE = {
    # nome file : (guscio esteso, blocchi dell'app finta)
    "lite.html": ("lite.html", {
        "testa": STILE_PROVA,
        "utente": "<strong>Riccardo</strong> · Formulatore, cosmetologo · "
                  "<a href='#'>esci</a>",
        "avviso": "",
        "footer_app": FOOTER_APP,
    }),
    "master.html": ("master.html", {
        "marchio_app": '<span class="nome">AllergeniCalc</span>',
        # qui l'app ridefinisce anche la palette, per mostrare che bastano
        # le quattro variabili a cambiare famiglia di colore
        "testa": STILE_PROVA + PALETTE_VERDE,
        "utente": "<strong>Riccardo</strong> · piano <span>Pro</span> · "
                  "<a href='#'>esci</a>",
        "avviso": "Anteprima tecnica — il dizionario normativo e' in fase di "
                  "validazione, alcune sostanze possono risultare non coperte.",
        "menu": "<li><a href='#' class='attivo'>Calcolo</a></li>"
                "<li><a href='#'>Le mie schede</a></li>"
                "<li><a href='#'>Impostazioni</a></li>"
                "<li><a href='#'>Novita'</a></li>",
        "footer_app": FOOTER_APP,
    }),
}


def sorgente(base, blocchi):
    """Costruisce al volo il template di un'app finta che estende il guscio."""
    righe = [f'{{% extends "{base}" %}}']
    righe.append(
        "{% block titolo %}Quali allergeni devi dichiarare in etichetta"
        "{% endblock %}"
    )
    righe.append(
        "{% block sottotitolo %}Reg. UE 2023/1545 · soglie leave-on e "
        "rinse-off{% endblock %}"
    )
    for nome, testo in blocchi.items():
        righe.append(f"{{% block {nome} %}}{testo}{{% endblock %}}")
    righe.append("{% block contenuto %}" + CONTENUTO + "{% endblock %}")
    return "\n".join(righe)


def controlla(reso):
    guasti = []
    lite, master = reso["lite.html"], reso["master.html"]

    if '<nav class="menu">' in lite:
        guasti.append("lite emette la barra del menu: non deve esistere")
    if '<nav class="menu">' not in master:
        guasti.append("master non emette il menu pieno")
    if 'class="avviso"' in lite:
        guasti.append("l'avviso vuoto lascia comunque il suo blocco")
    if 'class="avviso"' not in master:
        guasti.append("l'avviso pieno non compare")
    if "piano <span>" in lite:
        guasti.append("lite mostra il riconoscimento in formato SSO")

    for nome, html in reso.items():
        for atteso, cosa in [
            ("Uno strumento", "occhiello del garante"),
            ("P. IVA IT02924640648", "blocco legale"),
            ('class="social"', "fascia social"),
            ("pieno-2", "slot dell'app nel footer"),
            ("cosmetech-ui.css", "foglio del pacchetto"),
            ("img/favicon.ico", "favicon dell'app"),
            ("img/icona-128.png", "icona dell'app"),
        ]:
            if atteso not in html:
                guasti.append(f"{nome}: manca {cosa}")
        # il logo del garante compare due volte: header e footer
        if html.count("logo-cosmetech-academy-bianco.png") != 2:
            guasti.append(
                f"{nome}: il logo Academy non compare in header e footer")

    # il marchio predefinito: nome fisso, densita' alte, mai @1x
    if "logo-negativo@2x.png" not in lite or "srcset" not in lite:
        guasti.append("lite non usa il marchio predefinito con srcset")
    if "logo-negativo@1x.png" in lite:
        guasti.append("il marchio usa @1x: sfocato sugli schermi densi")
    if '<span class="nome">' not in master:
        guasti.append("master non mostra il marchio sovrascritto dall'app")

    if not APP_FINTA.exists():
        print(f"nota: {APP_FINTA} non c'e', i marchi dell'app "
              "resteranno immagini rotte nel browser")
    return guasti


def main():
    env = Environment(
        loader=FileSystemLoader(RADICE / "cosmetech_ui" / "templates"),
        autoescape=True,   # come in Flask sui .html
    )
    env.globals["url_for"] = url_for
    USCITA.mkdir(parents=True, exist_ok=True)

    reso = {}
    for nome, (base, blocchi) in PAGINE.items():
        html = env.from_string(sorgente(base, blocchi)).render(
            nome_app="AllergeniCalc")
        (USCITA / nome).write_text(html, encoding="utf-8")
        reso[nome] = html
        print(f"scritto  prova/uscita/{nome}")

    guasti = controlla(reso)
    if guasti:
        for g in guasti:
            print("GUASTO:", g)
        sys.exit(1)
    print("\ncontrolli superati. Apri prova/uscita/lite.html nel browser.")


if __name__ == "__main__":
    main()
