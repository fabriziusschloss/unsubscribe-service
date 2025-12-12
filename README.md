# DSGVO Newsletter Abmelde-Service

Standalone Flask App fuer DSGVO-konforme Newsletter-Abmeldungen.
Deployed via Coolify auf Hetzner.

## Features

- `/unsubscribe/<uuid>` - Personalisierte Abmeldeseite
- `/api/unsubscribe` - POST Endpoint fuer Abmeldung
- `/api/status/<uuid>` - Status pruefen
- `/health` - Health Check fuer Coolify
- NocoDB Integration fuer Empfaenger-Verwaltung

## Lokale Entwicklung

```bash
# Dependencies installieren
pip install -r requirements.txt
# oder mit uv:
uv sync

# Server starten
python main.py
```

Server laeuft auf http://localhost:3000

## Deployment mit Coolify

1. Repository in Coolify verbinden
2. Build Pack: Nixpacks (automatisch erkannt)
3. Port: 3000 (Standard)
4. Environment Variables setzen:
   - `NOCODB_API_URL` - NocoDB API URL
   - `NOCODB_API_TOKEN` - NocoDB API Token

## Environment Variables

| Variable | Beschreibung | Default |
|----------|--------------|---------|
| `PORT` | Server Port | 3000 |
| `NOCODB_API_URL` | NocoDB API Endpoint | (intern) |
| `NOCODB_API_TOKEN` | NocoDB Auth Token | (intern) |

## API Dokumentation

### POST /api/unsubscribe

Meldet einen Subscriber ab.

```json
{
  "uuid": "d1b1be95-4c77-4395-92c6-0d14494b1f7f"
}
```

Response:
```json
{
  "success": true,
  "message": "Erfolgreich abgemeldet: email@example.com"
}
```

### GET /api/status/<uuid>

Prueft den Abmelde-Status.

Response:
```json
{
  "found": true,
  "email": "email@example.com",
  "name": "Max",
  "abgemeldet": false,
  "abmeldedatum": null
}
```
