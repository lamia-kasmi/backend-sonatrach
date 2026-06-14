
# authentication.py
import requests
from dataclasses import dataclass
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# ✅ Importer les bonnes fonctions
from .discovery import discover_service, get_auth_base_url, AUTH_APP_NAME

# ✅ NOM CORRIGÉ (était 'AUTHENTICATION-SOUNATRCH' — R manquant)
# AUTH_APP_NAME est déjà défini dans discovery.py, donc on l'importe


@dataclass
class RemoteUser:
    id: int
    email: str
    role: str
    nom_complet: str
    activite_id: str = None
    direction_id: str = None
    departement_id: str = None
    is_authenticated: bool = True
    is_active: bool = True

    @property
    def is_anonymous(self):
        return False

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()

        try:
            # Utiliser la fonction get_auth_base_url
            base_url = get_auth_base_url()
            url = f'{base_url}/auth/me/'
            
            print(f'[AUTH] 🔍 Authentification via: {url}')
            
            resp = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'},
                timeout=3,
            )
        except requests.RequestException as e:
            # Invalider le cache en cas d'erreur
            cache.delete(f'eureka_url_{AUTH_APP_NAME}')
            print(f'[AUTH] ❌ Erreur connexion: {e}')
            raise AuthenticationFailed(f'Service authentification injoignable : {e}')

        if resp.status_code == 401:
            raise AuthenticationFailed('Token invalide ou expiré.')
        if resp.status_code != 200:
            raise AuthenticationFailed(f'Erreur auth: {resp.status_code}')

        data = resp.json()
        
        # Gérer le cas où la réponse est imbriquée dans 'user'
        if 'user' in data:
            user_data = data['user']
        else:
            user_data = data
        
        print(f'[AUTH] ✅ Authentifié: user_id={user_data.get("id")}, role={user_data.get("role")}')
        
        return (RemoteUser(
            id=user_data['id'],
            email=user_data.get('email', ''),
            role=user_data.get('role', ''),
            nom_complet=user_data.get('nom_complet', ''),
            activite_id=user_data.get('activite_id'),
            direction_id=user_data.get('direction_id'),
            departement_id=user_data.get('departement_id'),
            is_active=user_data.get('is_active', True),
        ), token)