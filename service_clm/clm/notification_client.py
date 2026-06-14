"""
clm/notification_client.py  — CORRIGÉ

Toutes les requêtes sortantes utilisent :
  NOTIF_URL = http://localhost:8083   (Spring Cloud Gateway)
  + /notifications/...               (route gateway → Node.js Notification)

Ne jamais appeler /clm/... depuis ce client :
  /clm/** → gateway → Django 8012 (boucle infinie + JWT revalidé par DRF)
  /notifications/** → gateway → Node.js Notification 
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ── Config settings.py ───────────────────────────────────────
# NOTIFICATION_SERVICE_URL     = "http://localhost:8083"   # via Gateway
# NOTIFICATION_SERVICE_TIMEOUT = 5

NOTIF_URL = getattr(settings, 'NOTIFICATION_SERVICE_URL', 'http://localhost:8083')
TIMEOUT   = getattr(settings, 'NOTIFICATION_SERVICE_TIMEOUT', 5)

# ✅ Point d'entrée Node.js (route gateway /notifications/**)
_RISK_ALERTS_ENDPOINT = f'{NOTIF_URL}/notifications/risk-alerts/'


def _headers(jwt_token: str) -> dict:
    return {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type':  'application/json',
    }


# ══════════════════════════════════════════════════════════════
# ENVOI D'ALERTES
# ══════════════════════════════════════════════════════════════

def envoyer_alertes_risque(contrat_id: int, risques: list, jwt_token: str) -> dict:
    """
    Envoie les risques de type RETARD détectés par risk_engine au service Notification.

    Route appelée : POST /notifications/risk-alerts/
                    → gateway → Node.js Notification (lb://SERVICE-NOTIFICATION)

    Args:
        contrat_id : ID du contrat analysé
        risques    : liste retournée par analyser_risques()
        jwt_token  : token JWT de l'utilisateur Django (propagé tel quel)

    Returns:
        dict { 'success', 'sent_count', 'errors' }
    """
    risques_retard = [r for r in risques if r.get('type') == 'retard']

    if not risques_retard:
        logger.info(f'[NOTIF] Contrat {contrat_id} : aucun risque retard à notifier.')
        return {'success': True, 'sent_count': 0, 'errors': []}

    sent_count = 0
    errors     = []

    for risque in risques_retard:
        try:
            payload = {
                'contrat_id':  contrat_id,
                'code':        risque['code'],
                'type':        risque['type'],
                'description': risque['description'],
                'severite':    risque['severite'],
                'article_ref': risque.get('article_ref', ''),
                'suggestion':  risque.get('suggestion', ''),
            }

            response = requests.post(
                _RISK_ALERTS_ENDPOINT,   # ✅ /notifications/risk-alerts/
                json=payload,
                headers=_headers(jwt_token),
                timeout=TIMEOUT,
            )

            if response.status_code in (200, 201):
                sent_count += 1
                logger.info(f'[NOTIF] Alerte {risque["code"]} envoyée pour contrat {contrat_id}')
            else:
                msg = f'HTTP {response.status_code} pour {risque["code"]}: {response.text[:200]}'
                logger.warning(f'[NOTIF] {msg}')
                errors.append(msg)

        except requests.exceptions.Timeout:
            msg = f'Timeout lors de l\'envoi de {risque["code"]}'
            logger.error(f'[NOTIF] {msg}')
            errors.append(msg)

        except requests.exceptions.ConnectionError:
            msg = f'Service Notification inaccessible (contrat {contrat_id})'
            logger.error(f'[NOTIF] {msg}')
            errors.append(msg)
            break  # inutile de continuer si le service est down

        except Exception as exc:
            msg = f'Erreur inattendue pour {risque["code"]}: {exc}'
            logger.error(f'[NOTIF] {msg}')
            errors.append(msg)

    return {
        'success':    len(errors) == 0,
        'sent_count': sent_count,
        'errors':     errors,
    }


# ══════════════════════════════════════════════════════════════
# LECTURE D'ALERTES
# ══════════════════════════════════════════════════════════════

def get_alertes_retard(contrat_id: int, jwt_token: str) -> list:
    """
    Récupère les alertes retard existantes pour un contrat depuis le service Notification.

    Route appelée : GET /notifications/risk-alerts/?contrat_id=...&type=retard
                    → gateway → Node.js Notification (lb://SERVICE-NOTIFICATION)

    CORRECTION :
      Ne PAS appeler /clm/contrats/{id}/alertes/ (boucle Django + JWT invalide).
      Appeler directement /notifications/risk-alerts/ via le gateway.

    Returns:
        liste d'alertes enrichies ou [] en cas d'erreur
    """
    try:
        response = requests.get(
            _RISK_ALERTS_ENDPOINT,   # ✅ /notifications/risk-alerts/
            params={'contrat_id': contrat_id, 'type': 'retard'},
            headers={'Authorization': f'Bearer {jwt_token}'},
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            return response.json().get('alerts', [])

        logger.warning(f'[NOTIF] GET alertes retard → HTTP {response.status_code}')
        return []

    except Exception as exc:
        logger.error(f'[NOTIF] Erreur GET alertes retard: {exc}')
        return []