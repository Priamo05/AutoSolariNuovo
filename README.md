# Auto Solari Nuovo - Flask + MySQL + Bootstrap

Applicazione MVP basata sui requisiti condivisi:
- autenticazione utenti
- ruoli user/admin
- gestione impianti e veicoli
- inserimento dati energetici e km
- dashboard personale
- area admin con export CSV

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="mysql+pymysql://USER:PASSWORD@localhost/autosolari_db"
flask --app run.py run
```

## Creazione admin iniziale
Registrare un utente, poi promuoverlo da shell SQL o endpoint `/promote/<user_id>` quando loggato da admin.
