"""
cosmetech-ui — il guscio comune delle app Cosmetech.

Fornisce i template Jinja del guscio (header, footer, stili) e i file
statici che li accompagnano. L'app che lo installa scrive solo il proprio
contenuto: struttura e stile vivono qui, in una sola copia.

Uso, nell'app:

    import cosmetech_ui
    cosmetech_ui.registra(app)      # unica riga di setup

Da quel momento l'app puo' scrivere:

    {% extends "lite.html" %}
    {% block contenuto %} ... {% endblock %}
"""

from flask import Blueprint

__version__ = "0.1.0"

# Il percorso sotto cui vengono serviti gli statici del pacchetto. E'
# dedicato apposta: non deve mai collidere con lo /static dell'app, che
# resta libero per le sue immagini e il suo foglio di stile.
PERCORSO_STATICI = "/cosmetech-ui"

# Il blueprint porta con se' sia i template sia gli statici: registrarlo
# e' l'unico gesto necessario perche' Flask trovi gli uni e serva gli altri.
guscio = Blueprint(
    "cosmetech_ui",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path=PERCORSO_STATICI,
)


def registra(app):
    """Aggancia il guscio all'app Flask passata. Idempotente.

    Registra il blueprint (template + statici) e restituisce l'app, cosi'
    la chiamata puo' stare in coda alla creazione dell'app.
    """
    if "cosmetech_ui" not in app.blueprints:
        app.register_blueprint(guscio)
    return app


__all__ = ["registra", "guscio", "PERCORSO_STATICI", "__version__"]
