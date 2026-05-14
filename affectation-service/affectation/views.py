


"""
views.py — Service Affectation (port 8011)
"""

import requests
from datetime import datetime
from django.core.cache import cache
from django.conf import settings

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission

from .authentication import RemoteJWTAuthentication
from .discovery import get_auth_base_url, get_gateway_url, AUTH_APP_NAME
from .permissions import *


# ──────────────────────────────────────────────
# RÔLES VALIDES
# ──────────────────────────────────────────────

VALID_ROLES = [
    'agent',
    'directeur_activite',
    'directeur_direction',
    'responsable_departement',
]

ROLE_DISPLAY = {
    'agent':                   'Agent',
    'directeur_activite':      'Directeur Activité',
    'directeur_direction':     'Directeur de Direction',
    'responsable_departement': 'Responsable de Département',
}


# ──────────────────────────────────────────────
# PERMISSION
# ──────────────────────────────────────────────

class IsAdmin(BasePermission):
    message = "Accès réservé aux administrateurs."
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', '') == 'admin'
        )


# ──────────────────────────────────────────────
# HELPER HTTP — appel vers le service Auth
# ──────────────────────────────────────────────

def _call_auth(method: str, path: str, token: str, use_gateway: bool = False, **kwargs):
    """
    Appelle le service Auth (résolu via Eureka ou Gateway).
    Retourne (status_code, dict).
    
    Args:
        method: HTTP method (get, post, patch, etc.)
        path: Chemin de l'API (ex: /auth/users/2/)
        token: JWT token
        use_gateway: Force l'utilisation de la Gateway au lieu d'Eureka
        **kwargs: Arguments supplémentaires pour requests (json, etc.)
    """
    # Choisir la base URL
    if use_gateway:
        base_url = get_gateway_url()
        print(f'[AFFECTATION] 🌐 Utilisation de la Gateway: {base_url}')
    else:
        base_url = get_auth_base_url()
        print(f'[AFFECTATION] 🔍 Utilisation de Eureka: {base_url}')
    
    url = f"{base_url}{path}"
    headers = {'Authorization': f'Bearer {token}'}

    print(f'[AFFECTATION] → {method.upper()} {url}')

    try:
        resp = getattr(requests, method)(
            url, headers=headers, timeout=5, **kwargs
        )
        print(f'[AFFECTATION] ← {resp.status_code} | body: {repr(resp.text[:200])}')

        # Réponse vide (204, ou body vide) → dict vide
        if not resp.text.strip():
            return resp.status_code, {}

        return resp.status_code, resp.json()

    except requests.exceptions.JSONDecodeError as e:
        print(f'[AFFECTATION] ✗ JSON decode error: {e} | raw: {repr(resp.text[:300])}')
        return resp.status_code, {"raw": resp.text}

    except requests.RequestException as e:
        print(f'[AFFECTATION] ✗ Réseau: {e}')
        # Invalider le cache Eureka en cas d'erreur réseau
        cache.delete(f'eureka_url_{AUTH_APP_NAME}')
        
        # Si on n'utilisait pas déjà la Gateway, essayer en fallback
        if not use_gateway:
            print(f'[AFFECTATION] 🔄 Fallback: tentative via Gateway...')
            return _call_auth(method, path, token, use_gateway=True, **kwargs)
        
        return 503, {"status": "error", "message": f"Service Auth injoignable : {e}"}


def _call_juridique(method: str, path: str, token: str, **kwargs):
    """
    Appelle le service Juridique (Node.js) via Eureka ou Gateway
    """
    try:
        from .discovery import get_juridique_base_url, get_gateway_url
        juridique_url = get_juridique_base_url()
    except:
        juridique_url = os.getenv('GATEWAY_URL', 'http://localhost:8083')
    
    url = f"{juridique_url}{path}"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f'[AFFECTATION] → Juridique {method.upper()} {url}')
    
    try:
        resp = getattr(requests, method)(
            url, headers=headers, timeout=5, **kwargs
        )
        print(f'[AFFECTATION] ← Juridique {resp.status_code}')
        
        if not resp.text.strip():
            return resp.status_code, {}
        return resp.status_code, resp.json()
        
    except requests.RequestException as e:
        print(f'[AFFECTATION] ✗ Erreur juridique: {e}')
        return 503, {"status": "error", "message": f"Service juridique injoignable: {e}"}
    
# ──────────────────────────────────────────────
# VIEW : ASSIGN ROLE
# ──────────────────────────────────────────────

@api_view(['POST'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def assign_role(request):
    """
    POST /affectation/assign-role/
    Body : { "user_id": 2, "role": "directeur_activite" }
    
    Query params optionnels:
    ?force_gateway=true - Force l'utilisation de la Gateway au lieu d'Eureka
    """
    # Vérifier si on force l'utilisation de la Gateway
    force_gateway = request.query_params.get('force_gateway', '').lower() == 'true'
    
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id = request.data.get('user_id')
    role = request.data.get('role')

    # ── Validation ──
    if not user_id:
        return Response(
            {"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."},
            status=400,
        )
    if not role:
        return Response(
            {"status": "error", "code": "MISSING_ROLE", "message": "role est obligatoire."},
            status=400,
        )
    if role not in VALID_ROLES:
        return Response(
            {"status": "error", "code": "INVALID_ROLE",
             "message": f"Rôle '{role}' invalide.", "valid_roles": VALID_ROLES},
            status=400,
        )

    print(f'[AFFECTATION] 📝 Assignation rôle: user_id={user_id}, role={role}, force_gateway={force_gateway}')

    # ── Étape 1 : récupérer l'user cible ──
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token, use_gateway=force_gateway)

    print(f'[AFFECTATION] user_response reçu: status={sc}')

    if sc == 503:
        return Response(user_response, status=503)
    if sc == 404:
        return Response(
            {"status": "error", "code": "USER_NOT_FOUND",
             "message": f"Utilisateur {user_id} introuvable."},
            status=404,
        )
    if sc != 200:
        return Response(
            {"status": "error", "code": "AUTH_SERVICE_ERROR",
             "message": f"Service Auth a retourné {sc}.", "detail": user_response},
            status=sc,
        )

    # Extraire les données utilisateur de la réponse imbriquée
    user_data = user_response.get('user', {})
    
    if not user_data:
        return Response(
            {"status": "error", "code": "INVALID_RESPONSE",
             "message": "Structure de réponse invalide du service Auth."},
            status=500,
        )

    if user_data.get('role') == 'admin':
        return Response(
            {"status": "error", "code": "CANNOT_MODIFY_ADMIN",
             "message": "Impossible de modifier le rôle d'un administrateur."},
            status=400,
        )

    previous_role = user_data.get('role')

    # ── Étape 2 : Mettre à jour le rôle ──
    sc, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update-role/',
        token,
        json={"role": role},
        use_gateway=force_gateway,
    )

    if sc == 503:
        return Response(updated, status=503)
    if sc not in (200, 201):
        return Response(
            {"status": "error", "code": "UPDATE_FAILED",
             "message": f"Impossible de mettre à jour le rôle (status {sc}).",
             "detail": updated},
            status=sc,
        )

    # ── Construction de la réponse ──
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    # Récupérer le nom de l'admin qui fait la requête
    admin_name = getattr(admin, 'nom_complet', None)
    if not admin_name:
        admin_prenom = getattr(admin, 'prenom', '')
        admin_nom = getattr(admin, 'nom', '')
        admin_name = f"{admin_prenom} {admin_nom}".strip() or str(admin)
    
    admin_role = getattr(admin, 'role', 'unknown')
    
    # Ajouter des métadonnées sur la source de l'appel
    response_data = {
        "status": "success",
        "code": "ROLE_ASSIGNED",
        "message": (
            f"Rôle '{ROLE_DISPLAY.get(role, role)}' affecté à "
            f"{nom_complet}."
        ),
        "data": {
            "user_id":          user_id,
            "user_name":        nom_complet,
            "email":            user_data.get('email'),
            "previous_role":    previous_role,
            "previous_role_display": ROLE_DISPLAY.get(previous_role, previous_role) if previous_role else None,
            "new_role":         role,
            "new_role_display": ROLE_DISPLAY.get(role, role),
            "assigned_by": {
                "id":   admin.id,
                "name": admin_name,
                "role": admin_role,
            },
            "timestamp": datetime.now().isoformat(),
        },
        "metadata": {
            "source": "gateway" if force_gateway else "eureka",
            "service": "affectation-service",
            "version": "1.0.0"
        }
    }
    
    # Si on a utilisé le fallback, l'indiquer dans la réponse
    if not force_gateway and sc == 200:
        response_data["metadata"]["discovery_method"] = "eureka"
    elif force_gateway:
        response_data["metadata"]["discovery_method"] = "gateway_forced"
    
    return Response(response_data, status=200)

    
# ──────────────────────────────────────────────
# VIEW : AFFECTATION (ACTIVITE,DEPARTEMENT,DIRECTION)
# ──────────────────────────────────────────────

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def assign_activite_to_user(request):
    """
    PATCH /affectation/assign-activite/
    Body: { "user_id": 2, "activite_id": "672a1b2c3d4e5f6789abcdef" }
    
    1. Vérifie que l'utilisateur a le rôle 'directeur_activite'
    2. Vérifie que l'utilisateur n'a PAS déjà une activité affectée
    3. Récupère l'activité depuis le service juridique
    4. Met à jour l'activite_id de l'utilisateur dans le service Auth
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user
    
    user_id = request.data.get('user_id')
    activite_id = request.data.get('activite_id')
    
    # ── Validation ──
    if not user_id:
        return Response(
            {"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."},
            status=400,
        )
    if not activite_id:
        return Response(
            {"status": "error", "code": "MISSING_ACTIVITE_ID", "message": "activite_id est obligatoire."},
            status=400,
        )
    
    # ── Étape 1 : Récupérer l'utilisateur depuis Auth ──
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
    if sc != 200:
        return Response(
            {"status": "error", "code": "USER_NOT_FOUND",
             "message": f"Utilisateur {user_id} introuvable."},
            status=404,
        )
    
    user_data = user_response.get('user', {})
    
    # Vérifier que l'utilisateur a le bon rôle
    if user_data.get('role') != 'directeur_activite':
        return Response(
            {"status": "error", "code": "INVALID_ROLE",
             "message": f"L'utilisateur a le rôle '{user_data.get('role')}', doit être 'directeur_activite'"},
            status=400,
        )
    
    # ✅ Vérifier si l'utilisateur a déjà une activité affectée
    existing_activite_id = user_data.get('activite_id')
    if existing_activite_id:
        # Récupérer le nom de l'activité existante pour un message plus clair
        existing_activite_nom = "Inconnue"
        sc_existing, existing_activite = _call_juridique('get', f'/juridique/activites/{existing_activite_id}/', token)
        if sc_existing == 200:
            existing_activite_nom = existing_activite.get('data', {}).get('nom', 'Inconnue')
        
        return Response(
            {"status": "error", "code": "ALREADY_ASSIGNED",
             "message": f"L'utilisateur a déjà une activité affectée.",
             "data": {
                 "user_id": user_id,
                 "user_name": user_data.get('nom_complet'),
                 "existing_activite_id": existing_activite_id,
                 "existing_activite_nom": existing_activite_nom,
                 "suggestion": "Utilisez PUT /affectation/reassign-activite/ pour changer d'activité"
             }},
            status=400,
        )
    
    # ── Étape 2 : Récupérer l'activité depuis le service Juridique ──
    sc_act, activite_data = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
    
    if sc_act == 404:
        return Response(
            {"status": "error", "code": "ACTIVITE_NOT_FOUND",
             "message": f"Activité {activite_id} non trouvée dans le service juridique."},
            status=404,
        )
    if sc_act != 200:
        return Response(
            {"status": "error", "code": "JURIDIQUE_SERVICE_ERROR",
             "message": f"Service juridique indisponible (status {sc_act})."},
            status=503,
        )
    
    # Extraire les données de l'activité
    activite_info = activite_data.get('data', {})
    activite_nom = activite_info.get('nom') or activite_info.get('name', 'Unknown')
    
    # ── Étape 3 : Mettre à jour l'activite_id de l'utilisateur dans Auth ──
    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={"activite_id": activite_id}
    )
    
    if sc_update != 200:
        return Response(
            {"status": "error", "code": "UPDATE_FAILED",
             "message": "Impossible de mettre à jour l'activite_id de l'utilisateur.",
             "detail": updated},
            status=sc_update,
        )
    
    # ── Réponse finale ──
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success",
        "code": "ACTIVITE_ASSIGNED",
        "message": f"Activité '{activite_nom}' affectée à {nom_complet}.",
        "data": {
            "user_id": user_id,
            "user_name": nom_complet,
            "user_email": user_data.get('email'),
            "user_role": user_data.get('role'),
            "activite_id": activite_id,
            "activite_nom": activite_nom,
            "activite_details": activite_info,
            "assigned_by": {
                "id": admin.id,
                "name": getattr(admin, 'nom_complet', str(admin)),
                "role": getattr(admin, 'role', 'admin')
            },
            "timestamp": datetime.now().isoformat()
        }
    }, status=200)

@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def reassign_activite_to_user(request):
    """
    PUT /affectation/reassign-activite/
    Body: { "user_id": 2, "activite_id": "672a1b2c3d4e5f6789abcdef" }
    
    Permet de changer l'activité d'un utilisateur même s'il en a déjà une.
    (Force la réaffectation)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user
    
    user_id = request.data.get('user_id')
    activite_id = request.data.get('activite_id')
    force = request.data.get('force', True)  # Par défaut True pour PUT
    
    # ── Validation ──
    if not user_id:
        return Response(
            {"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."},
            status=400,
        )
    if not activite_id:
        return Response(
            {"status": "error", "code": "MISSING_ACTIVITE_ID", "message": "activite_id est obligatoire."},
            status=400,
        )
    
    # ── Étape 1 : Récupérer l'utilisateur depuis Auth ──
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
    if sc != 200:
        return Response(
            {"status": "error", "code": "USER_NOT_FOUND",
             "message": f"Utilisateur {user_id} introuvable."},
            status=404,
        )
    
    user_data = user_response.get('user', {})
    
    # Vérifier que l'utilisateur a le bon rôle
    if user_data.get('role') != 'directeur_activite':
        return Response(
            {"status": "error", "code": "INVALID_ROLE",
             "message": f"L'utilisateur a le rôle '{user_data.get('role')}', doit être 'directeur_activite'"},
            status=400,
        )
    
    # Récupérer l'ancienne activité (si existe)
    old_activite_id = user_data.get('activite_id')
    old_activite_nom = None
    if old_activite_id:
        sc_old, old_activite = _call_juridique('get', f'/juridique/activites/{old_activite_id}/', token)
        if sc_old == 200:
            old_activite_nom = old_activite.get('data', {}).get('nom', 'Inconnue')
    
    # ── Étape 2 : Récupérer la nouvelle activité ──
    sc_act, activite_data = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
    
    if sc_act == 404:
        return Response(
            {"status": "error", "code": "ACTIVITE_NOT_FOUND",
             "message": f"Activité {activite_id} non trouvée dans le service juridique."},
            status=404,
        )
    if sc_act != 200:
        return Response(
            {"status": "error", "code": "JURIDIQUE_SERVICE_ERROR",
             "message": f"Service juridique indisponible (status {sc_act})."},
            status=503,
        )
    
    activite_info = activite_data.get('data', {})
    activite_nom = activite_info.get('nom') or activite_info.get('name', 'Unknown')
    
    # ── Étape 3 : Mettre à jour ──
    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={"activite_id": activite_id}
    )
    
    if sc_update != 200:
        return Response(
            {"status": "error", "code": "UPDATE_FAILED",
             "message": "Impossible de mettre à jour l'activite_id de l'utilisateur.",
             "detail": updated},
            status=sc_update,
        )
    
    # ── Réponse ──
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    response_data = {
        "status": "success",
        "code": "ACTIVITE_REASSIGNED",
        "message": f"Activité changée de '{old_activite_nom or 'aucune'}' vers '{activite_nom}' pour {nom_complet}.",
        "data": {
            "user_id": user_id,
            "user_name": nom_complet,
            "user_email": user_data.get('email'),
            "user_role": user_data.get('role'),
            "previous_activite_id": old_activite_id,
            "previous_activite_nom": old_activite_nom,
            "new_activite_id": activite_id,
            "new_activite_nom": activite_nom,
            "new_activite_details": activite_info,
            "assigned_by": {
                "id": admin.id,
                "name": getattr(admin, 'nom_complet', str(admin)),
                "role": getattr(admin, 'role', 'admin')
            },
            "timestamp": datetime.now().isoformat()
        }
    }
    
    return Response(response_data, status=200)


# ==========================
# DÉSAFFECTER UNE ACTIVITÉ
# ==========================

@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def remove_activite_from_user(request, user_id):
    """
    DELETE /affectation/users/<user_id>/remove-activite/
    
    Supprime l'affectation d'activité d'un utilisateur
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user
    
    # ── Récupérer l'utilisateur ──
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
    if sc != 200:
        return Response(
            {"status": "error", "code": "USER_NOT_FOUND",
             "message": f"Utilisateur {user_id} introuvable."},
            status=404,
        )
    
    user_data = user_response.get('user', {})
    
    # Vérifier s'il a une activité
    current_activite_id = user_data.get('activite_id')
    if not current_activite_id:
        return Response(
            {"status": "error", "code": "NO_ACTIVITE_ASSIGNED",
             "message": "Cet utilisateur n'a aucune activité affectée."},
            status=400,
        )
    
    # Récupérer le nom de l'activité pour le message
    activite_nom = "Inconnue"
    sc_act, activite_data = _call_juridique('get', f'/juridique/activites/{current_activite_id}/', token)
    if sc_act == 200:
        activite_nom = activite_data.get('data', {}).get('nom', 'Inconnue')
    
    # ── Supprimer l'activite_id ──
    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={"activite_id": None}
    )
    
    if sc_update != 200:
        return Response(
            {"status": "error", "code": "UPDATE_FAILED",
             "message": "Impossible de supprimer l'activite_id.",
             "detail": updated},
            status=sc_update,
        )
    
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success",
        "code": "ACTIVITE_REMOVED",
        "message": f"Activité '{activite_nom}' désaffectée de {nom_complet}.",
        "data": {
            "user_id": user_id,
            "user_name": nom_complet,
            "removed_activite_id": current_activite_id,
            "removed_activite_nom": activite_nom,
            "removed_by": {
                "id": admin.id,
                "name": getattr(admin, 'nom_complet', str(admin)),
                "role": getattr(admin, 'role', 'admin')
            },
            "timestamp": datetime.now().isoformat()
        }
    }, status=200)



# ==========================
# 1. LISTER LES DIRECTEURS D'ACTIVITÉ SANS ACTIVITÉ AFFECTÉE
# ==========================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_activite(request):
    """
    GET /affectation/users/directeurs-activite/
    
    Liste tous les directeurs d'activité SANS activité affectée
    (utilisateurs avec rôle 'directeur_activite' et activite_id = null)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
    # Récupérer tous les utilisateurs
    sc, users_response = _call_auth('get', '/auth/users/', token)
    
    if sc != 200:
        return Response(
            {"status": "error", "code": "AUTH_SERVICE_ERROR",
             "message": "Impossible de récupérer la liste des utilisateurs"},
            status=503,
        )
    
    users = users_response.get('users', [])
    
    # Filtrer: seulement directeurs d'activité SANS activité affectée
    directeurs_sans_activite = [
        u for u in users 
        if u.get('role') == 'directeur_activite' and not u.get('activite_id')
    ]
    
    # Formatage de la réponse
    data = []
    for directeur in directeurs_sans_activite:
        data.append({
            "id": directeur.get('id'),
            "email": directeur.get('email'),
            "nom": directeur.get('nom'),
            "prenom": directeur.get('prenom'),
            "nom_complet": directeur.get('nom_complet'),
            "role": directeur.get('role'),
            "role_display": directeur.get('role_display'),
            "is_active": directeur.get('is_active'),
            "matricule": directeur.get('matricule'),
            "telephone": directeur.get('telephone'),
            "photo_profil": directeur.get('photo_profil')
        })
    
    return Response({
        "status": "success",
        "code": "DIRECTEURS_SANS_ACTIVITE",
        "message": f"{len(data)} directeur(s) d'activité sans activité affectée",
        "data": {
            "count": len(data),
            "directeurs": data
        },
        "timestamp": datetime.now().isoformat()
    }, status=200)


# ==========================
# 2. LISTER LES DIRECTEURS D'ACTIVITÉ AVEC ACTIVITÉ AFFECTÉE
# ==========================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_activite_affectes(request):
    """
    GET /affectation/users/directeurs-activite/affectes/
    
    Liste tous les directeurs d'activité AVEC activité affectée
    (utilisateurs avec rôle 'directeur_activite' et activite_id non null)
    Inclut les détails de l'activité depuis le service juridique
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
    # Récupérer tous les utilisateurs
    sc, users_response = _call_auth('get', '/auth/users/', token)
    
    if sc != 200:
        return Response(
            {"status": "error", "code": "AUTH_SERVICE_ERROR",
             "message": "Impossible de récupérer la liste des utilisateurs"},
            status=503,
        )
    
    users = users_response.get('users', [])
    
    # Filtrer: seulement directeurs d'activité AVEC activité affectée
    directeurs_avec_activite = [
        u for u in users 
        if u.get('role') == 'directeur_activite' and u.get('activite_id')
    ]
    
    # Récupérer les détails des activités pour chaque directeur
    data = []
    for directeur in directeurs_avec_activite:
        activite_id = directeur.get('activite_id')
        activite_data = None
        
        # Récupérer l'activité depuis le service juridique
        if activite_id:
            sc_act, activite_response = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
            if sc_act == 200:
                activite_data = activite_response.get('data', {})
        
        data.append({
            "id": directeur.get('id'),
            "email": directeur.get('email'),
            "nom": directeur.get('nom'),
            "prenom": directeur.get('prenom'),
            "nom_complet": directeur.get('nom_complet'),
            "role": directeur.get('role'),
            "role_display": directeur.get('role_display'),
            "is_active": directeur.get('is_active'),
            "matricule": directeur.get('matricule'),
            "telephone": directeur.get('telephone'),
            "photo_profil": directeur.get('photo_profil'),
            "activite_id": activite_id,
            "activite": activite_data
        })
    
    # Statistiques
    total_avec_activite = len(data)
    
    return Response({
        "status": "success",
        "code": "DIRECTEURS_AVEC_ACTIVITE",
        "message": f"{total_avec_activite} directeur(s) d'activité avec activité affectée",
        "data": {
            "count": total_avec_activite,
            "directeurs": data
        },
        "timestamp": datetime.now().isoformat()
    }, status=200)
# ==========================
# 3. LISTER TOUS LES DIRECTEURS D'ACTIVITÉ (avec et sans activité)
# ==========================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_all_directeurs_activite(request):
    """
    GET /affectation/users/directeurs-activite/all/
    
    Liste TOUS les directeurs d'activité (avec ET sans activité affectée)
    Inclut les détails de l'activité si présente
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
    # Paramètres optionnels
    show_inactive = request.query_params.get('show_inactive', '').lower() == 'true'
    
    # Récupérer tous les utilisateurs
    sc, users_response = _call_auth('get', '/auth/users/', token)
    
    if sc != 200:
        return Response(
            {"status": "error", "code": "AUTH_SERVICE_ERROR",
             "message": "Impossible de récupérer la liste des utilisateurs"},
            status=503,
        )
    
    users = users_response.get('users', [])
    
    # Filtrer: tous les directeurs d'activité
    directeurs = [
        u for u in users 
        if u.get('role') == 'directeur_activite'
    ]
    
    # Filtrer les inactifs si demandé
    if not show_inactive:
        directeurs = [d for d in directeurs if d.get('is_active', True)]
    
    # Récupérer les détails des activités pour chaque directeur
    data = []
    for directeur in directeurs:
        activite_id = directeur.get('activite_id')
        activite_data = None
        
        # Récupérer l'activité depuis le service juridique si elle existe
        if activite_id:
            sc_act, activite_response = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
            if sc_act == 200:
                activite_data = activite_response.get('data', {})
        
        data.append({
            "id": directeur.get('id'),
            "email": directeur.get('email'),
            "nom": directeur.get('nom'),
            "prenom": directeur.get('prenom'),
            "nom_complet": directeur.get('nom_complet'),
            "role": directeur.get('role'),
            "role_display": directeur.get('role_display'),
            "is_active": directeur.get('is_active'),
            "matricule": directeur.get('matricule'),
            "telephone": directeur.get('telephone'),
            "photo_profil": directeur.get('photo_profil'),
            "activite_id": activite_id,
            "activite": activite_data,
            "has_activite": activite_id is not None
        })
    
    # Statistiques
    total = len(data)
    avec_activite = len([d for d in data if d.get('has_activite')])
    sans_activite = total - avec_activite
    actifs = len([d for d in data if d.get('is_active')])
    inactifs = total - actifs
    
    return Response({
        "status": "success",
        "code": "ALL_DIRECTEURS_ACTIVITE",
        "message": f"Total: {total} directeur(s) d'activité",
        "data": {
            "count": total,
            "statistics": {
                "with_activite": avec_activite,
                "without_activite": sans_activite,
                "active": actifs,
                "inactive": inactifs
            },
            "directeurs": data
        },
        "timestamp": datetime.now().isoformat()
    }, status=200)










####################### Direction ########################
# ==========================
# DIRECTIONS - Assignation
# ==========================

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def assign_direction_to_user(request):
    """
    PATCH /affectation/assign-direction/
    Body: { "user_id": 2, "direction_id": "672a1b2c3d4e5f6789abcdef" }
    
    Affecte une direction à un utilisateur (directeur_direction)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user
    
    user_id = request.data.get('user_id')
    direction_id = request.data.get('direction_id')
    
    if not user_id:
        return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
    if not direction_id:
        return Response({"status": "error", "code": "MISSING_DIRECTION_ID", "message": "direction_id est obligatoire."}, status=400)
    
    # Récupérer l'utilisateur
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)
    
    user_data = user_response.get('user', {})
    
    # Vérifier le rôle
    if user_data.get('role') != 'directeur_direction':
        return Response({"status": "error", "code": "INVALID_ROLE", "message": f"L'utilisateur doit être 'directeur_direction' (actuel: {user_data.get('role')})"}, status=400)
    
    # Vérifier si déjà affecté
    existing_direction_id = user_data.get('direction_id')
    if existing_direction_id:
        existing_direction_nom = "Inconnue"
        sc_existing, existing_direction = _call_juridique('get', f'/juridique/directions/{existing_direction_id}/', token)
        if sc_existing == 200:
            existing_direction_nom = existing_direction.get('data', {}).get('nom', 'Inconnue')
        
        return Response({"status": "error", "code": "ALREADY_ASSIGNED", "message": "L'utilisateur a déjà une direction affectée.", "data": {"existing_direction_id": existing_direction_id, "existing_direction_nom": existing_direction_nom}}, status=400)
    
    # Récupérer la direction
    sc_dir, direction_response = _call_juridique('get', f'/juridique/directions/{direction_id}/', token)
    if sc_dir == 404:
        return Response({"status": "error", "code": "DIRECTION_NOT_FOUND", "message": f"Direction {direction_id} non trouvée."}, status=404)
    if sc_dir != 200:
        return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible"}, status=503)
    
    direction_info = direction_response.get('data', {})
    direction_nom = direction_info.get('nom', 'Unknown')
    
    # Mettre à jour
    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": direction_id})
    if sc_update != 200:
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour"}, status=sc_update)
    
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success", "code": "DIRECTION_ASSIGNED",
        "message": f"Direction '{direction_nom}' affectée à {nom_complet}.",
        "data": {"user_id": user_id, "user_name": nom_complet, "direction_id": direction_id, "direction_nom": direction_nom, "direction_details": direction_info}
    }, status=200)


@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def reassign_direction_to_user(request):
    """
    PUT /affectation/reassign-direction/
    Body: { "user_id": 2, "direction_id": "672a1b2c3d4e5f6789abcdef" }
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user
    
    user_id = request.data.get('user_id')
    direction_id = request.data.get('direction_id')
    
    if not user_id or not direction_id:
        return Response({"status": "error", "message": "user_id et direction_id requis"}, status=400)
    
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
    user_data = user_response.get('user', {})
    
    if user_data.get('role') != 'directeur_direction':
        return Response({"status": "error", "message": "L'utilisateur doit être 'directeur_direction'"}, status=400)
    
    old_direction_id = user_data.get('direction_id')
    old_direction_nom = None
    if old_direction_id:
        sc_old, old_direction = _call_juridique('get', f'/juridique/directions/{old_direction_id}/', token)
        if sc_old == 200:
            old_direction_nom = old_direction.get('data', {}).get('nom', 'Inconnue')
    
    sc_dir, direction_response = _call_juridique('get', f'/juridique/directions/{direction_id}/', token)
    if sc_dir != 200:
        return Response({"status": "error", "message": "Direction non trouvée"}, status=404)
    
    direction_info = direction_response.get('data', {})
    direction_nom = direction_info.get('nom', 'Unknown')
    
    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": direction_id})
    if sc_update != 200:
        return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)
    
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success", "code": "DIRECTION_REASSIGNED",
        "message": f"Direction changée de '{old_direction_nom or 'aucune'}' vers '{direction_nom}'",
        "data": {"user_id": user_id, "user_name": nom_complet, "previous_direction_id": old_direction_id, "previous_direction_nom": old_direction_nom, "new_direction_id": direction_id, "new_direction_nom": direction_nom}
    }, status=200)


@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def remove_direction_from_user(request, user_id):
    """DELETE /affectation/users/<user_id>/remove-direction/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
    user_data = user_response.get('user', {})
    current_direction_id = user_data.get('direction_id')
    
    if not current_direction_id:
        return Response({"status": "error", "code": "NO_DIRECTION_ASSIGNED", "message": "Aucune direction affectée"}, status=400)
    
    direction_nom = "Inconnue"
    sc_dir, direction_response = _call_juridique('get', f'/juridique/directions/{current_direction_id}/', token)
    if sc_dir == 200:
        direction_nom = direction_response.get('data', {}).get('nom', 'Inconnue')
    
    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": None})
    if sc_update != 200:
        return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)
    
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success", "code": "DIRECTION_REMOVED",
        "message": f"Direction '{direction_nom}' désaffectée de {nom_complet}",
        "data": {"user_id": user_id, "user_name": nom_complet, "removed_direction_id": current_direction_id, "removed_direction_nom": direction_nom}
    }, status=200)


# ==========================
# DIRECTIONS - Listes
# ==========================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_direction(request):
    """GET /affectation/users/directeurs-direction/ - Directeurs SANS direction"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
    users = users_response.get('users', [])
    directeurs_sans = [u for u in users if u.get('role') == 'directeur_direction' and not u.get('direction_id')]
    
    data = [{"id": d.get('id'), "email": d.get('email'), "nom": d.get('nom'), "prenom": d.get('prenom'), "nom_complet": d.get('nom_complet'), "is_active": d.get('is_active')} for d in directeurs_sans]
    
    return Response({"status": "success", "code": "DIRECTEURS_DIRECTION_SANS", "message": f"{len(data)} directeur(s) de direction sans affectation", "data": {"count": len(data), "directeurs": data}}, status=200)


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_direction_affectes(request):
    """GET /affectation/users/directeurs-direction/affectes/ - Directeurs AVEC direction"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
    users = users_response.get('users', [])
    directeurs_avec = [u for u in users if u.get('role') == 'directeur_direction' and u.get('direction_id')]
    
    data = []
    for d in directeurs_avec:
        direction_data = None
        if d.get('direction_id'):
            sc_dir, dir_response = _call_juridique('get', f'/juridique/directions/{d["direction_id"]}/', token)
            if sc_dir == 200:
                direction_data = dir_response.get('data', {})
        
        data.append({"id": d.get('id'), "nom_complet": d.get('nom_complet'), "direction_id": d.get('direction_id'), "direction": direction_data})
    
    return Response({"status": "success", "code": "DIRECTEURS_DIRECTION_AVEC", "data": {"count": len(data), "directeurs": data}}, status=200)


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_all_directeurs_direction(request):
    """GET /affectation/users/directeurs-direction/all/ - TOUS les directeurs de direction"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
    users = users_response.get('users', [])
    directeurs = [u for u in users if u.get('role') == 'directeur_direction']
    
    data = []
    for d in directeurs:
        direction_data = None
        if d.get('direction_id'):
            sc_dir, dir_response = _call_juridique('get', f'/juridique/directions/{d["direction_id"]}/', token)
            if sc_dir == 200:
                direction_data = dir_response.get('data', {})
        
        data.append({"id": d.get('id'), "nom_complet": d.get('nom_complet'), "is_active": d.get('is_active'), "direction_id": d.get('direction_id'), "direction": direction_data, "has_direction": d.get('direction_id') is not None})
    
    avec = len([x for x in data if x.get('has_direction')])
    sans = len(data) - avec
    
    return Response({"status": "success", "code": "ALL_DIRECTEURS_DIRECTION", "data": {"count": len(data), "statistics": {"with_direction": avec, "without_direction": sans}, "directeurs": data}}, status=200)

# ──────────────────────────────────────────────
# VIEW : GET USER (via Gateway ou Eureka)
# ──────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def get_user(request, user_id):
    """
    GET /affectation/user/<user_id>/
    Récupère les informations d'un utilisateur (admin seulement)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    force_gateway = request.query_params.get('force_gateway', '').lower() == 'true'
    
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token, use_gateway=force_gateway)
    
    if sc != 200:
        return Response(user_response, status=sc)
    
    return Response({
        "status": "success",
        "data": user_response.get('user', user_response),
        "metadata": {
            "source": "gateway" if force_gateway else "eureka"
        }
    })






# ==========================
# DÉPARTEMENTS - Assignation (avec vérification direction automatique)
# ==========================

# affectation/views.py - Code complet pour les départements

# ==========================
# HELPER - Appel spécifique pour département
# ==========================

def _call_auth_update_departement(user_id: int, departement_id: str, direction_id: str, token: str):
    """
    Appel spécifique pour mettre à jour le département et la direction d'un utilisateur
    Utilise l'endpoint dédié pour directeur_direction
    """
    base_url = get_auth_base_url()
    path = f'/auth/users/{user_id}/update-departement/'
    url = f"{base_url}{path}"
    headers = {'Authorization': f'Bearer {token}'}
    
    update_data = {
        "departement_id": departement_id,
        "direction_id": direction_id
    }
    
    print(f'[AFFECTATION] → PATCH {url}')
    print(f'[AFFECTATION] → Data: {update_data}')
    
    try:
        resp = requests.patch(
            url,
            headers=headers,
            json=update_data,
            timeout=5
        )
        print(f'[AFFECTATION] ← {resp.status_code}')
        
        if resp.status_code == 200:
            return resp.status_code, resp.json()
        return resp.status_code, {"error": resp.text}
        
    except requests.RequestException as e:
        print(f'[AFFECTATION] ✗ Erreur: {e}')
        return 503, {"status": "error", "message": str(e)}


# ==========================
# DÉPARTEMENTS - Assignation
# ==========================

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def assign_departement_to_user(request):
    """
    PATCH /affectation/assign-departement/
    Body: { "user_id": 2, "departement_id": "672a1b2c3d4e5f6789abcdef" }
    
    Affecte un département à un responsable_departement
    Met à jour automatiquement direction_id et departement_id
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user
    
    user_id = request.data.get('user_id')
    departement_id = request.data.get('departement_id')
    
    # ── Validation ──
    if not user_id:
        return Response({
            "status": "error", "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)
    
    if not departement_id:
        return Response({
            "status": "error", "code": "MISSING_DEPARTEMENT_ID",
            "message": "departement_id est obligatoire."
        }, status=400)
    
    # Vérifier que le directeur a une direction_id
    directeur_direction_id = getattr(directeur, 'direction_id', None)
    if not directeur_direction_id:
        return Response({
            "status": "error", "code": "DIRECTEUR_NO_DIRECTION",
            "message": "Vous n'avez pas de direction associée."
        }, status=403)
    
    # ── Étape 1 : Récupérer l'utilisateur cible ──
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
    if sc != 200:
        return Response({
            "status": "error", "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} introuvable."
        }, status=404)
    
    user_data = user_response.get('user', {})
    
    # Vérifier le rôle
    if user_data.get('role') != 'responsable_departement':
        return Response({
            "status": "error", "code": "INVALID_ROLE",
            "message": f"L'utilisateur doit être 'responsable_departement' (actuel: {user_data.get('role')})"
        }, status=400)
    
    # Vérifier si déjà affecté
    existing_departement_id = user_data.get('departement_id')
    if existing_departement_id:
        existing_nom = "Inconnu"
        sc_exist, exist_response = _call_juridique('get', f'/juridique/departements/{existing_departement_id}/', token)
        if sc_exist == 200:
            existing_nom = exist_response.get('data', {}).get('nom', 'Inconnu')
        
        return Response({
            "status": "error", "code": "ALREADY_ASSIGNED",
            "message": f"L'utilisateur a déjà un département: '{existing_nom}'",
            "suggestion": "Utilisez PUT /affectation/reassign-departement/ pour changer"
        }, status=400)
    
    # ── Étape 2 : Récupérer le département ──
    sc_dep, departement_response = _call_juridique('get', f'/juridique/departements/{departement_id}/', token)
    
    if sc_dep == 404:
        return Response({
            "status": "error", "code": "DEPARTEMENT_NOT_FOUND",
            "message": f"Département {departement_id} non trouvé."
        }, status=404)
    
    if sc_dep != 200:
        return Response({
            "status": "error", "code": "JURIDIQUE_SERVICE_ERROR",
            "message": "Service juridique indisponible"
        }, status=503)
    
    departement_info = departement_response.get('data', {})
    departement_nom = departement_info.get('nom', 'Unknown')
    
    # Vérifier que le département appartient à la direction du directeur
    departement_direction_id = departement_info.get('direction', {}).get('_id') or departement_info.get('direction')
    
    if str(directeur_direction_id) != str(departement_direction_id):
        direction_nom = "Inconnue"
        sc_dir, dir_response = _call_juridique('get', f'/juridique/directions/{directeur_direction_id}/', token)
        if sc_dir == 200:
            direction_nom = dir_response.get('data', {}).get('nom', 'Inconnue')
        
        return Response({
            "status": "error", "code": "DEPARTEMENT_NOT_IN_DIRECTION",
            "message": f"Ce département n'appartient pas à votre direction '{direction_nom}'."
        }, status=403)
    
    # ── Étape 3 : Mettre à jour l'utilisateur ──
    sc_update, updated = _call_auth_update_departement(
        user_id=user_id,
        departement_id=departement_id,
        direction_id=directeur_direction_id,
        token=token
    )
    
    if sc_update != 200:
        return Response({
            "status": "error", "code": "UPDATE_FAILED",
            "message": "Impossible de mettre à jour l'utilisateur.",
            "detail": updated
        }, status=sc_update)
    
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success", "code": "DEPARTEMENT_ASSIGNED",
        "message": f"Département '{departement_nom}' affecté à {nom_complet}.",
        "data": {
            "user_id": int(user_id),
            "user_name": nom_complet,
            "user_email": user_data.get('email'),
            "user_role": user_data.get('role'),
            "direction_id": directeur_direction_id,
            "departement_id": departement_id,
            "departement_nom": departement_nom,
            "departement_details": departement_info,
            "assigned_by": {
                "id": directeur.id,
                "name": getattr(directeur, 'nom_complet', str(directeur)),
                "role": directeur.role,
                "direction_id": directeur_direction_id
            },
            "timestamp": datetime.now().isoformat()
        }
    }, status=200)


@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def reassign_departement_to_user(request):
    """
    PUT /affectation/reassign-departement/
    Body: { "user_id": 2, "departement_id": "672a1b2c3d4e5f6789abcdef" }
    
    Réaffecte un département (change même si déjà affecté)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user
    
    user_id = request.data.get('user_id')
    departement_id = request.data.get('departement_id')
    
    if not user_id or not departement_id:
        return Response({
            "status": "error", "message": "user_id et departement_id requis"
        }, status=400)
    
    directeur_direction_id = getattr(directeur, 'direction_id', None)
    if not directeur_direction_id:
        return Response({
            "status": "error", "code": "DIRECTEUR_NO_DIRECTION",
            "message": "Vous n'avez pas de direction associée."
        }, status=403)
    
    # Récupérer l'utilisateur
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
    user_data = user_response.get('user', {})
    
    if user_data.get('role') != 'responsable_departement':
        return Response({
            "status": "error", "message": "L'utilisateur doit être 'responsable_departement'"
        }, status=400)
    
    # Récupérer le nouveau département
    sc_dep, departement_response = _call_juridique('get', f'/juridique/departements/{departement_id}/', token)
    if sc_dep != 200:
        return Response({"status": "error", "message": "Département non trouvé"}, status=404)
    
    departement_info = departement_response.get('data', {})
    departement_nom = departement_info.get('nom', 'Unknown')
    
    # Vérifier que le département appartient à la direction
    departement_direction_id = departement_info.get('direction', {}).get('_id') or departement_info.get('direction')
    if str(directeur_direction_id) != str(departement_direction_id):
        return Response({
            "status": "error", "code": "DEPARTEMENT_NOT_IN_DIRECTION",
            "message": "Ce département n'appartient pas à votre direction."
        }, status=403)
    
    # Ancien département
    old_departement_id = user_data.get('departement_id')
    old_departement_nom = "Inconnu"
    if old_departement_id:
        sc_old, old_response = _call_juridique('get', f'/juridique/departements/{old_departement_id}/', token)
        if sc_old == 200:
            old_departement_nom = old_response.get('data', {}).get('nom', 'Inconnu')
    
    # Mettre à jour
    sc_update, _ = _call_auth_update_departement(
        user_id=user_id,
        departement_id=departement_id,
        direction_id=directeur_direction_id,
        token=token
    )
    
    if sc_update != 200:
        return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)
    
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success", "code": "DEPARTEMENT_REASSIGNED",
        "message": f"Département changé de '{old_departement_nom}' vers '{departement_nom}'",
        "data": {
            "user_id": user_id, 
            "user_name": nom_complet,
            "previous_departement_id": old_departement_id, 
            "previous_departement_nom": old_departement_nom,
            "new_departement_id": departement_id, 
            "new_departement_nom": departement_nom
        }
    }, status=200)


# affectation/views.py

# affectation/views.py - Modifier remove_departement_from_user

@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def remove_departement_from_user(request, user_id):
    """
    DELETE /affectation/users/<user_id>/remove-departement/
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user
    
    directeur_direction_id = getattr(directeur, 'direction_id', None)
    
    # Récupérer l'utilisateur
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
    user_data = user_response.get('user', {})
    current_departement_id = user_data.get('departement_id')
    current_direction_id = user_data.get('direction_id')
    
    if not current_departement_id:
        return Response({"status": "error", "message": "Aucun département affecté"}, status=400)
    
    # Récupérer le nom du département
    departement_nom = "Inconnu"
    sc_dep, departement_response = _call_juridique('get', f'/juridique/departements/{current_departement_id}/', token)
    if sc_dep == 200:
        departement_nom = departement_response.get('data', {}).get('nom', 'Inconnu')
    
    # Supprimer les affectations
    sc_update, updated = _call_auth_update_departement(
        user_id=user_id,
        departement_id=None,
        direction_id=None,
        token=token
    )
    
    if sc_update != 200:
        return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)
    
    # ✅ Option 2: Invalider le refresh token pour forcer la reconnexion
    try:
        # Appeler un endpoint pour blacklister les tokens de l'utilisateur
        _call_auth('post', f'/auth/users/{user_id}/logout-all/', token)
    except:
        pass  # Ignorer si l'endpoint n'existe pas
    
    nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
    return Response({
        "status": "success", 
        "code": "DEPARTEMENT_REMOVED",
        "message": f"Département '{departement_nom}' désaffecté de {nom_complet}",
        "data": {
            "user_id": user_id,
            "user_name": nom_complet,
            "removed_departement_id": current_departement_id,
            "removed_departement_nom": departement_nom,
            "new_departement_id": None,
            "new_direction_id": None,
            "requires_relogin": True,  # ✅ Indiquer que l'utilisateur doit se reconnecter
            "message_for_user": "Veuillez vous reconnecter pour que les changements prennent effet",
            "removed_by": {
                "id": directeur.id,
                "name": getattr(directeur, 'nom_complet', str(directeur)),
                "role": directeur.role
            },
            "timestamp": datetime.now().isoformat()
        }
    }, status=200)

# ==========================
# DÉPARTEMENTS - Listes
# ==========================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def api_list_responsables_departement(request):
    """
    GET /affectation/users/responsables-departement/
    Liste les responsables SANS département (dans la direction du directeur)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user
    
    directeur_direction_id = getattr(directeur, 'direction_id', None)
    
    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
    users = users_response.get('users', [])
    
    # Filtrer responsables département
    responsables = [u for u in users if u.get('role') == 'responsable_departement']
    
    # Filtrer ceux sans direction_id (disponibles pour affectation dans n'importe quelle direction)
    responsables_disponibles = [r for r in responsables if r.get('direction_id') is None]
    
    # Filtrer ceux sans département
    responsables_sans = [r for r in responsables_disponibles if not r.get('departement_id')]
    
    data = [{
        "id": r.get('id'), 
        "email": r.get('email'),
        "nom": r.get('nom'), 
        "prenom": r.get('prenom'),
        "nom_complet": r.get('nom_complet'), 
        "is_active": r.get('is_active')
    } for r in responsables_sans]
    
    return Response({
        "status": "success", 
        "code": "RESPONSABLES_SANS_DEPARTEMENT",
        "data": {"count": len(data), "responsables": data}
    }, status=200)


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def api_list_responsables_departement_affectes(request):
    """
    GET /affectation/users/responsables-departement/affectes/
    Liste les responsables AVEC département (de la direction du directeur)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user
    
    directeur_direction_id = getattr(directeur, 'direction_id', None)
    
    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
    users = users_response.get('users', [])
    
    responsables = [u for u in users if u.get('role') == 'responsable_departement']
    
    # Filtrer ceux de la direction du directeur
    if directeur_direction_id:
        responsables = [r for r in responsables if r.get('direction_id') == directeur_direction_id]
    
    responsables_avec = [r for r in responsables if r.get('departement_id')]
    
    data = []
    for r in responsables_avec:
        departement_data = None
        if r.get('departement_id'):
            sc_dep, dep_response = _call_juridique('get', f'/juridique/departements/{r["departement_id"]}/', token)
            if sc_dep == 200:
                departement_data = dep_response.get('data', {})
        
        data.append({
            "id": r.get('id'), 
            "nom_complet": r.get('nom_complet'),
            "direction_id": r.get('direction_id'),
            "departement_id": r.get('departement_id'), 
            "departement": departement_data
        })
    
    return Response({
        "status": "success", 
        "code": "RESPONSABLES_AVEC_DEPARTEMENT",
        "data": {"count": len(data), "responsables": data}
    }, status=200)


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def api_list_all_responsables_departement(request):
    """
    GET /affectation/users/responsables-departement/all/
    Liste TOUS les responsables département (de la direction du directeur)
    """
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user
    
    directeur_direction_id = getattr(directeur, 'direction_id', None)
    
    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
    users = users_response.get('users', [])
    
    responsables = [u for u in users if u.get('role') == 'responsable_departement']
    
    # Filtrer ceux de la direction du directeur ou sans direction
    if directeur_direction_id:
        responsables = [r for r in responsables if r.get('direction_id') == directeur_direction_id or r.get('direction_id') is None]
    
    data = []
    for r in responsables:
        departement_data = None
        if r.get('departement_id'):
            sc_dep, dep_response = _call_juridique('get', f'/juridique/departements/{r["departement_id"]}/', token)
            if sc_dep == 200:
                departement_data = dep_response.get('data', {})
        
        data.append({
            "id": r.get('id'), 
            "nom_complet": r.get('nom_complet'),
            "email": r.get('email'),
            "is_active": r.get('is_active'), 
            "direction_id": r.get('direction_id'),
            "departement_id": r.get('departement_id'), 
            "departement": departement_data,
            "has_departement": r.get('departement_id') is not None
        })
    
    avec = len([x for x in data if x.get('has_departement')])
    sans = len(data) - avec
    
    return Response({
        "status": "success", 
        "code": "ALL_RESPONSABLES_DEPARTEMENT",
        "data": {
            "count": len(data),
            "statistics": {"with_departement": avec, "without_departement": sans},
            "responsables": data
        }
    }, status=200)