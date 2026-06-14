# clm_service/resolvers.py
import requests
from django.conf import settings
from discovery import get_juridique_base_url   # votre discovery.py existant

def get_direction_centrale_id(direction_id: str, access_token: str) -> str | None:
    """
    Appelle /juridique/directions/{direction_id}/
    pour récupérer direction_centrale_id.

    Utilise Eureka via votre discovery.py existant.
    """
    base_url = get_juridique_base_url()   # Eureka → fallback Gateway
    url = f"{base_url}/juridique/directions/{direction_id}/"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            # Adapter selon la structure réelle de la réponse juridique
            return (
                data.get("direction_centrale_id")
                or data.get("direction_centrale", {}).get("id")
            )
    except Exception as e:
        print(f"[CLM][resolver] Impossible de résoudre direction_centrale: {e}")

    return None  # null toléré dans le modèle