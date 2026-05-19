# Auto Solari Nuovo (Flask + MySQL + Bootstrap)

Applicazione web per gestire:
- utenti autenticati con ruoli (`user`, `admin`)
- impianti energetici
- veicoli elettrici
- misurazioni giornaliere (produzione, consumo, km)
- dashboard personale e area admin con export CSV

## Stack
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- MySQL (via `pymysql`)
- Bootstrap 5

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="cambia-questa-chiave"
export DATABASE_URL="mysql+pymysql://USER:PASSWORD@localhost/autosolari_db"
flask --app run.py run --debug
```

## Funzionalità principali
- Registrazione/Login/Logout
- CRUD base (create + delete) per impianti, veicoli e misurazioni
- Protezione ownership: ogni utente vede e modifica solo i propri dati
- Admin dashboard con promozione utente e export CSV globale

## Note
- Al primo avvio, le tabelle vengono create automaticamente (`db.create_all()`).
- Endpoint di promozione admin disponibile solo via POST nell'area admin.
