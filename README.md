# cosmetech-ui

Il guscio comune delle app Cosmetech: header, footer e stili in **una sola
copia**. Un'app che lo installa scrive soltanto il proprio contenuto.

Esiste perché la stessa intestazione era stata copiata in ogni app e le
copie avevano già cominciato a divergere. Da qui in avanti struttura e
stile hanno una fonte sola: questo pacchetto, che replica il container
approvato (`prototipo.html`, v3).

## Installazione

Nel `requirements.txt` dell'app:

```
cosmetech-ui @ git+https://github.com/infinito62/cosmetech-ui.git@main
```

Il repo è pubblico apposta: il build Docker delle app deve poterlo
scaricare senza credenziali.

## Setup nell'app: una riga

```python
import cosmetech_ui

app = Flask(__name__)
cosmetech_ui.registra(app)
```

`registra()` aggancia un blueprint che porta con sé sia i template sia gli
statici. Da quel momento i template del guscio sono raggiungibili per nome
e gli statici sono serviti sotto `/cosmetech-ui/` — percorso dedicato, che
non tocca lo `/static` dell'app. La chiamata è idempotente.

## Usare il guscio

```jinja
{% extends "lite.html" %}

{% block marchio_app %}<span class="nome">AllergeniCalc</span>{% endblock %}

{% block titolo %}Quali allergeni devi dichiarare in etichetta{% endblock %}
{% block sottotitolo %}Reg. UE 2023/1545 · soglie leave-on e rinse-off{% endblock %}

{% block utente %}
  <strong>{{ iscritto.nome }}</strong> · {{ qualifica }} · <a href="/esci">esci</a>
{% endblock %}

{% block testa %}
  <link rel="stylesheet" href="{{ url_for('static', filename='app.css') }}">
{% endblock %}

{% block contenuto %}
  … il corpo dell'app …
{% endblock %}
```

### Gli slot

| Slot | Cosa ci va |
|---|---|
| `marchio_app` | logo (`<img>`, 32px) e/o nome (`<span class="nome">`) dell'app |
| `titolo` | titolo dell'app; diventa l'`<h1>` |
| `sottotitolo` | riga descrittiva sotto il titolo |
| `utente` | riconoscimento utente (sotto) |
| `menu` | le voci `<li>` del menu — **vuoto in `lite.html`** |
| `avviso` | banner sotto l'header; se vuoto il blocco non compare |
| `contenuto` | il corpo dell'app |
| `footer_app` | sezione dell'app nel footer |

Più tre slot di servizio: `testa` (nel `<head>`, dopo il css del
pacchetto), `copertina` (titolo della finestra, se diverso da `titolo`) e
`scripts` (in coda al `<body>`).

Sono fissi e non sovrascrivibili: il logo Academy in header — con
l'occhiello «Uno strumento» — e nel footer, la fascia social, il blocco
legale.

### `master.html` e `lite.html`

`lite.html` estende `master.html` e lascia vuoto lo slot `menu`. Quando lo
slot è vuoto il `<nav class="menu">` **non viene emesso affatto**: non è
nascosto via CSS, non è nel documento. Un'app che estende `lite.html` non
deve sapere che il menu esiste. Lo stesso vale per `avviso`,
`sottotitolo`, `utente` e `footer_app`: slot vuoto, elemento assente.

Un'app che vuole il menu estende `master.html` e mette le voci — solo i
`<li>`, l'`<ul>` e la barra li fa il guscio:

```jinja
{% block menu %}
  <li><a href="/" class="attivo">Calcolo</a></li>
  <li><a href="/schede">Le mie schede</a></li>
{% endblock %}
```

### Riconoscimento utente

Due formati, secondo il tipo di sessione. Il guscio non ha logica di
sessione: riceve i dati già pronti dall'app e li dispone.

```jinja
{# sessione lite #}
{% block utente %}<strong>{{ nome }}</strong> · {{ qualifica }} · <a href="/esci">esci</a>{% endblock %}

{# sessione SSO #}
{% block utente %}<strong>{{ sso.nome }}</strong> · piano <span>{{ sso.tier }}</span> · <a href="/esci">esci</a>{% endblock %}
```

## I colori

Il foglio del pacchetto espone in cima **quattro** variabili, e solo
quelle si ridefiniscono:

```css
--c1-fondo      /* header, footer, filetti, hover del menu */
--c2-menu       /* sfondo della barra menu */
--c3-pulsante   /* pulsanti e link */
--c4-titoli     /* titoli nel corpo */
```

Tutto il resto — `--filetto`, `--sfondo`, `--tenue` — **deriva** da
`--c1-fondo` con `color-mix()`. Fuori dai blocchi `:root` non c'è nessun
colore scritto a mano: chi sviluppa un'app non deve mai poter scegliere il
colore di un bordo.

L'app ridefinisce le quattro nel proprio foglio, che va caricato **dopo**
quello del pacchetto — cioè dentro il blocco `testa`:

```css
/* app.css dell'app */
:root {
  --c1-fondo:    #123a60;
  --c2-menu:     #0d2c4a;   /* di norma più scuro di --c1-fondo */
  --c3-pulsante: #1f6fb2;
  --c4-titoli:   #123a60;
}
```

I valori qui sopra sono anche quelli predefiniti del pacchetto: la
famiglia blu di allergeni-calc.

## Cosa arriva già pronto al contenuto

Il guscio non porta solo header e footer. Dentro `contenuto` sono già
disponibili, senza scrivere una riga di CSS:

- `.contenitore` — larghezza max 1180px, gutter 30px. Il corpo ce l'ha già.
- `.colonna` — colonna centrale da 880px, per le app che stanno strette.
- `.card` — pannello bianco con filetto, raggio e ombra.
- `.btn` e `.btn-secondario` — i pulsanti, con l'hover a colori invertiti.
- `label` e `th` — maiuscoletto spaziato, già stilati.
- `hr.filetto` — il separatore.
- la scala di spazi `--sp-1`…`--sp-5` e i token `--radius`, `--ombra`,
  `--font-titoli`, `--font-testo`.

I font sono ospitati dal pacchetto (Questrial e Inter in `static/fonts/`):
nessuna chiamata a Google Fonts, così il container non dipende dalla rete.

## Verificare senza agganciare un'app

```
python3 prova/prova.py
```

Renderizza `lite.html` e `master.html` con contenuto finto in
`prova/uscita/`, da aprire nel browser. Non serve Flask: gli statici sono
letti da disco. La variante master mostra anche la palette ridefinita
dall'app, per far vedere che bastano le quattro variabili a cambiare
famiglia di colore.

Lo script controlla anche ciò che a occhio non si vede — che `lite` non
emetta la barra del menu, che l'avviso vuoto non lasci il suo blocco, che
il logo Academy compaia in header e footer, che il blocco legale ci sia —
ed esce con codice diverso da zero se qualcosa non torna.

## Struttura

```
cosmetech_ui/
  __init__.py          registra() — blueprint con template e statici
  templates/
    master.html        il guscio completo: header, menu, avviso, corpo, footer
    lite.html          estende master, senza menu
  static/
    cosmetech-ui.css   tutti gli stili; le quattro variabili in cima
    fonts/             Questrial e Inter
    logo-academy.png
prototipo.html         il container approvato, riferimento del guscio
prova/prova.py         pagina di prova, senza Flask
```
