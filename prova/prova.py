"""
Pagina di prova: renderizza il guscio con contenuto finto, senza Flask e
senza agganciare un'app.

    python3 prova/prova.py

Scrive prova/uscita/lite.html e prova/uscita/master.html, da aprire nel
browser. Verifica anche le due cose che non si vedono a occhio:
il <nav class="menu"> assente in lite, e il blocco avviso che sparisce
quando lo slot e' vuoto.
"""

import pathlib
import sys

from jinja2 import Environment, FileSystemLoader

RADICE = pathlib.Path(__file__).resolve().parent.parent
USCITA = RADICE / "prova" / "uscita"


def url_for(endpoint, filename=""):
    """Sostituto di quello di Flask: qui gli statici si leggono da disco."""
    if endpoint != "cosmetech_ui.static":
        raise AssertionError(f"endpoint inatteso nel guscio: {endpoint}")
    return f"../../cosmetech_ui/static/{filename}"


UTENTE_LITE = (
    "<strong>Marta Bianchi</strong> · Formulatrice · <a href='#'>esci</a>"
)
UTENTE_SSO = (
    "<strong>Marta Bianchi</strong> · piano <span>Pro</span> · <a href='#'>esci</a>"
)

CONTENUTO = """
  <div class="carta">
    <h2 style="margin-top:0">Contenuto finto</h2>
    <p>Questo blocco arriva dall'app: il guscio non sa cosa contenga.</p>
    <p><label>Un campo <input placeholder="scrivi qui"></label></p>
    <p><a class="pulsante" href="#">Un pulsante</a></p>
  </div>
"""

PAGINE = {
    # nome file : (template esteso, blocchi aggiuntivi)
    "lite.html": ("lite.html", {"utente": UTENTE_LITE, "avviso": ""}),
    "master.html": (
        "master.html",
        {
            "utente": UTENTE_SSO,
            "avviso": "Dal 31 luglio 2026 cambia l'Allegato III. "
                      "<a href='#'>Cosa cambia</a>",
            "menu": "<a class='attivo' href='#'>Calcolo</a>"
                    "<a href='#'>Storico</a><a href='#'>Guida</a>",
        },
    ),
}


def sorgente(base, blocchi):
    """Costruisce al volo il template di un'app finta che estende il guscio."""
    righe = [f'{{% extends "{base}" %}}']
    righe.append(
        "{% block marchio_app %}<span>AppDiProva</span>{% endblock %}"
    )
    righe.append("{% block titolo %}Titolo dello strumento{% endblock %}")
    righe.append(
        "{% block sottotitolo %}Riga di contesto sotto il titolo{% endblock %}"
    )
    for nome, testo in blocchi.items():
        righe.append(f"{{% block {nome} %}}{testo}{{% endblock %}}")
    righe.append("{% block contenuto %}" + CONTENUTO + "{% endblock %}")
    righe.append(
        "{% block footer_app %}<strong>AppDiProva</strong> "
        "— sezione dell'app nel footer{% endblock %}"
    )
    return "\n".join(righe)


def main():
    env = Environment(
        loader=FileSystemLoader(RADICE / "cosmetech_ui" / "templates"),
        autoescape=True,
    )
    env.globals["url_for"] = url_for
    USCITA.mkdir(parents=True, exist_ok=True)

    reso = {}
    for nome, (base, blocchi) in PAGINE.items():
        html = env.from_string(sorgente(base, blocchi)).render()
        (USCITA / nome).write_text(html, encoding="utf-8")
        reso[nome] = html
        print(f"scritto  prova/uscita/{nome}")

    guasti = []
    if '<nav class="menu">' in reso["lite.html"]:
        guasti.append("lite renderizza la barra del menu: non deve esistere")
    if '<nav class="menu">' not in reso["master.html"]:
        guasti.append("master non renderizza il menu pieno")
    if 'class="avviso"' in reso["lite.html"]:
        guasti.append("l'avviso vuoto lascia comunque il suo blocco")
    if 'class="avviso"' not in reso["master.html"]:
        guasti.append("l'avviso pieno non compare")
    for nome, html in reso.items():
        if "piano <span>" in html and nome == "lite.html":
            guasti.append("lite mostra il riconoscimento in formato SSO")
        if "logo-academy.png" not in html:
            guasti.append(f"{nome}: manca il logo Academy")

    if guasti:
        for g in guasti:
            print("GUASTO:", g)
        sys.exit(1)
    print("\ncontrolli superati. Apri prova/uscita/lite.html nel browser.")


if __name__ == "__main__":
    main()
