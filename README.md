# Auto Solari Nuovo su Cloudflare Pages + Workers

Questa versione è stata riscritta per funzionare su **Cloudflare Pages** con backend in **Pages Functions (Workers runtime)**, senza Flask.

## Architettura
- Frontend statico in `public/` (Bootstrap + JS)
- API serverless in `functions/api/`
- Database Cloudflare **D1** (SQLite gestito) tramite binding `DB`

## Struttura
- `public/index.html`: UI login/registrazione/dashboard
- `public/app.js`: logica client (auth, CRUD impianti/veicoli/misurazioni, admin)
- `functions/api/[[path]].js`: router API unico
- `schema.sql`: schema D1
- `wrangler.toml`: configurazione progetto Cloudflare

## Deploy su Cloudflare Pages
1. Crea progetto Pages collegato a questa repo.
2. Build command: nessuno (`""`)
3. Build output directory: `public`
4. Aggiungi una D1 database e collega il binding `DB`.
5. Esegui migrazione schema:
   ```bash
   npx wrangler d1 execute autosolari_db --remote --file=schema.sql
   ```
6. Deploy.

## Sviluppo locale
```bash
npm install
npm run dev
```

## Endpoint principali
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/dashboard`
- `GET/POST/DELETE /api/plants`
- `GET/POST/DELETE /api/vehicles`
- `GET/POST/DELETE /api/measurements`
- `GET /api/admin/stats`
- `POST /api/admin/promote`
- `GET /api/admin/export.csv`

## Note sicurezza
- Sessione basata su cookie `session` firmato HMAC (WebCrypto)
- CSRF mitigato via SameSite=Strict + HttpOnly cookie
- Role check lato API (`user` / `admin`)
