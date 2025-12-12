"""
DSGVO Newsletter Abmelde-Service
================================
Standalone Flask App fuer Newsletter-Abmeldungen.
Deployed via Coolify auf Hetzner.

Features:
- /unsubscribe/<uuid> - Abmeldeseite mit UUID
- /unsubscribe - Fallback ohne UUID
- /api/unsubscribe - POST Endpoint fuer Abmeldung
- /api/health - Health Check fuer Coolify
- NocoDB Integration fuer Empfaenger-Verwaltung
"""

import os
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# =============================================================================
# KONFIGURATION
# =============================================================================

# NocoDB API Konfiguration (aus Environment Variables oder Defaults)
NOCODB_API_URL = os.environ.get(
    "NOCODB_API_URL",
    "https://app.nocodb.com/api/v2/tables/m6yg62ezrua6vuy/records"
)
NOCODB_API_TOKEN = os.environ.get(
    "NOCODB_API_TOKEN",
    "afFvRQIHdPrLPCXu0Vl9iq5IuSso_WDlMc8vNEww"
)

# Port (Coolify erwartet 3000)
PORT = int(os.environ.get("PORT", 3000))


# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

def get_nocodb_headers():
    """Erstellt Header fuer NocoDB API Requests."""
    return {
        "xc-token": NOCODB_API_TOKEN,
        "Content-Type": "application/json"
    }


def find_subscriber_by_uuid(uuid: str) -> dict | None:
    """Sucht Subscriber in NocoDB anhand der UUID."""
    try:
        # Alle Records laden und nach UUID filtern
        response = requests.get(
            f"{NOCODB_API_URL}?offset=0&limit=100",
            headers=get_nocodb_headers(),
            timeout=15
        )
        if response.status_code == 200:
            records = response.json().get("list", [])
            for record in records:
                if record.get("uuid") == uuid:
                    return record
    except Exception as e:
        print(f"Fehler beim Suchen des Subscribers: {e}")
    return None


def unsubscribe_user(uuid: str) -> tuple[bool, str]:
    """
    Meldet einen Benutzer ab (setzt Status in NocoDB).
    Returns: (success: bool, message: str)
    """
    subscriber = find_subscriber_by_uuid(uuid)

    if not subscriber:
        return False, "Subscriber nicht gefunden"

    record_id = subscriber.get("Id")
    email = subscriber.get("email", "unbekannt")

    try:
        # Update: Setze Abmelde-Datum und Status
        patch_data = {
            "Id": record_id,
            "abgemeldet": True,
            "abmeldedatum": datetime.now().isoformat()
        }

        response = requests.patch(
            NOCODB_API_URL,
            headers=get_nocodb_headers(),
            json=patch_data,
            timeout=15
        )

        if response.status_code == 200:
            print(f"Abmeldung erfolgreich: {email} (UUID: {uuid})")
            return True, f"Erfolgreich abgemeldet: {email}"
        else:
            return False, f"NocoDB Fehler: {response.status_code}"

    except Exception as e:
        print(f"Fehler bei Abmeldung: {e}")
        return False, str(e)


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/health')
def health():
    """Health Check Endpoint fuer Coolify."""
    return jsonify({
        "status": "healthy",
        "service": "unsubscribe-service",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/unsubscribe/<uuid>')
def unsubscribe_page(uuid):
    """Abmeldeseite mit UUID."""
    # Subscriber-Info laden (optional)
    subscriber = find_subscriber_by_uuid(uuid)
    email = subscriber.get("email", "") if subscriber else ""
    name = subscriber.get("name", "") if subscriber else ""

    return render_template(
        'unsubscribe.html',
        uuid=uuid,
        email=email,
        name=name,
        found=subscriber is not None
    )


@app.route('/unsubscribe')
def unsubscribe_fallback():
    """Fallback-Seite ohne UUID."""
    return render_template('unsubscribe_fallback.html')


@app.route('/api/unsubscribe', methods=['POST'])
def api_unsubscribe():
    """API Endpoint fuer Abmeldung."""
    data = request.get_json() or {}
    uuid = data.get('uuid')

    if not uuid:
        return jsonify({
            "success": False,
            "error": "UUID fehlt"
        }), 400

    success, message = unsubscribe_user(uuid)

    return jsonify({
        "success": success,
        "message": message
    }), 200 if success else 400


@app.route('/api/status/<uuid>')
def api_status(uuid):
    """Prueft den Abmelde-Status eines Subscribers."""
    subscriber = find_subscriber_by_uuid(uuid)

    if not subscriber:
        return jsonify({
            "found": False,
            "error": "Subscriber nicht gefunden"
        }), 404

    return jsonify({
        "found": True,
        "email": subscriber.get("email", ""),
        "name": subscriber.get("name", ""),
        "abgemeldet": subscriber.get("abgemeldet", False),
        "abmeldedatum": subscriber.get("abmeldedatum", None)
    })


@app.route('/')
def index():
    """Startseite."""
    return render_template('index.html')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║           DSGVO Newsletter Abmelde-Service                    ║
╠═══════════════════════════════════════════════════════════════╣
║  Port:     {PORT}                                              ║
║  NocoDB:   {NOCODB_API_URL[:40]}...
╚═══════════════════════════════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=PORT, debug=False)
