
# discovery.py
import os
import requests
import json
from django.core.cache import cache

# Configuration
EUREKA_URL = os.getenv('EUREKA_URL', 'http://localhost:8761/eureka')
AUTH_APP_NAME = os.getenv('AUTH_APP_NAME', 'AUTHENTICATION-SERVICE')
JURIDIQUE_APP_NAME = os.getenv('JURIDIQUE_APP_NAME', 'SERVICE-JURIDIQUE')
GATEWAY_URL = os.getenv('GATEWAY_URL', 'http://localhost:8083')
USE_EUREKA = os.getenv('USE_EUREKA', 'true').lower() == 'true'
CACHE_TTL = 60  # secondes


def discover_service(service_name: str) -> str:
    """
    Découvre l'URL d'un service via Eureka
    Retourne l'URL du service ou lève une exception
    """
    # Si Eureka est désactivé, utiliser Gateway
    if not USE_EUREKA:
        print(f'[DISCOVERY] ℹ️ Eureka désactivé, utilisation Gateway: {GATEWAY_URL}')
        return GATEWAY_URL
    
    cache_key = f'eureka_url_{service_name}'
    cached_url = cache.get(cache_key)
    
    if cached_url:
        print(f'[DISCOVERY] ✅ Cache hit: {cached_url}')
        return cached_url
    
    try:
        # Appel à Eureka
        url = f'{EUREKA_URL}/apps/{service_name}'
        print(f'[DISCOVERY] 🔍 Découverte: {url}')
        
        response = requests.get(url, timeout=5, headers={'Accept': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            application = data.get('application', {})
            instances = application.get('instance', [])
            
            if instances:
                instance = instances[0] if isinstance(instances, list) else instances
                ip_addr = instance.get('ipAddr', 'localhost')
                
                # Gérer le port (peut être dict ou int)
                port_info = instance.get('port', {})
                if isinstance(port_info, dict):
                    port = port_info.get('$', 8010)
                else:
                    port = port_info or 8010
                
                base_url = f'http://{ip_addr}:{port}'
                print(f'[DISCOVERY] ✅ Service {service_name} trouvé: {base_url}')
                
                cache.set(cache_key, base_url, CACHE_TTL)
                return base_url
            else:
                print(f'[DISCOVERY] ⚠️ Aucune instance pour {service_name}')
                raise Exception(f'Service {service_name} non trouvé dans Eureka')
        else:
            print(f'[DISCOVERY] ❌ Eureka erreur {response.status_code}')
            raise Exception(f'Eureka a retourné {response.status_code}')
            
    except Exception as e:
        print(f'[DISCOVERY] ❌ Exception: {e}')
        # Fallback Gateway
        print(f'[DISCOVERY] 🔄 Fallback Gateway: {GATEWAY_URL}')
        cache.set(cache_key, GATEWAY_URL, CACHE_TTL // 2)
        return GATEWAY_URL


def get_auth_base_url() -> str:
    """
    Récupère l'URL du service d'authentification
    Alias de discover_service pour AUTH_APP_NAME
    """
    return discover_service(AUTH_APP_NAME)


def get_juridique_base_url() -> str:
    """Récupère l'URL du service juridique via Eureka ou Gateway"""
    return discover_service(JURIDIQUE_APP_NAME)



def get_gateway_url() -> str:
    """Retourne l'URL de la Gateway"""
    return GATEWAY_URL


def get_all_services() -> dict:
    """
    Récupérer tous les services enregistrés dans Eureka (debug)
    """
    if not USE_EUREKA:
        return {"gateway": GATEWAY_URL, "services": {}}
    
    try:
        response = requests.get(f'{EUREKA_URL}/apps', timeout=5)
        if response.status_code == 200:
            data = response.json()
            applications = data.get('applications', {}).get('application', [])
            services = {}
            for app in applications:
                app_name = app.get('name')
                instances = app.get('instance', [])
                if instances:
                    instance = instances[0] if isinstance(instances, list) else instances
                    ip = instance.get('ipAddr')
                    port = instance.get('port', {}).get('$', 0)
                    services[app_name] = f'http://{ip}:{port}'
            return services
    except Exception as e:
        print(f'[DISCOVERY] Erreur get_all_services: {e}')
    
    return {}