


# """
# views.py — Service Affectation (port 8011)
# """

# import requests
# from datetime import datetime
# from django.core.cache import cache
# from django.conf import settings

# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from rest_framework.response import Response
# from rest_framework.permissions import BasePermission

# from .authentication import RemoteJWTAuthentication
# from .discovery import get_auth_base_url, get_gateway_url, AUTH_APP_NAME
# from .permissions import *
# from .serializers import (
#     UserDetailSerializer,
#     UserByIdSerializer,
#     UserSummarySerializer,
# )


# # ──────────────────────────────────────────────
# # RÔLES VALIDES
# # ──────────────────────────────────────────────

# VALID_ROLES = [
#     'agent',
#     'vice_presedent',
#     'directeur_direction',
#     'responsable_departement',
#     'directeur_centrale',        
#     'assistant_directeur_centrale',  
#     'directeur_direction_activite', 
#     'directeur_division_activite',    
#     'responsable_direction_division',
#     'responsable_departement_division',             

# ]

# ROLE_DISPLAY = {
#     'agent':                   'Agent',
#     'vice_presedent':      'Vice Presedent',
#     'directeur_direction':     'Directeur de Direction',
#     'responsable_departement': 'Responsable de Département',
#     'directeur_centrale': 'Directeur Centrale',
#     'assistant_directeur_centrale': 'Assistant Directeur Centrale',
#     'directeur_direction_activite': 'Directeur Direction Activité',
#     'directeur_division_activite': 'Directeur Division Activité',
#     'responsable_direction_division': 'Responsable Direction Division',
#     'responsable_departement_division': 'Responsable Département Division',
# }




# # ──────────────────────────────────────────────
# # PERMISSION
# # ──────────────────────────────────────────────

# class IsAdmin(BasePermission):
#     message = "Accès réservé aux administrateurs."
#     def has_permission(self, request, view):
#         return (
#             request.user
#             and request.user.is_authenticated
#             and getattr(request.user, 'role', '') == 'admin'
#         )


# # ──────────────────────────────────────────────
# # HELPER HTTP — appel vers le service Auth
# # ──────────────────────────────────────────────

# def _call_auth(method: str, path: str, token: str, use_gateway: bool = False, **kwargs):
#     """
#     Appelle le service Auth (résolu via Eureka ou Gateway).
#     Retourne (status_code, dict).
    
#     Args:
#         method: HTTP method (get, post, patch, etc.)
#         path: Chemin de l'API (ex: /auth/users/2/)
#         token: JWT token
#         use_gateway: Force l'utilisation de la Gateway au lieu d'Eureka
#         **kwargs: Arguments supplémentaires pour requests (json, etc.)
#     """
#     # Choisir la base URL
#     if use_gateway:
#         base_url = get_gateway_url()
#         print(f'[AFFECTATION] 🌐 Utilisation de la Gateway: {base_url}')
#     else:
#         base_url = get_auth_base_url()
#         print(f'[AFFECTATION] 🔍 Utilisation de Eureka: {base_url}')
    
#     url = f"{base_url}{path}"
#     headers = {'Authorization': f'Bearer {token}'}

#     print(f'[AFFECTATION] → {method.upper()} {url}')

#     try:
#         resp = getattr(requests, method)(
#             url, headers=headers, timeout=5, **kwargs
#         )
#         print(f'[AFFECTATION] ← {resp.status_code} | body: {repr(resp.text[:200])}')

#         # Réponse vide (204, ou body vide) → dict vide
#         if not resp.text.strip():
#             return resp.status_code, {}

#         return resp.status_code, resp.json()

#     except requests.exceptions.JSONDecodeError as e:
#         print(f'[AFFECTATION] ✗ JSON decode error: {e} | raw: {repr(resp.text[:300])}')
#         return resp.status_code, {"raw": resp.text}

#     except requests.RequestException as e:
#         print(f'[AFFECTATION] ✗ Réseau: {e}')
#         # Invalider le cache Eureka en cas d'erreur réseau
#         cache.delete(f'eureka_url_{AUTH_APP_NAME}')
        
#         # Si on n'utilisait pas déjà la Gateway, essayer en fallback
#         if not use_gateway:
#             print(f'[AFFECTATION] 🔄 Fallback: tentative via Gateway...')
#             return _call_auth(method, path, token, use_gateway=True, **kwargs)
        
#         return 503, {"status": "error", "message": f"Service Auth injoignable : {e}"}


# # def _call_juridique(method: str, path: str, token: str, **kwargs):
# #     """
# #     Appelle le service Juridique (Node.js) via Eureka ou Gateway
# #     """
# #     try:
# #         from .discovery import get_juridique_base_url, get_gateway_url
# #         juridique_url = get_juridique_base_url()
# #     except:
# #         juridique_url = os.getenv('GATEWAY_URL', 'http://localhost:8083')
    
# #     url = f"{juridique_url}{path}"
# #     headers = {'Authorization': f'Bearer {token}'}
    
# #     print(f'[AFFECTATION] → Juridique {method.upper()} {url}')
    
# #     try:
# #         resp = getattr(requests, method)(
# #             url, headers=headers, timeout=5, **kwargs
# #         )
# #         print(f'[AFFECTATION] ← Juridique {resp.status_code}')
        
# #         if not resp.text.strip():
# #             return resp.status_code, {}
# #         return resp.status_code, resp.json()
        
# #     except requests.RequestException as e:
# #         print(f'[AFFECTATION] ✗ Erreur juridique: {e}')
# #         return 503, {"status": "error", "message": f"Service juridique injoignable: {e}"}
# def _call_juridique(method: str, path: str, token: str, **kwargs):
#     """
#     Appelle le service Juridique (Node.js) via Eureka ou Gateway
#     """
#     try:
#         from .discovery import get_juridique_base_url
#         juridique_url = get_juridique_base_url()
#     except Exception:
#         import os  # ✅ CORRECTION: import os était manquant
#         juridique_url = os.getenv('GATEWAY_URL', 'http://localhost:8083')
    
#     url = f"{juridique_url}{path}"
#     headers = {'Authorization': f'Bearer {token}'}
    
#     print(f'[AFFECTATION] → Juridique {method.upper()} {url}')
    
#     try:
#         resp = getattr(requests, method)(
#             url, headers=headers, timeout=5, **kwargs
#         )
#         print(f'[AFFECTATION] ← Juridique {resp.status_code}')
        
#         if not resp.text.strip():
#             return resp.status_code, {}
#         return resp.status_code, resp.json()
        
#     except requests.RequestException as e:
#         print(f'[AFFECTATION] ✗ Erreur juridique: {e}')
#         return 503, {"status": "error", "message": f"Service juridique injoignable: {e}"} 
# # ──────────────────────────────────────────────
# # VIEW : ASSIGN ROLE
# # ──────────────────────────────────────────────

# @api_view(['POST'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def assign_role(request):
#     """
#     POST /affectation/assign-role/
#     Body : { "user_id": 2, "role": "vice_presedent" }
    
#     Query params optionnels:
#     ?force_gateway=true - Force l'utilisation de la Gateway au lieu d'Eureka
#     """
#     # Vérifier si on force l'utilisation de la Gateway
#     force_gateway = request.query_params.get('force_gateway', '').lower() == 'true'
    
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user

#     user_id = request.data.get('user_id')
#     role = request.data.get('role')

#     # ── Validation ──
#     if not user_id:
#         return Response(
#             {"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."},
#             status=400,
#         )
#     if not role:
#         return Response(
#             {"status": "error", "code": "MISSING_ROLE", "message": "role est obligatoire."},
#             status=400,
#         )
#     if role not in VALID_ROLES:
#         return Response(
#             {"status": "error", "code": "INVALID_ROLE",
#              "message": f"Rôle '{role}' invalide.", "valid_roles": VALID_ROLES},
#             status=400,
#         )

#     print(f'[AFFECTATION] 📝 Assignation rôle: user_id={user_id}, role={role}, force_gateway={force_gateway}')

#     # ── Étape 1 : récupérer l'user cible ──
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token, use_gateway=force_gateway)

#     print(f'[AFFECTATION] user_response reçu: status={sc}')

#     if sc == 503:
#         return Response(user_response, status=503)
#     if sc == 404:
#         return Response(
#             {"status": "error", "code": "USER_NOT_FOUND",
#              "message": f"Utilisateur {user_id} introuvable."},
#             status=404,
#         )
#     if sc != 200:
#         return Response(
#             {"status": "error", "code": "AUTH_SERVICE_ERROR",
#              "message": f"Service Auth a retourné {sc}.", "detail": user_response},
#             status=sc,
#         )

#     # Extraire les données utilisateur de la réponse imbriquée
#     user_data = user_response.get('user', {})
    
#     if not user_data:
#         return Response(
#             {"status": "error", "code": "INVALID_RESPONSE",
#              "message": "Structure de réponse invalide du service Auth."},
#             status=500,
#         )

#     if user_data.get('role') == 'admin':
#         return Response(
#             {"status": "error", "code": "CANNOT_MODIFY_ADMIN",
#              "message": "Impossible de modifier le rôle d'un administrateur."},
#             status=400,
#         )

#     previous_role = user_data.get('role')

#     # ── Étape 2 : Mettre à jour le rôle ──
#     sc, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update-role/',
#         token,
#         json={"role": role},
#         use_gateway=force_gateway,
#     )

#     if sc == 503:
#         return Response(updated, status=503)
#     if sc not in (200, 201):
#         return Response(
#             {"status": "error", "code": "UPDATE_FAILED",
#              "message": f"Impossible de mettre à jour le rôle (status {sc}).",
#              "detail": updated},
#             status=sc,
#         )

#     # ── Construction de la réponse ──
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     # Récupérer le nom de l'admin qui fait la requête
#     admin_name = getattr(admin, 'nom_complet', None)
#     if not admin_name:
#         admin_prenom = getattr(admin, 'prenom', '')
#         admin_nom = getattr(admin, 'nom', '')
#         admin_name = f"{admin_prenom} {admin_nom}".strip() or str(admin)
    
#     admin_role = getattr(admin, 'role', 'unknown')
    
#     # Ajouter des métadonnées sur la source de l'appel
#     response_data = {
#         "status": "success",
#         "code": "ROLE_ASSIGNED",
#         "message": (
#             f"Rôle '{ROLE_DISPLAY.get(role, role)}' affecté à "
#             f"{nom_complet}."
#         ),
#         "data": {
#             "user_id":          user_id,
#             "user_name":        nom_complet,
#             "email":            user_data.get('email'),
#             "previous_role":    previous_role,
#             "previous_role_display": ROLE_DISPLAY.get(previous_role, previous_role) if previous_role else None,
#             "new_role":         role,
#             "new_role_display": ROLE_DISPLAY.get(role, role),
#             "assigned_by": {
#                 "id":   admin.id,
#                 "name": admin_name,
#                 "role": admin_role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         },
#         "metadata": {
#             "source": "gateway" if force_gateway else "eureka",
#             "service": "affectation-service",
#             "version": "1.0.0"
#         }
#     }
    
#     # Si on a utilisé le fallback, l'indiquer dans la réponse
#     if not force_gateway and sc == 200:
#         response_data["metadata"]["discovery_method"] = "eureka"
#     elif force_gateway:
#         response_data["metadata"]["discovery_method"] = "gateway_forced"
    
#     return Response(response_data, status=200)

    
# # ──────────────────────────────────────────────
# # VIEW : AFFECTATION (ACTIVITE,DEPARTEMENT,DIRECTION)
# # ──────────────────────────────────────────────

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def assign_activite_to_user(request):
#     """
#     PATCH /affectation/assign-activite/
#     Body: { "user_id": 2, "activite_id": "672a1b2c3d4e5f6789abcdef" }
    
#     1. Vérifie que l'utilisateur a le rôle 'vice_presedent'
#     2. Vérifie que l'utilisateur n'a PAS déjà une activité affectée
#     3. Récupère l'activité depuis le service juridique
#     4. Met à jour l'activite_id de l'utilisateur dans le service Auth
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user
    
#     user_id = request.data.get('user_id')
#     activite_id = request.data.get('activite_id')
    
#     # ── Validation ──
#     if not user_id:
#         return Response(
#             {"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."},
#             status=400,
#         )
#     if not activite_id:
#         return Response(
#             {"status": "error", "code": "MISSING_ACTIVITE_ID", "message": "activite_id est obligatoire."},
#             status=400,
#         )
    
#     # ── Étape 1 : Récupérer l'utilisateur depuis Auth ──
#     # sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
#     # if sc != 200:
#     #     return Response(
#     #         {"status": "error", "code": "USER_NOT_FOUND",
#     #          "message": f"Utilisateur {user_id} introuvable."},
#     #         status=404,
#     #     )
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
 
#     if sc == 200:
#         s = UserDetailSerializer(data=user_response.get('user', {}))
#         s.is_valid()                     # valide et normalise tous les champs
#         user_data = s.data               # dict validé et typé
    
#         nom_complet = user_data['nom_complet']
#         email       = user_data['email']
#         role        = user_data['role']  # None si absent, jamais KeyError

    
#     user_data = user_response.get('user', {})
    
#     # Vérifier que l'utilisateur a le bon rôle
#     if user_data.get('role') != 'vice_presedent':
#         return Response(
#             {"status": "error", "code": "INVALID_ROLE",
#              "message": f"L'utilisateur a le rôle '{user_data.get('role')}', doit être 'vice_presedent'"},
#             status=400,
#         )
    
#     # ✅ Vérifier si l'utilisateur a déjà une activité affectée
#     existing_activite_id = user_data.get('activite_id')
#     if existing_activite_id:
#         # Récupérer le nom de l'activité existante pour un message plus clair
#         existing_activite_nom = "Inconnue"
#         sc_existing, existing_activite = _call_juridique('get', f'/juridique/activites/{existing_activite_id}/', token)
#         if sc_existing == 200:
#             existing_activite_nom = existing_activite.get('data', {}).get('nom', 'Inconnue')
        
#         return Response(
#             {"status": "error", "code": "ALREADY_ASSIGNED",
#              "message": f"L'utilisateur a déjà une activité affectée.",
#              "data": {
#                  "user_id": user_id,
#                  "user_name": user_data.get('nom_complet'),
#                  "existing_activite_id": existing_activite_id,
#                  "existing_activite_nom": existing_activite_nom,
#                  "suggestion": "Utilisez PUT /affectation/reassign-activite/ pour changer d'activité"
#              }},
#             status=400,
#         )
    
#     # ── Étape 2 : Récupérer l'activité depuis le service Juridique ──
#     sc_act, activite_data = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
    
#     if sc_act == 404:
#         return Response(
#             {"status": "error", "code": "ACTIVITE_NOT_FOUND",
#              "message": f"Activité {activite_id} non trouvée dans le service juridique."},
#             status=404,
#         )
#     if sc_act != 200:
#         return Response(
#             {"status": "error", "code": "JURIDIQUE_SERVICE_ERROR",
#              "message": f"Service juridique indisponible (status {sc_act})."},
#             status=503,
#         )
    
#     # Extraire les données de l'activité
#     activite_info = activite_data.get('data', {})
#     activite_nom = activite_info.get('nom') or activite_info.get('name', 'Unknown')
    
#     # ── Étape 3 : Mettre à jour l'activite_id de l'utilisateur dans Auth ──
#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={"activite_id": activite_id}
#     )
    
#     if sc_update != 200:
#         return Response(
#             {"status": "error", "code": "UPDATE_FAILED",
#              "message": "Impossible de mettre à jour l'activite_id de l'utilisateur.",
#              "detail": updated},
#             status=sc_update,
#         )
    
#     # ── Réponse finale ──
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success",
#         "code": "ACTIVITE_ASSIGNED",
#         "message": f"Activité '{activite_nom}' affectée à {nom_complet}.",
#         "data": {
#             "user_id": user_id,
#             "user_name": nom_complet,
#             "user_email": user_data.get('email'),
#             "user_role": user_data.get('role'),
#             "activite_id": activite_id,
#             "activite_nom": activite_nom,
#             "activite_details": activite_info,
#             "assigned_by": {
#                 "id": admin.id,
#                 "name": getattr(admin, 'nom_complet', str(admin)),
#                 "role": getattr(admin, 'role', 'admin')
#             },
#             "timestamp": datetime.now().isoformat()
#         }
#     }, status=200)

# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def reassign_activite_to_user(request):
#     """
#     PUT /affectation/reassign-activite/
#     Body: { "user_id": 2, "activite_id": "672a1b2c3d4e5f6789abcdef" }
    
#     Permet de changer l'activité d'un utilisateur même s'il en a déjà une.
#     (Force la réaffectation)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user
    
#     user_id = request.data.get('user_id')
#     activite_id = request.data.get('activite_id')
#     force = request.data.get('force', True)  # Par défaut True pour PUT
    
#     # ── Validation ──
#     if not user_id:
#         return Response(
#             {"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."},
#             status=400,
#         )
#     if not activite_id:
#         return Response(
#             {"status": "error", "code": "MISSING_ACTIVITE_ID", "message": "activite_id est obligatoire."},
#             status=400,
#         )
    
#     # ── Étape 1 : Récupérer l'utilisateur depuis Auth ──
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
#     if sc != 200:
#         return Response(
#             {"status": "error", "code": "USER_NOT_FOUND",
#              "message": f"Utilisateur {user_id} introuvable."},
#             status=404,
#         )
    
#     user_data = user_response.get('user', {})
    
#     # Vérifier que l'utilisateur a le bon rôle
#     if user_data.get('role') != 'vice_presedent':
#         return Response(
#             {"status": "error", "code": "INVALID_ROLE",
#              "message": f"L'utilisateur a le rôle '{user_data.get('role')}', doit être 'vice_presedent'"},
#             status=400,
#         )
    
#     # Récupérer l'ancienne activité (si existe)
#     old_activite_id = user_data.get('activite_id')
#     old_activite_nom = None
#     if old_activite_id:
#         sc_old, old_activite = _call_juridique('get', f'/juridique/activites/{old_activite_id}/', token)
#         if sc_old == 200:
#             old_activite_nom = old_activite.get('data', {}).get('nom', 'Inconnue')
    
#     # ── Étape 2 : Récupérer la nouvelle activité ──
#     sc_act, activite_data = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
    
#     if sc_act == 404:
#         return Response(
#             {"status": "error", "code": "ACTIVITE_NOT_FOUND",
#              "message": f"Activité {activite_id} non trouvée dans le service juridique."},
#             status=404,
#         )
#     if sc_act != 200:
#         return Response(
#             {"status": "error", "code": "JURIDIQUE_SERVICE_ERROR",
#              "message": f"Service juridique indisponible (status {sc_act})."},
#             status=503,
#         )
    
#     activite_info = activite_data.get('data', {})
#     activite_nom = activite_info.get('nom') or activite_info.get('name', 'Unknown')
    
#     # ── Étape 3 : Mettre à jour ──
#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={"activite_id": activite_id}
#     )
    
#     if sc_update != 200:
#         return Response(
#             {"status": "error", "code": "UPDATE_FAILED",
#              "message": "Impossible de mettre à jour l'activite_id de l'utilisateur.",
#              "detail": updated},
#             status=sc_update,
#         )
    
#     # ── Réponse ──
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     response_data = {
#         "status": "success",
#         "code": "ACTIVITE_REASSIGNED",
#         "message": f"Activité changée de '{old_activite_nom or 'aucune'}' vers '{activite_nom}' pour {nom_complet}.",
#         "data": {
#             "user_id": user_id,
#             "user_name": nom_complet,
#             "user_email": user_data.get('email'),
#             "user_role": user_data.get('role'),
#             "previous_activite_id": old_activite_id,
#             "previous_activite_nom": old_activite_nom,
#             "new_activite_id": activite_id,
#             "new_activite_nom": activite_nom,
#             "new_activite_details": activite_info,
#             "assigned_by": {
#                 "id": admin.id,
#                 "name": getattr(admin, 'nom_complet', str(admin)),
#                 "role": getattr(admin, 'role', 'admin')
#             },
#             "timestamp": datetime.now().isoformat()
#         }
#     }
    
#     return Response(response_data, status=200)


# # ==========================
# # DÉSAFFECTER UNE ACTIVITÉ
# # ==========================

# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def remove_activite_from_user(request, user_id):
#     """
#     DELETE /affectation/users/<user_id>/remove-activite/
    
#     Supprime l'affectation d'activité d'un utilisateur
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user
    
#     # ── Récupérer l'utilisateur ──
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
#     if sc != 200:
#         return Response(
#             {"status": "error", "code": "USER_NOT_FOUND",
#              "message": f"Utilisateur {user_id} introuvable."},
#             status=404,
#         )
    
#     user_data = user_response.get('user', {})
    
#     # Vérifier s'il a une activité
#     current_activite_id = user_data.get('activite_id')
#     if not current_activite_id:
#         return Response(
#             {"status": "error", "code": "NO_ACTIVITE_ASSIGNED",
#              "message": "Cet utilisateur n'a aucune activité affectée."},
#             status=400,
#         )
    
#     # Récupérer le nom de l'activité pour le message
#     activite_nom = "Inconnue"
#     sc_act, activite_data = _call_juridique('get', f'/juridique/activites/{current_activite_id}/', token)
#     if sc_act == 200:
#         activite_nom = activite_data.get('data', {}).get('nom', 'Inconnue')
    
#     # ── Supprimer l'activite_id ──
#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={"activite_id": None}
#     )
    
#     if sc_update != 200:
#         return Response(
#             {"status": "error", "code": "UPDATE_FAILED",
#              "message": "Impossible de supprimer l'activite_id.",
#              "detail": updated},
#             status=sc_update,
#         )
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success",
#         "code": "ACTIVITE_REMOVED",
#         "message": f"Activité '{activite_nom}' désaffectée de {nom_complet}.",
#         "data": {
#             "user_id": user_id,
#             "user_name": nom_complet,
#             "removed_activite_id": current_activite_id,
#             "removed_activite_nom": activite_nom,
#             "removed_by": {
#                 "id": admin.id,
#                 "name": getattr(admin, 'nom_complet', str(admin)),
#                 "role": getattr(admin, 'role', 'admin')
#             },
#             "timestamp": datetime.now().isoformat()
#         }
#     }, status=200)



# # ==========================
# # 1. LISTER LES DIRECTEURS D'ACTIVITÉ SANS ACTIVITÉ AFFECTÉE
# # ==========================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_activite(request):
#     """
#     GET /affectation/users/directeurs-activite/
    
#     Liste tous les directeurs d'activité SANS activité affectée
#     (utilisateurs avec rôle 'vice_presedent' et activite_id = null)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     # Récupérer tous les utilisateurs
#     sc, users_response = _call_auth('get', '/auth/users/', token)
    
#     if sc != 200:
#         return Response(
#             {"status": "error", "code": "AUTH_SERVICE_ERROR",
#              "message": "Impossible de récupérer la liste des utilisateurs"},
#             status=503,
#         )
    
#     users = users_response.get('users', [])
    
#     # Filtrer: seulement directeurs d'activité SANS activité affectée
#     directeurs_sans_activite = [
#         u for u in users 
#         if u.get('role') == 'vice_presedent' and not u.get('activite_id')
#     ]
    
#     # Formatage de la réponse
#     data = []
#     for directeur in directeurs_sans_activite:
#         data.append({
#             "id": directeur.get('id'),
#             "email": directeur.get('email'),
#             "nom": directeur.get('nom'),
#             "prenom": directeur.get('prenom'),
#             "nom_complet": directeur.get('nom_complet'),
#             "role": directeur.get('role'),
#             "role_display": directeur.get('role_display'),
#             "is_active": directeur.get('is_active'),
#             "matricule": directeur.get('matricule'),
#             "telephone": directeur.get('telephone'),
#             "photo_profil": directeur.get('photo_profil')
#         })
    
#     return Response({
#         "status": "success",
#         "code": "DIRECTEURS_SANS_ACTIVITE",
#         "message": f"{len(data)} directeur(s) d'activité sans activité affectée",
#         "data": {
#             "count": len(data),
#             "directeurs": data
#         },
#         "timestamp": datetime.now().isoformat()
#     }, status=200)


# # ==========================
# # 2. LISTER LES DIRECTEURS D'ACTIVITÉ AVEC ACTIVITÉ AFFECTÉE
# # ==========================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_activite_affectes(request):
#     """
#     GET /affectation/users/directeurs-activite/affectes/
    
#     Liste tous les directeurs d'activité AVEC activité affectée
#     (utilisateurs avec rôle 'vice_presedent' et activite_id non null)
#     Inclut les détails de l'activité depuis le service juridique
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     # Récupérer tous les utilisateurs
#     sc, users_response = _call_auth('get', '/auth/users/', token)
    
#     if sc != 200:
#         return Response(
#             {"status": "error", "code": "AUTH_SERVICE_ERROR",
#              "message": "Impossible de récupérer la liste des utilisateurs"},
#             status=503,
#         )
    
#     users = users_response.get('users', [])
    
#     # Filtrer: seulement directeurs d'activité AVEC activité affectée
#     directeurs_avec_activite = [
#         u for u in users 
#         if u.get('role') == 'vice_presedent' and u.get('activite_id')
#     ]
    
#     # Récupérer les détails des activités pour chaque directeur
#     data = []
#     for directeur in directeurs_avec_activite:
#         activite_id = directeur.get('activite_id')
#         activite_data = None
        
#         # Récupérer l'activité depuis le service juridique
#         if activite_id:
#             sc_act, activite_response = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
#             if sc_act == 200:
#                 activite_data = activite_response.get('data', {})
        
#         data.append({
#             "id": directeur.get('id'),
#             "email": directeur.get('email'),
#             "nom": directeur.get('nom'),
#             "prenom": directeur.get('prenom'),
#             "nom_complet": directeur.get('nom_complet'),
#             "role": directeur.get('role'),
#             "role_display": directeur.get('role_display'),
#             "is_active": directeur.get('is_active'),
#             "matricule": directeur.get('matricule'),
#             "telephone": directeur.get('telephone'),
#             "photo_profil": directeur.get('photo_profil'),
#             "activite_id": activite_id,
#             "activite": activite_data
#         })
    
#     # Statistiques
#     total_avec_activite = len(data)
    
#     return Response({
#         "status": "success",
#         "code": "DIRECTEURS_AVEC_ACTIVITE",
#         "message": f"{total_avec_activite} directeur(s) d'activité avec activité affectée",
#         "data": {
#             "count": total_avec_activite,
#             "directeurs": data
#         },
#         "timestamp": datetime.now().isoformat()
#     }, status=200)
# # ==========================
# # 3. LISTER TOUS LES DIRECTEURS D'ACTIVITÉ (avec et sans activité)
# # ==========================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_all_directeurs_activite(request):
#     """
#     GET /affectation/users/directeurs-activite/all/
    
#     Liste TOUS les directeurs d'activité (avec ET sans activité affectée)
#     Inclut les détails de l'activité si présente
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     # Paramètres optionnels
#     show_inactive = request.query_params.get('show_inactive', '').lower() == 'true'
    
#     # Récupérer tous les utilisateurs
#     sc, users_response = _call_auth('get', '/auth/users/', token)
    
#     if sc != 200:
#         return Response(
#             {"status": "error", "code": "AUTH_SERVICE_ERROR",
#              "message": "Impossible de récupérer la liste des utilisateurs"},
#             status=503,
#         )
    
#     users = users_response.get('users', [])
    
#     # Filtrer: tous les directeurs d'activité
#     directeurs = [
#         u for u in users 
#         if u.get('role') == 'vice_presedent'
#     ]
    
#     # Filtrer les inactifs si demandé
#     if not show_inactive:
#         directeurs = [d for d in directeurs if d.get('is_active', True)]
    
#     # Récupérer les détails des activités pour chaque directeur
#     data = []
#     for directeur in directeurs:
#         activite_id = directeur.get('activite_id')
#         activite_data = None
        
#         # Récupérer l'activité depuis le service juridique si elle existe
#         if activite_id:
#             sc_act, activite_response = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
#             if sc_act == 200:
#                 activite_data = activite_response.get('data', {})
        
#         data.append({
#             "id": directeur.get('id'),
#             "email": directeur.get('email'),
#             "nom": directeur.get('nom'),
#             "prenom": directeur.get('prenom'),
#             "nom_complet": directeur.get('nom_complet'),
#             "role": directeur.get('role'),
#             "role_display": directeur.get('role_display'),
#             "is_active": directeur.get('is_active'),
#             "matricule": directeur.get('matricule'),
#             "telephone": directeur.get('telephone'),
#             "photo_profil": directeur.get('photo_profil'),
#             "activite_id": activite_id,
#             "activite": activite_data,
#             "has_activite": activite_id is not None
#         })
    
#     # Statistiques
#     total = len(data)
#     avec_activite = len([d for d in data if d.get('has_activite')])
#     sans_activite = total - avec_activite
#     actifs = len([d for d in data if d.get('is_active')])
#     inactifs = total - actifs
    
#     return Response({
#         "status": "success",
#         "code": "ALL_DIRECTEURS_ACTIVITE",
#         "message": f"Total: {total} directeur(s) d'activité",
#         "data": {
#             "count": total,
#             "statistics": {
#                 "with_activite": avec_activite,
#                 "without_activite": sans_activite,
#                 "active": actifs,
#                 "inactive": inactifs
#             },
#             "directeurs": data
#         },
#         "timestamp": datetime.now().isoformat()
#     }, status=200)










# ####################### Direction ########################
# # ==========================
# # DIRECTIONS - Assignation
# # ==========================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def assign_direction_to_user(request):
#     """
#     PATCH /affectation/assign-direction/
#     Body: { "user_id": 2, "direction_id": "672a1b2c3d4e5f6789abcdef" }
    
#     Affecte une direction à un utilisateur (directeur_direction)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user
    
#     user_id = request.data.get('user_id')
#     direction_id = request.data.get('direction_id')
    
#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
#     if not direction_id:
#         return Response({"status": "error", "code": "MISSING_DIRECTION_ID", "message": "direction_id est obligatoire."}, status=400)
    
#     # Récupérer l'utilisateur
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)
    
#     user_data = user_response.get('user', {})
    
#     # Vérifier le rôle
#     if user_data.get('role') != 'directeur_direction':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": f"L'utilisateur doit être 'directeur_direction' (actuel: {user_data.get('role')})"}, status=400)
    
#     # Vérifier si déjà affecté
#     existing_direction_id = user_data.get('direction_id')
#     if existing_direction_id:
#         existing_direction_nom = "Inconnue"
#         sc_existing, existing_direction = _call_juridique('get', f'/juridique/directions/{existing_direction_id}/', token)
#         if sc_existing == 200:
#             existing_direction_nom = existing_direction.get('data', {}).get('nom', 'Inconnue')
        
#         return Response({"status": "error", "code": "ALREADY_ASSIGNED", "message": "L'utilisateur a déjà une direction affectée.", "data": {"existing_direction_id": existing_direction_id, "existing_direction_nom": existing_direction_nom}}, status=400)
    
#     # Récupérer la direction
#     sc_dir, direction_response = _call_juridique('get', f'/juridique/directions/{direction_id}/', token)
#     if sc_dir == 404:
#         return Response({"status": "error", "code": "DIRECTION_NOT_FOUND", "message": f"Direction {direction_id} non trouvée."}, status=404)
#     if sc_dir != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible"}, status=503)
    
#     direction_info = direction_response.get('data', {})
#     direction_nom = direction_info.get('nom', 'Unknown')
    
#     # Mettre à jour
#     sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": direction_id})
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour"}, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", "code": "DIRECTION_ASSIGNED",
#         "message": f"Direction '{direction_nom}' affectée à {nom_complet}.",
#         "data": {"user_id": user_id, "user_name": nom_complet, "direction_id": direction_id, "direction_nom": direction_nom, "direction_details": direction_info}
#     }, status=200)


# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def reassign_direction_to_user(request):
#     """
#     PUT /affectation/reassign-direction/
#     Body: { "user_id": 2, "direction_id": "672a1b2c3d4e5f6789abcdef" }
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user
    
#     user_id = request.data.get('user_id')
#     direction_id = request.data.get('direction_id')
    
#     if not user_id or not direction_id:
#         return Response({"status": "error", "message": "user_id et direction_id requis"}, status=400)
    
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
#     user_data = user_response.get('user', {})
    
#     if user_data.get('role') != 'directeur_direction':
#         return Response({"status": "error", "message": "L'utilisateur doit être 'directeur_direction'"}, status=400)
    
#     old_direction_id = user_data.get('direction_id')
#     old_direction_nom = None
#     if old_direction_id:
#         sc_old, old_direction = _call_juridique('get', f'/juridique/directions/{old_direction_id}/', token)
#         if sc_old == 200:
#             old_direction_nom = old_direction.get('data', {}).get('nom', 'Inconnue')
    
#     sc_dir, direction_response = _call_juridique('get', f'/juridique/directions/{direction_id}/', token)
#     if sc_dir != 200:
#         return Response({"status": "error", "message": "Direction non trouvée"}, status=404)
    
#     direction_info = direction_response.get('data', {})
#     direction_nom = direction_info.get('nom', 'Unknown')
    
#     sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": direction_id})
#     if sc_update != 200:
#         return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", "code": "DIRECTION_REASSIGNED",
#         "message": f"Direction changée de '{old_direction_nom or 'aucune'}' vers '{direction_nom}'",
#         "data": {"user_id": user_id, "user_name": nom_complet, "previous_direction_id": old_direction_id, "previous_direction_nom": old_direction_nom, "new_direction_id": direction_id, "new_direction_nom": direction_nom}
#     }, status=200)


# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def remove_direction_from_user(request, user_id):
#     """DELETE /affectation/users/<user_id>/remove-direction/"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
#     user_data = user_response.get('user', {})
#     current_direction_id = user_data.get('direction_id')
    
#     if not current_direction_id:
#         return Response({"status": "error", "code": "NO_DIRECTION_ASSIGNED", "message": "Aucune direction affectée"}, status=400)
    
#     direction_nom = "Inconnue"
#     sc_dir, direction_response = _call_juridique('get', f'/juridique/directions/{current_direction_id}/', token)
#     if sc_dir == 200:
#         direction_nom = direction_response.get('data', {}).get('nom', 'Inconnue')
    
#     sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": None})
#     if sc_update != 200:
#         return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", "code": "DIRECTION_REMOVED",
#         "message": f"Direction '{direction_nom}' désaffectée de {nom_complet}",
#         "data": {"user_id": user_id, "user_name": nom_complet, "removed_direction_id": current_direction_id, "removed_direction_nom": direction_nom}
#     }, status=200)


# # ==========================
# # DIRECTIONS - Listes
# # ==========================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_direction(request):
#     """GET /affectation/users/directeurs-direction/ - Directeurs SANS direction"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
#     directeurs_sans = [u for u in users if u.get('role') == 'directeur_direction' and not u.get('direction_id')]
    
#     data = [{"id": d.get('id'), "email": d.get('email'), "nom": d.get('nom'), "prenom": d.get('prenom'), "nom_complet": d.get('nom_complet'), "is_active": d.get('is_active')} for d in directeurs_sans]
    
#     return Response({"status": "success", "code": "DIRECTEURS_DIRECTION_SANS", "message": f"{len(data)} directeur(s) de direction sans affectation", "data": {"count": len(data), "directeurs": data}}, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_direction_affectes(request):
#     """GET /affectation/users/directeurs-direction/affectes/ - Directeurs AVEC direction"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
#     directeurs_avec = [u for u in users if u.get('role') == 'directeur_direction' and u.get('direction_id')]
    
#     data = []
#     for d in directeurs_avec:
#         direction_data = None
#         if d.get('direction_id'):
#             sc_dir, dir_response = _call_juridique('get', f'/juridique/directions/{d["direction_id"]}/', token)
#             if sc_dir == 200:
#                 direction_data = dir_response.get('data', {})
        
#         data.append({"id": d.get('id'), "nom_complet": d.get('nom_complet'), "direction_id": d.get('direction_id'), "direction": direction_data})
    
#     return Response({"status": "success", "code": "DIRECTEURS_DIRECTION_AVEC", "data": {"count": len(data), "directeurs": data}}, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_all_directeurs_direction(request):
#     """GET /affectation/users/directeurs-direction/all/ - TOUS les directeurs de direction"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
#     directeurs = [u for u in users if u.get('role') == 'directeur_direction']
    
#     data = []
#     for d in directeurs:
#         direction_data = None
#         if d.get('direction_id'):
#             sc_dir, dir_response = _call_juridique('get', f'/juridique/directions/{d["direction_id"]}/', token)
#             if sc_dir == 200:
#                 direction_data = dir_response.get('data', {})
        
#         data.append({"id": d.get('id'), "nom_complet": d.get('nom_complet'), "is_active": d.get('is_active'), "direction_id": d.get('direction_id'), "direction": direction_data, "has_direction": d.get('direction_id') is not None})
    
#     avec = len([x for x in data if x.get('has_direction')])
#     sans = len(data) - avec
    
#     return Response({"status": "success", "code": "ALL_DIRECTEURS_DIRECTION", "data": {"count": len(data), "statistics": {"with_direction": avec, "without_direction": sans}, "directeurs": data}}, status=200)

# # ──────────────────────────────────────────────
# # VIEW : GET USER (via Gateway ou Eureka)
# # ──────────────────────────────────────────────

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def get_user(request, user_id):
#     """
#     GET /affectation/user/<user_id>/
#     Récupère les informations d'un utilisateur (admin seulement)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     force_gateway = request.query_params.get('force_gateway', '').lower() == 'true'
    
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token, use_gateway=force_gateway)
    
#     if sc != 200:
#         return Response(user_response, status=sc)
    
#     return Response({
#         "status": "success",
#         "data": user_response.get('user', user_response),
#         "metadata": {
#             "source": "gateway" if force_gateway else "eureka"
#         }
#     })






# # ==========================
# # DÉPARTEMENTS - Assignation (avec vérification direction automatique)
# # ==========================

# # affectation/views.py - Code complet pour les départements

# # ==========================
# # HELPER - Appel spécifique pour département
# # ==========================

# def _call_auth_update_departement(user_id: int, departement_id: str, direction_id: str, token: str):
#     """
#     Appel spécifique pour mettre à jour le département et la direction d'un utilisateur
#     Utilise l'endpoint dédié pour directeur_direction
#     """
#     base_url = get_auth_base_url()
#     path = f'/auth/users/{user_id}/update-departement/'
#     url = f"{base_url}{path}"
#     headers = {'Authorization': f'Bearer {token}'}
    
#     update_data = {
#         "departement_id": departement_id,
#         "direction_id": direction_id
#     }
    
#     print(f'[AFFECTATION] → PATCH {url}')
#     print(f'[AFFECTATION] → Data: {update_data}')
    
#     try:
#         resp = requests.patch(
#             url,
#             headers=headers,
#             json=update_data,
#             timeout=5
#         )
#         print(f'[AFFECTATION] ← {resp.status_code}')
        
#         if resp.status_code == 200:
#             return resp.status_code, resp.json()
#         return resp.status_code, {"error": resp.text}
        
#     except requests.RequestException as e:
#         print(f'[AFFECTATION] ✗ Erreur: {e}')
#         return 503, {"status": "error", "message": str(e)}


# # ==========================
# # DÉPARTEMENTS - Assignation
# # ==========================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def assign_departement_to_user(request):
#     """
#     PATCH /affectation/assign-departement/
#     Body: { "user_id": 2, "departement_id": "672a1b2c3d4e5f6789abcdef" }
    
#     Affecte un département à un responsable_departement
#     Met à jour automatiquement direction_id et departement_id
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
    
#     user_id = request.data.get('user_id')
#     departement_id = request.data.get('departement_id')
    
#     # ── Validation ──
#     if not user_id:
#         return Response({
#             "status": "error", "code": "MISSING_USER_ID",
#             "message": "user_id est obligatoire."
#         }, status=400)
    
#     if not departement_id:
#         return Response({
#             "status": "error", "code": "MISSING_DEPARTEMENT_ID",
#             "message": "departement_id est obligatoire."
#         }, status=400)
    
#     # Vérifier que le directeur a une direction_id
#     directeur_direction_id = getattr(directeur, 'direction_id', None)
#     if not directeur_direction_id:
#         return Response({
#             "status": "error", "code": "DIRECTEUR_NO_DIRECTION",
#             "message": "Vous n'avez pas de direction associée."
#         }, status=403)
    
#     # ── Étape 1 : Récupérer l'utilisateur cible ──
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    
#     if sc != 200:
#         return Response({
#             "status": "error", "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur {user_id} introuvable."
#         }, status=404)
    
#     user_data = user_response.get('user', {})
    
#     # Vérifier le rôle
#     if user_data.get('role') != 'responsable_departement':
#         return Response({
#             "status": "error", "code": "INVALID_ROLE",
#             "message": f"L'utilisateur doit être 'responsable_departement' (actuel: {user_data.get('role')})"
#         }, status=400)
    
#     # Vérifier si déjà affecté
#     existing_departement_id = user_data.get('departement_id')
#     if existing_departement_id:
#         existing_nom = "Inconnu"
#         sc_exist, exist_response = _call_juridique('get', f'/juridique/departements/{existing_departement_id}/', token)
#         if sc_exist == 200:
#             existing_nom = exist_response.get('data', {}).get('nom', 'Inconnu')
        
#         return Response({
#             "status": "error", "code": "ALREADY_ASSIGNED",
#             "message": f"L'utilisateur a déjà un département: '{existing_nom}'",
#             "suggestion": "Utilisez PUT /affectation/reassign-departement/ pour changer"
#         }, status=400)
    
#     # ── Étape 2 : Récupérer le département ──
#     sc_dep, departement_response = _call_juridique('get', f'/juridique/departements/{departement_id}/', token)
    
#     if sc_dep == 404:
#         return Response({
#             "status": "error", "code": "DEPARTEMENT_NOT_FOUND",
#             "message": f"Département {departement_id} non trouvé."
#         }, status=404)
    
#     if sc_dep != 200:
#         return Response({
#             "status": "error", "code": "JURIDIQUE_SERVICE_ERROR",
#             "message": "Service juridique indisponible"
#         }, status=503)
    
#     departement_info = departement_response.get('data', {})
#     departement_nom = departement_info.get('nom', 'Unknown')
    
#     # Vérifier que le département appartient à la direction du directeur
#     departement_direction_id = departement_info.get('direction', {}).get('_id') or departement_info.get('direction')
    
#     if str(directeur_direction_id) != str(departement_direction_id):
#         direction_nom = "Inconnue"
#         sc_dir, dir_response = _call_juridique('get', f'/juridique/directions/{directeur_direction_id}/', token)
#         if sc_dir == 200:
#             direction_nom = dir_response.get('data', {}).get('nom', 'Inconnue')
        
#         return Response({
#             "status": "error", "code": "DEPARTEMENT_NOT_IN_DIRECTION",
#             "message": f"Ce département n'appartient pas à votre direction '{direction_nom}'."
#         }, status=403)
    
#     # ── Étape 3 : Mettre à jour l'utilisateur ──
#     sc_update, updated = _call_auth_update_departement(
#         user_id=user_id,
#         departement_id=departement_id,
#         direction_id=directeur_direction_id,
#         token=token
#     )
    
#     if sc_update != 200:
#         return Response({
#             "status": "error", "code": "UPDATE_FAILED",
#             "message": "Impossible de mettre à jour l'utilisateur.",
#             "detail": updated
#         }, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", "code": "DEPARTEMENT_ASSIGNED",
#         "message": f"Département '{departement_nom}' affecté à {nom_complet}.",
#         "data": {
#             "user_id": int(user_id),
#             "user_name": nom_complet,
#             "user_email": user_data.get('email'),
#             "user_role": user_data.get('role'),
#             "direction_id": directeur_direction_id,
#             "departement_id": departement_id,
#             "departement_nom": departement_nom,
#             "departement_details": departement_info,
#             "assigned_by": {
#                 "id": directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#                 "direction_id": directeur_direction_id
#             },
#             "timestamp": datetime.now().isoformat()
#         }
#     }, status=200)


# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def reassign_departement_to_user(request):
#     """
#     PUT /affectation/reassign-departement/
#     Body: { "user_id": 2, "departement_id": "672a1b2c3d4e5f6789abcdef" }
    
#     Réaffecte un département (change même si déjà affecté)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
    
#     user_id = request.data.get('user_id')
#     departement_id = request.data.get('departement_id')
    
#     if not user_id or not departement_id:
#         return Response({
#             "status": "error", "message": "user_id et departement_id requis"
#         }, status=400)
    
#     directeur_direction_id = getattr(directeur, 'direction_id', None)
#     if not directeur_direction_id:
#         return Response({
#             "status": "error", "code": "DIRECTEUR_NO_DIRECTION",
#             "message": "Vous n'avez pas de direction associée."
#         }, status=403)
    
#     # Récupérer l'utilisateur
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
#     user_data = user_response.get('user', {})
    
#     if user_data.get('role') != 'responsable_departement':
#         return Response({
#             "status": "error", "message": "L'utilisateur doit être 'responsable_departement'"
#         }, status=400)
    
#     # Récupérer le nouveau département
#     sc_dep, departement_response = _call_juridique('get', f'/juridique/departements/{departement_id}/', token)
#     if sc_dep != 200:
#         return Response({"status": "error", "message": "Département non trouvé"}, status=404)
    
#     departement_info = departement_response.get('data', {})
#     departement_nom = departement_info.get('nom', 'Unknown')
    
#     # Vérifier que le département appartient à la direction
#     departement_direction_id = departement_info.get('direction', {}).get('_id') or departement_info.get('direction')
#     if str(directeur_direction_id) != str(departement_direction_id):
#         return Response({
#             "status": "error", "code": "DEPARTEMENT_NOT_IN_DIRECTION",
#             "message": "Ce département n'appartient pas à votre direction."
#         }, status=403)
    
#     # Ancien département
#     old_departement_id = user_data.get('departement_id')
#     old_departement_nom = "Inconnu"
#     if old_departement_id:
#         sc_old, old_response = _call_juridique('get', f'/juridique/departements/{old_departement_id}/', token)
#         if sc_old == 200:
#             old_departement_nom = old_response.get('data', {}).get('nom', 'Inconnu')
    
#     # Mettre à jour
#     sc_update, _ = _call_auth_update_departement(
#         user_id=user_id,
#         departement_id=departement_id,
#         direction_id=directeur_direction_id,
#         token=token
#     )
    
#     if sc_update != 200:
#         return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", "code": "DEPARTEMENT_REASSIGNED",
#         "message": f"Département changé de '{old_departement_nom}' vers '{departement_nom}'",
#         "data": {
#             "user_id": user_id, 
#             "user_name": nom_complet,
#             "previous_departement_id": old_departement_id, 
#             "previous_departement_nom": old_departement_nom,
#             "new_departement_id": departement_id, 
#             "new_departement_nom": departement_nom
#         }
#     }, status=200)


# # affectation/views.py

# # affectation/views.py - Modifier remove_departement_from_user

# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def remove_departement_from_user(request, user_id):
#     """
#     DELETE /affectation/users/<user_id>/remove-departement/
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
    
#     directeur_direction_id = getattr(directeur, 'direction_id', None)
    
#     # Récupérer l'utilisateur
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
#     user_data = user_response.get('user', {})
#     current_departement_id = user_data.get('departement_id')
#     current_direction_id = user_data.get('direction_id')
    
#     if not current_departement_id:
#         return Response({"status": "error", "message": "Aucun département affecté"}, status=400)
    
#     # Récupérer le nom du département
#     departement_nom = "Inconnu"
#     sc_dep, departement_response = _call_juridique('get', f'/juridique/departements/{current_departement_id}/', token)
#     if sc_dep == 200:
#         departement_nom = departement_response.get('data', {}).get('nom', 'Inconnu')
    
#     # Supprimer les affectations
#     sc_update, updated = _call_auth_update_departement(
#         user_id=user_id,
#         departement_id=None,
#         direction_id=None,
#         token=token
#     )
    
#     if sc_update != 200:
#         return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)
    
#     # ✅ Option 2: Invalider le refresh token pour forcer la reconnexion
#     try:
#         # Appeler un endpoint pour blacklister les tokens de l'utilisateur
#         _call_auth('post', f'/auth/users/{user_id}/logout-all/', token)
#     except:
#         pass  # Ignorer si l'endpoint n'existe pas
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", 
#         "code": "DEPARTEMENT_REMOVED",
#         "message": f"Département '{departement_nom}' désaffecté de {nom_complet}",
#         "data": {
#             "user_id": user_id,
#             "user_name": nom_complet,
#             "removed_departement_id": current_departement_id,
#             "removed_departement_nom": departement_nom,
#             "new_departement_id": None,
#             "new_direction_id": None,
#             "requires_relogin": True,  # ✅ Indiquer que l'utilisateur doit se reconnecter
#             "message_for_user": "Veuillez vous reconnecter pour que les changements prennent effet",
#             "removed_by": {
#                 "id": directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role
#             },
#             "timestamp": datetime.now().isoformat()
#         }
#     }, status=200)

# # ==========================
# # DÉPARTEMENTS - Listes
# # ==========================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def api_list_responsables_departement(request):
#     """
#     GET /affectation/users/responsables-departement/
#     Liste les responsables SANS département (dans la direction du directeur)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
    
#     directeur_direction_id = getattr(directeur, 'direction_id', None)
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
    
#     # Filtrer responsables département
#     responsables = [u for u in users if u.get('role') == 'responsable_departement']
    
#     # Filtrer ceux sans direction_id (disponibles pour affectation dans n'importe quelle direction)
#     responsables_disponibles = [r for r in responsables if r.get('direction_id') is None]
    
#     # Filtrer ceux sans département
#     responsables_sans = [r for r in responsables_disponibles if not r.get('departement_id')]
    
#     data = [{
#         "id": r.get('id'), 
#         "email": r.get('email'),
#         "nom": r.get('nom'), 
#         "prenom": r.get('prenom'),
#         "nom_complet": r.get('nom_complet'), 
#         "is_active": r.get('is_active')
#     } for r in responsables_sans]
    
#     return Response({
#         "status": "success", 
#         "code": "RESPONSABLES_SANS_DEPARTEMENT",
#         "data": {"count": len(data), "responsables": data}
#     }, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def api_list_responsables_departement_affectes(request):
#     """
#     GET /affectation/users/responsables-departement/affectes/
#     Liste les responsables AVEC département (de la direction du directeur)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
    
#     directeur_direction_id = getattr(directeur, 'direction_id', None)
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
    
#     responsables = [u for u in users if u.get('role') == 'responsable_departement']
    
#     # Filtrer ceux de la direction du directeur
#     if directeur_direction_id:
#         responsables = [r for r in responsables if r.get('direction_id') == directeur_direction_id]
    
#     responsables_avec = [r for r in responsables if r.get('departement_id')]
    
#     data = []
#     for r in responsables_avec:
#         departement_data = None
#         if r.get('departement_id'):
#             sc_dep, dep_response = _call_juridique('get', f'/juridique/departements/{r["departement_id"]}/', token)
#             if sc_dep == 200:
#                 departement_data = dep_response.get('data', {})
        
#         data.append({
#             "id": r.get('id'), 
#             "nom_complet": r.get('nom_complet'),
#             "direction_id": r.get('direction_id'),
#             "departement_id": r.get('departement_id'), 
#             "departement": departement_data
#         })
    
#     return Response({
#         "status": "success", 
#         "code": "RESPONSABLES_AVEC_DEPARTEMENT",
#         "data": {"count": len(data), "responsables": data}
#     }, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def api_list_all_responsables_departement(request):
#     """
#     GET /affectation/users/responsables-departement/all/
#     Liste TOUS les responsables département (de la direction du directeur)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
    
#     directeur_direction_id = getattr(directeur, 'direction_id', None)
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
    
#     responsables = [u for u in users if u.get('role') == 'responsable_departement']
    
#     # Filtrer ceux de la direction du directeur ou sans direction
#     if directeur_direction_id:
#         responsables = [r for r in responsables if r.get('direction_id') == directeur_direction_id or r.get('direction_id') is None]
    
#     data = []
#     for r in responsables:
#         departement_data = None
#         if r.get('departement_id'):
#             sc_dep, dep_response = _call_juridique('get', f'/juridique/departements/{r["departement_id"]}/', token)
#             if sc_dep == 200:
#                 departement_data = dep_response.get('data', {})
        
#         data.append({
#             "id": r.get('id'), 
#             "nom_complet": r.get('nom_complet'),
#             "email": r.get('email'),
#             "is_active": r.get('is_active'), 
#             "direction_id": r.get('direction_id'),
#             "departement_id": r.get('departement_id'), 
#             "departement": departement_data,
#             "has_departement": r.get('departement_id') is not None
#         })
    
#     avec = len([x for x in data if x.get('has_departement')])
#     sans = len(data) - avec
    
#     return Response({
#         "status": "success", 
#         "code": "ALL_RESPONSABLES_DEPARTEMENT",
#         "data": {
#             "count": len(data),
#             "statistics": {"with_departement": avec, "without_departement": sans},
#             "responsables": data
#         }
#     }, status=200)

# # ==========================
# # DIRECTION CENTRALE - Helpers spécifiques
# # ==========================

# def _call_auth_update_directeur_centrale(user_id: int, direction_centrale_id: str, token: str):
#     """
#     Met à jour la direction centrale d'un directeur centrale
#     """
#     base_url = get_auth_base_url()
#     path = f'/auth/users/{user_id}/update/'
#     url = f"{base_url}{path}"
#     headers = {'Authorization': f'Bearer {token}'}
    
#     update_data = {"direction_centrale_id": direction_centrale_id}
    
#     print(f'[AFFECTATION] → PATCH {url}')
#     print(f'[AFFECTATION] → Data: {update_data}')
    
#     try:
#         resp = requests.patch(
#             url,
#             headers=headers,
#             json=update_data,
#             timeout=5
#         )
#         print(f'[AFFECTATION] ← {resp.status_code}')
        
#         if resp.status_code == 200:
#             return resp.status_code, resp.json()
#         return resp.status_code, {"error": resp.text}
        
#     except requests.RequestException as e:
#         print(f'[AFFECTATION] ✗ Erreur: {e}')
#         return 503, {"status": "error", "message": str(e)}


# def _call_auth_clear_directeur_centrale(user_id: int, token: str):
#     """
#     Supprime l'affectation direction centrale d'un directeur centrale
#     """
#     base_url = get_auth_base_url()
#     path = f'/auth/users/{user_id}/update/'
#     url = f"{base_url}{path}"
#     headers = {'Authorization': f'Bearer {token}'}
    
#     update_data = {"direction_centrale_id": None}
    
#     try:
#         resp = requests.patch(
#             url,
#             headers=headers,
#             json=update_data,
#             timeout=5
#         )
        
#         if resp.status_code == 200:
#             return resp.status_code, resp.json()
#         return resp.status_code, {"error": resp.text}
        
#     except requests.RequestException as e:
#         return 503, {"status": "error", "message": str(e)}


# def _get_direction_centrale_details(direction_centrale_id: str, token: str) -> dict:
#     """
#     Récupère les détails d'une direction centrale depuis le service juridique
#     """
#     sc, response = _call_juridique(
#         'get', f'/juridique/directions-centrales/{direction_centrale_id}/', token
#     )
    
#     if sc == 200:
#         return response.get('data', {})
#     return {}


# def _get_direction_centrale_by_code(code: str, token: str) -> dict:
#     """
#     Récupère une direction centrale par son code
#     """
#     sc, response = _call_juridique(
#         'get', f'/juridique/directions-centrales/code/{code}/', token
#     )
    
#     if sc == 200:
#         return response.get('data', {})
#     return {}



# # ==========================
# # DIRECTION CENTRALE - Assignation
# # ==========================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def assign_direction_centrale_to_user(request):
#     """
#     PATCH /affectation/assign-direction-centrale/
#     Body: { "user_id": 2, "direction_centrale_id": "672a1b2c3d4e5f6789abcdef" }
    
#     Affecte une direction centrale à un utilisateur (directeur_centrale)
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user
    
#     user_id = request.data.get('user_id')
#     direction_centrale_id = request.data.get('direction_centrale_id')
    
#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
#     if not direction_centrale_id:
#         return Response({"status": "error", "code": "MISSING_DIRECTION_CENTRALE_ID", "message": "direction_centrale_id est obligatoire."}, status=400)
    
#     # Récupérer l'utilisateur
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)
    
#     user_data = user_response.get('user', {})
    
#     # Vérifier le rôle
#     if user_data.get('role') != 'directeur_centrale':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": f"L'utilisateur doit être 'directeur_centrale' (actuel: {user_data.get('role')})"}, status=400)
    
#     # Vérifier si déjà affecté
#     existing_direction_centrale_id = user_data.get('direction_centrale_id')
#     if existing_direction_centrale_id:
#         existing_nom = "Inconnue"
#         sc_existing, existing_direction_centrale = _call_juridique('get', f'/juridique/directions-centrales/{existing_direction_centrale_id}/', token)
#         if sc_existing == 200:
#             existing_nom = existing_direction_centrale.get('data', {}).get('nom', 'Inconnue')
        
#         return Response({
#             "status": "error", 
#             "code": "ALREADY_ASSIGNED", 
#             "message": "L'utilisateur a déjà une direction centrale affectée.", 
#             "data": {
#                 "existing_direction_centrale_id": existing_direction_centrale_id, 
#                 "existing_direction_centrale_nom": existing_nom
#             }
#         }, status=400)
    
#     # Récupérer la direction centrale
#     sc_dir, direction_centrale_response = _call_juridique('get', f'/juridique/directions-centrales/{direction_centrale_id}/', token)
#     if sc_dir == 404:
#         return Response({"status": "error", "code": "DIRECTION_CENTRALE_NOT_FOUND", "message": f"Direction centrale {direction_centrale_id} non trouvée."}, status=404)
#     if sc_dir != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible"}, status=503)
    
#     direction_centrale_info = direction_centrale_response.get('data', {})
#     direction_centrale_nom = direction_centrale_info.get('nom', 'Unknown')
    
#     # Mettre à jour
#     sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_centrale_id": direction_centrale_id})
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour"}, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", 
#         "code": "DIRECTION_CENTRALE_ASSIGNED",
#         "message": f"Direction centrale '{direction_centrale_nom}' affectée à {nom_complet}.",
#         "data": {
#             "user_id": user_id, 
#             "user_name": nom_complet, 
#             "direction_centrale_id": direction_centrale_id, 
#             "direction_centrale_nom": direction_centrale_nom, 
#             "direction_centrale_details": direction_centrale_info
#         }
#     }, status=200)


# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def reassign_direction_centrale_to_user(request):
#     """
#     PUT /affectation/reassign-direction-centrale/
#     Body: { "user_id": 2, "direction_centrale_id": "672a1b2c3d4e5f6789abcdef" }
#     """
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user
    
#     user_id = request.data.get('user_id')
#     direction_centrale_id = request.data.get('direction_centrale_id')
    
#     if not user_id or not direction_centrale_id:
#         return Response({"status": "error", "message": "user_id et direction_centrale_id requis"}, status=400)
    
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
#     user_data = user_response.get('user', {})
    
#     if user_data.get('role') != 'directeur_centrale':
#         return Response({"status": "error", "message": "L'utilisateur doit être 'directeur_centrale'"}, status=400)
    
#     old_direction_centrale_id = user_data.get('direction_centrale_id')
#     old_direction_centrale_nom = None
#     if old_direction_centrale_id:
#         sc_old, old_direction_centrale = _call_juridique('get', f'/juridique/directions-centrales/{old_direction_centrale_id}/', token)
#         if sc_old == 200:
#             old_direction_centrale_nom = old_direction_centrale.get('data', {}).get('nom', 'Inconnue')
    
#     sc_dir, direction_centrale_response = _call_juridique('get', f'/juridique/directions-centrales/{direction_centrale_id}/', token)
#     if sc_dir != 200:
#         return Response({"status": "error", "message": "Direction centrale non trouvée"}, status=404)
    
#     direction_centrale_info = direction_centrale_response.get('data', {})
#     direction_centrale_nom = direction_centrale_info.get('nom', 'Unknown')
    
#     sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_centrale_id": direction_centrale_id})
#     if sc_update != 200:
#         return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", 
#         "code": "DIRECTION_CENTRALE_REASSIGNED",
#         "message": f"Direction centrale changée de '{old_direction_centrale_nom or 'aucune'}' vers '{direction_centrale_nom}'",
#         "data": {
#             "user_id": user_id, 
#             "user_name": nom_complet, 
#             "previous_direction_centrale_id": old_direction_centrale_id, 
#             "previous_direction_centrale_nom": old_direction_centrale_nom, 
#             "new_direction_centrale_id": direction_centrale_id, 
#             "new_direction_centrale_nom": direction_centrale_nom
#         }
#     }, status=200)


# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def remove_direction_centrale_from_user(request, user_id):
#     """DELETE /affectation/users/<user_id>/remove-direction-centrale/"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)
    
#     user_data = user_response.get('user', {})
#     current_direction_centrale_id = user_data.get('direction_centrale_id')
    
#     if not current_direction_centrale_id:
#         return Response({"status": "error", "code": "NO_DIRECTION_CENTRALE_ASSIGNED", "message": "Aucune direction centrale affectée"}, status=400)
    
#     direction_centrale_nom = "Inconnue"
#     sc_dir, direction_centrale_response = _call_juridique('get', f'/juridique/directions-centrales/{current_direction_centrale_id}/', token)
#     if sc_dir == 200:
#         direction_centrale_nom = direction_centrale_response.get('data', {}).get('nom', 'Inconnue')
    
#     sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_centrale_id": None})
#     if sc_update != 200:
#         return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)
    
#     nom_complet = user_data.get('nom_complet', f"{user_data.get('prenom', '')} {user_data.get('nom', '')}").strip()
    
#     return Response({
#         "status": "success", 
#         "code": "DIRECTION_CENTRALE_REMOVED",
#         "message": f"Direction centrale '{direction_centrale_nom}' désaffectée de {nom_complet}",
#         "data": {
#             "user_id": user_id, 
#             "user_name": nom_complet, 
#             "removed_direction_centrale_id": current_direction_centrale_id, 
#             "removed_direction_centrale_nom": direction_centrale_nom
#         }
#     }, status=200)


# # ==========================
# # DIRECTION CENTRALE - Listes
# # ==========================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_centrale(request):
#     """GET /affectation/users/directeurs-centrale/ - Directeurs centrale SANS direction centrale"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
#     directeurs_sans = [u for u in users if u.get('role') == 'directeur_centrale' and not u.get('direction_centrale_id')]
    
#     data = [{
#         "id": d.get('id'), 
#         "email": d.get('email'), 
#         "nom": d.get('nom'), 
#         "prenom": d.get('prenom'), 
#         "nom_complet": d.get('nom_complet'), 
#         "is_active": d.get('is_active')
#     } for d in directeurs_sans]
    
#     return Response({
#         "status": "success", 
#         "code": "DIRECTEURS_CENTRALE_SANS", 
#         "message": f"{len(data)} directeur(s) centrale sans affectation", 
#         "data": {"count": len(data), "directeurs": data}
#     }, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_centrale_affectes(request):
#     """GET /affectation/users/directeurs-centrale/affectes/ - Directeurs centrale AVEC direction centrale"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
#     directeurs_avec = [u for u in users if u.get('role') == 'directeur_centrale' and u.get('direction_centrale_id')]
    
#     data = []
#     for d in directeurs_avec:
#         direction_centrale_data = None
#         if d.get('direction_centrale_id'):
#             try:
#                 sc_dir, dir_response = _call_juridique('get', f'/juridique/directions-centrales/{d["direction_centrale_id"]}/', token)
#                 if sc_dir == 200:
#                     # La réponse peut être dans 'data' ou directement l'objet
#                     direction_centrale_data = dir_response.get('data', dir_response)
#                 else:
#                     # Si l'endpoint n'existe pas, on met juste l'ID
#                     direction_centrale_data = {"_id": d["direction_centrale_id"], "nom": "Information non disponible"}
#             except Exception as e:
#                 direction_centrale_data = {"_id": d["direction_centrale_id"], "nom": "Erreur de récupération"}
        
#         data.append({
#             "id": d.get('id'), 
#             "nom_complet": d.get('nom_complet'),
#             "email": d.get('email'),
#             "is_active": d.get('is_active'),
#             "direction_centrale_id": d.get('direction_centrale_id'), 
#             "direction_centrale": direction_centrale_data
#         })
    
#     return Response({
#         "status": "success", 
#         "code": "DIRECTEURS_CENTRALE_AVEC", 
#         "message": f"{len(data)} directeur(s) centrale avec affectation",
#         "data": {"count": len(data), "directeurs": data}
#     }, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_all_directeurs_centrale(request):
#     """GET /affectation/users/directeurs-centrale/all/ - TOUS les directeurs centrale"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    
#     # Paramètre optionnel pour inclure les inactifs
#     show_inactive = request.query_params.get('show_inactive', '').lower() == 'true'
    
#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)
    
#     users = users_response.get('users', [])
#     directeurs = [u for u in users if u.get('role') == 'directeur_centrale']
    
#     # Filtrer les inactifs si demandé
#     if not show_inactive:
#         directeurs = [d for d in directeurs if d.get('is_active', True)]
    
#     data = []
#     for d in directeurs:
#         direction_centrale_data = None
#         if d.get('direction_centrale_id'):
#             try:
#                 sc_dir, dir_response = _call_juridique('get', f'/juridique/directions-centrales/{d["direction_centrale_id"]}/', token)
#                 if sc_dir == 200:
#                     direction_centrale_data = dir_response.get('data', dir_response)
#                 else:
#                     direction_centrale_data = {"_id": d["direction_centrale_id"], "nom": "Information non disponible"}
#             except Exception as e:
#                 direction_centrale_data = {"_id": d["direction_centrale_id"], "nom": "Erreur de récupération"}
        
#         data.append({
#             "id": d.get('id'), 
#             "email": d.get('email'),
#             "nom": d.get('nom'),
#             "prenom": d.get('prenom'),
#             "nom_complet": d.get('nom_complet'), 
#             "is_active": d.get('is_active'),
#             "matricule": d.get('matricule'),
#             "telephone": d.get('telephone'),
#             "direction_centrale_id": d.get('direction_centrale_id'), 
#             "direction_centrale": direction_centrale_data, 
#             "has_direction_centrale": d.get('direction_centrale_id') is not None
#         })
    
#     avec = len([x for x in data if x.get('has_direction_centrale')])
#     sans = len(data) - avec
#     actifs = len([x for x in data if x.get('is_active')])
#     inactifs = len(data) - actifs
    
#     return Response({
#         "status": "success", 
#         "code": "ALL_DIRECTEURS_CENTRALE",
#         "message": f"Total: {len(data)} directeur(s) centrale",
#         "data": {
#             "count": len(data), 
#             "statistics": {
#                 "with_direction_centrale": avec, 
#                 "without_direction_centrale": sans,
#                 "active": actifs,
#                 "inactive": inactifs
#             }, 
#             "directeurs": data
#         }
#     }, status=200)
"""
views.py — Service Affectation (port 8011)
Chaque view retourne le user COMPLET avec toutes ses données juridiques.
"""

import requests
from datetime import datetime
from django.core.cache import cache

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission

from .authentication import RemoteJWTAuthentication
from .discovery import get_auth_base_url, get_gateway_url, AUTH_APP_NAME
from .permissions import *
from .serializers import (
    UserDetailSerializer,
    UserByIdSerializer,
    UserSummarySerializer,
)


# ──────────────────────────────────────────────────────────────────────────────
# RÔLES VALIDES
# ──────────────────────────────────────────────────────────────────────────────

VALID_ROLES = [
    'agent',
    'vice_presedent',
    'directeur_direction',
    'responsable_departement',
    'directeur_centrale',
    'assistant_directeur_centrale',
    'directeur_direction_activite',
    'directeur_division_activite',
    'responsable_direction_division',
    'responsable_departement_division',
]

ROLE_DISPLAY = {
    'agent':                            'Agent',
    'vice_presedent':                   'Vice Presedent',
    'directeur_direction':              'Directeur de Direction',
    'responsable_departement':          'Responsable de Département',
    'directeur_centrale':               'Directeur Centrale',
    'assistant_directeur_centrale':     'Assistant Directeur Centrale',
    'directeur_direction_activite':     'Directeur Direction Activité',
    'directeur_division_activite':      'Directeur Division Activité',
    'responsable_direction_division':   'Responsable Direction Division',
    'responsable_departement_division': 'Responsable Département Division',
}


# ──────────────────────────────────────────────────────────────────────────────
# PERMISSION
# ──────────────────────────────────────────────────────────────────────────────

class IsAdmin(BasePermission):
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', '') == 'admin'
        )


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS HTTP
# ──────────────────────────────────────────────────────────────────────────────

def _call_auth(method: str, path: str, token: str, use_gateway: bool = False, **kwargs):
    if use_gateway:
        base_url = get_gateway_url()
    else:
        base_url = get_auth_base_url()

    url = f"{base_url}{path}"
    headers = {'Authorization': f'Bearer {token}'}
    print(f'[AFFECTATION] → {method.upper()} {url}')

    try:
        resp = getattr(requests, method)(url, headers=headers, timeout=5, **kwargs)
        print(f'[AFFECTATION] ← {resp.status_code}')
        if not resp.text.strip():
            return resp.status_code, {}
        return resp.status_code, resp.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f'[AFFECTATION] ✗ JSON: {e}')
        return resp.status_code, {"raw": resp.text}
    except requests.RequestException as e:
        print(f'[AFFECTATION] ✗ Réseau: {e}')
        cache.delete(f'eureka_url_{AUTH_APP_NAME}')
        if not use_gateway:
            return _call_auth(method, path, token, use_gateway=True, **kwargs)
        return 503, {"status": "error", "message": f"Service Auth injoignable : {e}"}


def _call_juridique(method: str, path: str, token: str, **kwargs):
    try:
        from .discovery import get_juridique_base_url
        juridique_url = get_juridique_base_url()
    except Exception:
        import os
        juridique_url = os.getenv('GATEWAY_URL', 'http://localhost:8083')

    url = f"{juridique_url}{path}"
    headers = {'Authorization': f'Bearer {token}'}
    print(f'[AFFECTATION] → Juridique {method.upper()} {url}')

    try:
        resp = getattr(requests, method)(url, headers=headers, timeout=5, **kwargs)
        print(f'[AFFECTATION] ← Juridique {resp.status_code}')
        if not resp.text.strip():
            return resp.status_code, {}
        return resp.status_code, resp.json()
    except requests.RequestException as e:
        print(f'[AFFECTATION] ✗ Erreur juridique: {e}')
        return 503, {"status": "error", "message": f"Service juridique injoignable: {e}"}


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS DÉSÉRIALISATION
# ──────────────────────────────────────────────────────────────────────────────

# def _normalize_user(u: dict) -> dict:
#     prenom = u.get('prenom', '') or ''
#     nom    = u.get('nom', '')    or ''
#     return {
#         'id':                       u.get('id'),
#         'email':                    u.get('email'),
#         'nom':                      nom,
#         'prenom':                   prenom,
#         'nom_complet':              u.get('nom_complet') or f"{prenom} {nom}".strip(),
#         'role':                     u.get('role'),
#         'role_display':             u.get('role_display'),
#         'is_active':                u.get('is_active', True),
#         'is_staff':                 u.get('is_staff', False),
#         'is_superuser':             u.get('is_superuser', False),
#         'matricule':                u.get('matricule'),
#         'telephone':                u.get('telephone'),
#         'adresse':                  u.get('adresse'),
#         'sexe':                     u.get('sexe'),
#         'sexe_display':             u.get('sexe_display'),
#         'date_naissance':           u.get('date_naissance'),
#         'age':                      u.get('age'),
#         'photo_profil':             u.get('photo_profil'),
#         'last_login':               u.get('last_login'),
#         'date_joined':              u.get('date_joined'),
#         'groups':                   u.get('groups', []),
#         'user_permissions':         u.get('user_permissions', []),
#         'account_stats':            u.get('account_stats', {}),
#         'other_info':               u.get('other_info', {}),
#         'admin_info':               u.get('admin_info', {}),
#         # IDs organisationnels
#         'activite_id':              u.get('activite_id'),
#         'direction_id':             u.get('direction_id'),
#         'departement_id':           u.get('departement_id'),
#         'direction_centrale_id':    u.get('direction_centrale_id'),
#         'direction_division_id':    u.get('direction_division_id'),
#         'departement_division_id':  u.get('departement_division_id'),
#         'direction_activite_id':    u.get('direction_activite_id'),
#         'division_activite_id':     u.get('division_activite_id'),
#     }


def _deserialize_user(user_dict: dict) -> dict:
    s = UserDetailSerializer(data=user_dict)
    if s.is_valid():
        return dict(s.data)
    print(f'[AFFECTATION] ⚠️ UserDetailSerializer errors: {s.errors}')
    return _normalize_user(user_dict)



def _deserialize_users(users_list: list) -> list:
    """
    Clean passthrough safe:
    - ne modifie aucun champ
    - garantit seulement dict valide
    """
    if not isinstance(users_list, list):
        return []

    return [
        u for u in users_list
        if isinstance(u, dict)
    ]

# # ──────────────────────────────────────────────────────────────────────────────
# # HELPER UNIVERSEL : enrichit UN user avec TOUTES ses données juridiques
# # ──────────────────────────────────────────────────────────────────────────────

# def _build_full_user(user: dict, token: str) -> dict:
#     """
#     Prend un user dict (désérialisé) et retourne un dict COMPLET :
#     - tous les champs Auth (identité, role, flags, dates, permissions…)
#     - tous les objets juridiques correspondant aux IDs présents
#     - tous les flags has_*
#     """

#     # ── Données juridiques (None si ID absent ou erreur) ──────────────────────

#     activite = None
#     if user.get('activite_id'):
#         sc, resp = _call_juridique('get', f'/juridique/activites/{user["activite_id"]}/', token)
#         if sc == 200:
#             activite = resp.get('data', resp)

#     direction = None
#     if user.get('direction_id'):
#         sc, resp = _call_juridique('get', f'/juridique/directions/{user["direction_id"]}/', token)
#         if sc == 200:
#             direction = resp.get('data', resp)

#     departement = None
#     if user.get('departement_id'):
#         sc, resp = _call_juridique('get', f'/juridique/departements/{user["departement_id"]}/', token)
#         if sc == 200:
#             departement = resp.get('data', resp)

#     direction_centrale = None
#     if user.get('direction_centrale_id'):
#         sc, resp = _call_juridique('get', f'/juridique/directions-centrales/{user["direction_centrale_id"]}/', token)
#         if sc == 200:
#             direction_centrale = resp.get('data', resp)

#     direction_division = None
#     if user.get('direction_division_id'):
#         sc, resp = _call_juridique('get', f'/juridique/directions-division/{user["direction_division_id"]}/', token)
#         if sc == 200:
#             direction_division = resp.get('data', resp)

#     departement_division = None
#     if user.get('departement_division_id'):
#         sc, resp = _call_juridique('get', f'/juridique/departements-division/{user["departement_division_id"]}/', token)
#         if sc == 200:
#             departement_division = resp.get('data', resp)

#     direction_activite = None
#     if user.get('direction_activite_id'):
#         sc, resp = _call_juridique('get', f'/juridique/direction_activite/{user["direction_activite_id"]}/', token)
#         if sc == 200:
#             direction_activite = resp.get('data', resp)

#     division_activite = None
#     if user.get('division_activite_id'):
#         sc, resp = _call_juridique('get', f'/juridique/division_activite/{user["division_activite_id"]}/', token)
#         if sc == 200:
#             division_activite = resp.get('data', resp)

#     # ── Assemblage final ───────────────────────────────────────────────────────

#     return {
#         # ── Identité ──────────────────────────────────────────────────────────
#         "id":               user.get('id'),
#         "email":            user.get('email'),
#         "nom":              user.get('nom'),
#         "prenom":           user.get('prenom'),
#         "nom_complet":      user.get('nom_complet'),

#         # ── Rôle & flags ──────────────────────────────────────────────────────
#         "role":             user.get('role'),
#         "role_display":     user.get('role_display'),
#         "is_active":        user.get('is_active', True),
#         "is_staff":         user.get('is_staff', False),
#         "is_superuser":     user.get('is_superuser', False),

#         # ── Infos pro ─────────────────────────────────────────────────────────
#         "matricule":        user.get('matricule'),
#         "telephone":        user.get('telephone'),
#         "adresse":          user.get('adresse'),

#         # ── Infos perso ───────────────────────────────────────────────────────
#         "sexe":             user.get('sexe'),
#         "sexe_display":     user.get('sexe_display'),
#         "date_naissance":   user.get('date_naissance'),
#         "age":              user.get('age'),

#         # ── Médias & dates ────────────────────────────────────────────────────
#         "photo_profil":     user.get('photo_profil'),
#         "last_login":       user.get('last_login'),
#         "date_joined":      user.get('date_joined'),

#         # ── Groupes & permissions ─────────────────────────────────────────────
#         "groups":           user.get('groups', []),
#         "user_permissions": user.get('user_permissions', []),

#         # ── Méta compte ───────────────────────────────────────────────────────
#         "account_stats":    user.get('account_stats', {}),
#         "other_info":       user.get('other_info', {}),
#         "admin_info":       user.get('admin_info', {}),

#         # ── IDs organisationnels ──────────────────────────────────────────────
#         "activite_id":              user.get('activite_id'),
#         "direction_id":             user.get('direction_id'),
#         "departement_id":           user.get('departement_id'),
#         "direction_centrale_id":    user.get('direction_centrale_id'),
#         "direction_division_id":    user.get('direction_division_id'),
#         "departement_division_id":  user.get('departement_division_id'),
#         "direction_activite_id":    user.get('direction_activite_id'),
#         "division_activite_id":     user.get('division_activite_id'),

#         # ── Objets juridiques complets ────────────────────────────────────────
#         "activite":             activite,
#         "direction":            direction,
#         "departement":          departement,
#         "direction_centrale":   direction_centrale,
#         "direction_division":   direction_division,
#         "departement_division": departement_division,
#         "direction_activite":   direction_activite,
#         "division_activite":    division_activite,

#         # ── Flags de présence ─────────────────────────────────────────────────
#         "has_activite":             bool(user.get('activite_id')),
#         "has_direction":            bool(user.get('direction_id')),
#         "has_departement":          bool(user.get('departement_id')),
#         "has_direction_centrale":   bool(user.get('direction_centrale_id')),
#         "has_direction_division":   bool(user.get('direction_division_id')),
#         "has_departement_division": bool(user.get('departement_division_id')),
#         "has_direction_activite":   bool(user.get('direction_activite_id')),
#         "has_division_activite":    bool(user.get('division_activite_id')),
#     }


# def _build_full_users(users: list, token: str) -> list:
#     """Applique _build_full_user sur une liste."""
#     return [_build_full_user(u, token) for u in users]
def _normalize_user(u: dict) -> dict:
    prenom = u.get('prenom', '') or ''
    nom    = u.get('nom', '')    or ''
    return {
        'id':                       u.get('id'),
        'email':                    u.get('email'),
        'nom':                      nom,
        'prenom':                   prenom,
        'nom_complet':              u.get('nom_complet') or f"{prenom} {nom}".strip(),
        'role':                     u.get('role'),
        'role_display':             u.get('role_display'),
        'is_active':                u.get('is_active', True),
        'is_staff':                 u.get('is_staff', False),
        'is_superuser':             u.get('is_superuser', False),
        'matricule':                u.get('matricule'),
        'telephone':                u.get('telephone'),
        'adresse':                  u.get('adresse'),
        'sexe':                     u.get('sexe'),
        'sexe_display':             u.get('sexe_display'),
        'date_naissance':           u.get('date_naissance'),
        'age':                      u.get('age'),
        'photo_profil':             u.get('photo_profil'),
        'last_login':               u.get('last_login'),
        'date_joined':              u.get('date_joined'),
        'groups':                   u.get('groups', []),
        'user_permissions':         u.get('user_permissions', []),
        'account_stats':            u.get('account_stats', {}),
        'other_info':               u.get('other_info', {}),
        'admin_info':               u.get('admin_info', {}),
        # IDs organisationnels
        'activite_id':              u.get('activite_id'),
        'direction_id':             u.get('direction_id'),
        'departement_id':           u.get('departement_id'),
        'direction_centrale_id':    u.get('direction_centrale_id'),
        'direction_activite_id':    u.get('direction_activite_id'),
        'division_activite_id':     u.get('division_activite_id'),
        'structure_id':             u.get('structure_id'),   # ← direction OU departement division
    }

def _fetch_structure_complete(structure_id: str, token: str, depth: int = 0) -> dict:
    """Récupère une structure avec toutes ses relations (division, direction_activite, etc.)"""
    if depth > 3:  # Éviter les récursions infinies
        return {"_id": structure_id, "_error": "Max recursion depth reached"}
    
    sc, resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
    if sc != 200:
        return {"_id": structure_id, "_error": f"Failed to fetch structure: {sc}"}
    
    structure = resp.get('data', resp)
    
    # Si la structure a une division, récupérer la division complète
    if structure.get('division') and isinstance(structure['division'], dict) and structure['division'].get('_id'):
        division_id = structure['division']['_id']
        sc_div, resp_div = _call_juridique('get', f'/juridique/division_activite/{division_id}/', token)
        if sc_div == 200:
            division_data = resp_div.get('data', resp_div)
            structure['division'] = division_data
            
            # Si la division a une direction_activite, la récupérer
            if division_data.get('direction_activite') and isinstance(division_data['direction_activite'], dict):
                dir_act_id = division_data['direction_activite'].get('_id')
                if dir_act_id:
                    sc_dir, resp_dir = _call_juridique('get', f'/juridique/direction_activite/{dir_act_id}/', token)
                    if sc_dir == 200:
                        direction_activite = resp_dir.get('data', resp_dir)
                        structure['division']['direction_activite'] = direction_activite
                        
                        # Si la direction_activite a une direction_centrale
                        if direction_activite.get('direction_centrale') and isinstance(direction_activite['direction_centrale'], dict):
                            dir_cent_id = direction_activite['direction_centrale'].get('_id')
                            if dir_cent_id:
                                sc_cent, resp_cent = _call_juridique('get', f'/juridique/directions-centrales/{dir_cent_id}/', token)
                                if sc_cent == 200:
                                    structure['division']['direction_activite']['direction_centrale'] = resp_cent.get('data', resp_cent)
    
    # Si la structure a une direction_activite directement
    elif structure.get('direction_activite') and isinstance(structure['direction_activite'], dict):
        dir_act_id = structure['direction_activite'].get('_id')
        if dir_act_id:
            sc_dir, resp_dir = _call_juridique('get', f'/juridique/direction_activite/{dir_act_id}/', token)
            if sc_dir == 200:
                direction_activite = resp_dir.get('data', resp_dir)
                structure['direction_activite'] = direction_activite
                
                # Récupérer la direction_centrale associée
                if direction_activite.get('direction_centrale') and isinstance(direction_activite['direction_centrale'], dict):
                    dir_cent_id = direction_activite['direction_centrale'].get('_id')
                    if dir_cent_id:
                        sc_cent, resp_cent = _call_juridique('get', f'/juridique/directions-centrales/{dir_cent_id}/', token)
                        if sc_cent == 200:
                            structure['direction_activite']['direction_centrale'] = resp_cent.get('data', resp_cent)
    
    return structure


def _fetch_activite_complete(activite_id: str, token: str) -> dict:
    """Récupère une activité avec ses directions et départements"""
    sc, resp = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
    if sc != 200:
        return {"_id": activite_id, "_error": f"Failed to fetch activite: {sc}"}
    
    activite = resp.get('data', resp)
    
    # Récupérer les directions de l'activité
    if activite.get('directions'):
        for i, direction in enumerate(activite['directions']):
            if isinstance(direction, dict) and direction.get('_id'):
                sc_dir, resp_dir = _call_juridique('get', f'/juridique/directions/{direction["_id"]}/', token)
                if sc_dir == 200:
                    direction_data = resp_dir.get('data', resp_dir)
                    activite['directions'][i] = direction_data
                    
                    # Récupérer les départements de chaque direction
                    if direction_data.get('departements'):
                        for j, dept in enumerate(direction_data['departements']):
                            if isinstance(dept, dict) and dept.get('_id'):
                                sc_dept, resp_dept = _call_juridique('get', f'/juridique/departements/{dept["_id"]}/', token)
                                if sc_dept == 200:
                                    activite['directions'][i]['departements'][j] = resp_dept.get('data', resp_dept)
    
    return activite


def _fetch_direction_complete(direction_id: str, token: str) -> dict:
    """Récupère une direction avec ses départements"""
    sc, resp = _call_juridique('get', f'/juridique/directions/{direction_id}/', token)
    if sc != 200:
        return {"_id": direction_id, "_error": f"Failed to fetch direction: {sc}"}
    
    direction = resp.get('data', resp)
    
    # Récupérer les départements complets
    if direction.get('departements'):
        for i, dept in enumerate(direction['departements']):
            if isinstance(dept, dict) and dept.get('_id'):
                sc_dept, resp_dept = _call_juridique('get', f'/juridique/departements/{dept["_id"]}/', token)
                if sc_dept == 200:
                    direction['departements'][i] = resp_dept.get('data', resp_dept)
    
    return direction


def _build_full_user(user: dict, token: str) -> dict:
    """Construit l'utilisateur complet avec TOUTES les données juridiques"""

    # ── Données juridiques enrichies ──────────────────────────────────────────

    activite = None
    if user.get('activite_id'):
        activite = _fetch_activite_complete(user["activite_id"], token)

    direction = None
    if user.get('direction_id'):
        direction = _fetch_direction_complete(user["direction_id"], token)

    departement = None
    if user.get('departement_id'):
        sc, resp = _call_juridique('get', f'/juridique/departements/{user["departement_id"]}/', token)
        if sc == 200:
            departement = resp.get('data', resp)

    direction_centrale = None
    if user.get('direction_centrale_id'):
        sc, resp = _call_juridique('get', f'/juridique/directions-centrales/{user["direction_centrale_id"]}/', token)
        if sc == 200:
            direction_centrale = resp.get('data', resp)

    direction_activite = None
    if user.get('direction_activite_id'):
        sc, resp = _call_juridique('get', f'/juridique/direction_activite/{user["direction_activite_id"]}/', token)
        if sc == 200:
            direction_activite = resp.get('data', resp)
            
            # Récupérer la direction_centrale associée
            if direction_activite.get('direction_centrale') and isinstance(direction_activite['direction_centrale'], dict):
                dir_cent_id = direction_activite['direction_centrale'].get('_id')
                if dir_cent_id:
                    sc_cent, resp_cent = _call_juridique('get', f'/juridique/directions-centrales/{dir_cent_id}/', token)
                    if sc_cent == 200:
                        direction_activite['direction_centrale'] = resp_cent.get('data', resp_cent)

    division_activite = None
    if user.get('division_activite_id'):
        sc, resp = _call_juridique('get', f'/juridique/division_activite/{user["division_activite_id"]}/', token)
        if sc == 200:
            division_activite = resp.get('data', resp)
            
            # Récupérer la direction_activite associée
            if division_activite.get('direction_activite') and isinstance(division_activite['direction_activite'], dict):
                dir_act_id = division_activite['direction_activite'].get('_id')
                if dir_act_id:
                    sc_dir, resp_dir = _call_juridique('get', f'/juridique/direction_activite/{dir_act_id}/', token)
                    if sc_dir == 200:
                        direction_activite_data = resp_dir.get('data', resp_dir)
                        division_activite['direction_activite'] = direction_activite_data
                        
                        # Récupérer la direction_centrale
                        if direction_activite_data.get('direction_centrale') and isinstance(direction_activite_data['direction_centrale'], dict):
                            dir_cent_id = direction_activite_data['direction_centrale'].get('_id')
                            if dir_cent_id:
                                sc_cent, resp_cent = _call_juridique('get', f'/juridique/directions-centrales/{dir_cent_id}/', token)
                                if sc_cent == 200:
                                    division_activite['direction_activite']['direction_centrale'] = resp_cent.get('data', resp_cent)

    # structure_id → Récupération COMPLÈTE (avec toutes les relations)
    structure = None
    if user.get('structure_id'):
        structure = _fetch_structure_complete(user["structure_id"], token)

    # ── Assemblage final ──────────────────────────────────────────────────────

    return {
        # ── Identité ──────────────────────────────────────────────────────────
        "id":               user.get('id'),
        "email":            user.get('email'),
        "nom":              user.get('nom'),
        "prenom":           user.get('prenom'),
        "nom_complet":      user.get('nom_complet'),

        # ── Rôle & flags ──────────────────────────────────────────────────────
        "role":             user.get('role'),
        "role_display":     user.get('role_display'),
        "is_active":        user.get('is_active', True),
        "is_staff":         user.get('is_staff', False),
        "is_superuser":     user.get('is_superuser', False),

        # ── Infos pro ─────────────────────────────────────────────────────────
        "matricule":        user.get('matricule'),
        "telephone":        user.get('telephone'),
        "adresse":          user.get('adresse'),

        # ── Infos perso ───────────────────────────────────────────────────────
        "sexe":             user.get('sexe'),
        "sexe_display":     user.get('sexe_display'),
        "date_naissance":   user.get('date_naissance'),
        "age":              user.get('age'),

        # ── Médias & dates ────────────────────────────────────────────────────
        "photo_profil":     user.get('photo_profil'),
        "last_login":       user.get('last_login'),
        "date_joined":      user.get('date_joined'),

        # ── Groupes & permissions ─────────────────────────────────────────────
        "groups":           user.get('groups', []),
        "user_permissions": user.get('user_permissions', []),

        # ── Méta compte ───────────────────────────────────────────────────────
        "account_stats":    user.get('account_stats', {}),
        "other_info":       user.get('other_info', {}),
        "admin_info":       user.get('admin_info', {}),

        # ── IDs organisationnels ──────────────────────────────────────────────
        "activite_id":           user.get('activite_id'),
        "direction_id":          user.get('direction_id'),
        "departement_id":        user.get('departement_id'),
        "direction_centrale_id": user.get('direction_centrale_id'),
        "direction_activite_id": user.get('direction_activite_id'),
        "division_activite_id":  user.get('division_activite_id'),
        "structure_id":          user.get('structure_id'),

        # ── Objets juridiques COMPLETS (avec toutes les relations) ────────────
        "activite":           activite,
        "direction":          direction,
        "departement":        departement,
        "direction_centrale": direction_centrale,
        "direction_activite": direction_activite,
        "division_activite":  division_activite,
        "structure":          structure,   # Contient division + direction_activite + direction_centrale

        # ── Flags de présence ─────────────────────────────────────────────────
        "has_activite":           bool(user.get('activite_id')),
        "has_direction":          bool(user.get('direction_id')),
        "has_departement":        bool(user.get('departement_id')),
        "has_direction_centrale": bool(user.get('direction_centrale_id')),
        "has_direction_activite": bool(user.get('direction_activite_id')),
        "has_division_activite":  bool(user.get('division_activite_id')),
        "has_structure":          bool(user.get('structure_id')),
    }
# def _build_full_user(user: dict, token: str) -> dict:

#     # ── Données juridiques ────────────────────────────────────────────────────

#     activite = None
#     if user.get('activite_id'):
#         sc, resp = _call_juridique('get', f'/juridique/activites/{user["activite_id"]}/', token)
#         if sc == 200:
#             activite = resp.get('data', resp)

#     direction = None
#     if user.get('direction_id'):
#         sc, resp = _call_juridique('get', f'/juridique/directions/{user["direction_id"]}/', token)
#         if sc == 200:
#             direction = resp.get('data', resp)

#     departement = None
#     if user.get('departement_id'):
#         sc, resp = _call_juridique('get', f'/juridique/departements/{user["departement_id"]}/', token)
#         if sc == 200:
#             departement = resp.get('data', resp)

#     direction_centrale = None
#     if user.get('direction_centrale_id'):
#         sc, resp = _call_juridique('get', f'/juridique/directions-centrales/{user["direction_centrale_id"]}/', token)
#         if sc == 200:
#             direction_centrale = resp.get('data', resp)

#     direction_activite = None
#     if user.get('direction_activite_id'):
#         sc, resp = _call_juridique('get', f'/juridique/direction_activite/{user["direction_activite_id"]}/', token)
#         if sc == 200:
#             direction_activite = resp.get('data', resp)

#     division_activite = None
#     if user.get('division_activite_id'):
#         sc, resp = _call_juridique('get', f'/juridique/division_activite/{user["division_activite_id"]}/', token)
#         if sc == 200:
#             division_activite = resp.get('data', resp)

#     # structure_id → peut être direction ou departement selon le rôle
#     structure = None
#     if user.get('structure_id'):
#         sc, resp = _call_juridique('get', f'/juridique/structures/{user["structure_id"]}/', token)
#         if sc == 200:
#             structure = resp.get('data', resp)

#     # ── Assemblage final ──────────────────────────────────────────────────────

#     return {
#         # ── Identité ──────────────────────────────────────────────────────────
#         "id":               user.get('id'),
#         "email":            user.get('email'),
#         "nom":              user.get('nom'),
#         "prenom":           user.get('prenom'),
#         "nom_complet":      user.get('nom_complet'),

#         # ── Rôle & flags ──────────────────────────────────────────────────────
#         "role":             user.get('role'),
#         "role_display":     user.get('role_display'),
#         "is_active":        user.get('is_active', True),
#         "is_staff":         user.get('is_staff', False),
#         "is_superuser":     user.get('is_superuser', False),

#         # ── Infos pro ─────────────────────────────────────────────────────────
#         "matricule":        user.get('matricule'),
#         "telephone":        user.get('telephone'),
#         "adresse":          user.get('adresse'),

#         # ── Infos perso ───────────────────────────────────────────────────────
#         "sexe":             user.get('sexe'),
#         "sexe_display":     user.get('sexe_display'),
#         "date_naissance":   user.get('date_naissance'),
#         "age":              user.get('age'),

#         # ── Médias & dates ────────────────────────────────────────────────────
#         "photo_profil":     user.get('photo_profil'),
#         "last_login":       user.get('last_login'),
#         "date_joined":      user.get('date_joined'),

#         # ── Groupes & permissions ─────────────────────────────────────────────
#         "groups":           user.get('groups', []),
#         "user_permissions": user.get('user_permissions', []),

#         # ── Méta compte ───────────────────────────────────────────────────────
#         "account_stats":    user.get('account_stats', {}),
#         "other_info":       user.get('other_info', {}),
#         "admin_info":       user.get('admin_info', {}),

#         # ── IDs organisationnels ──────────────────────────────────────────────
#         "activite_id":           user.get('activite_id'),
#         "direction_id":          user.get('direction_id'),
#         "departement_id":        user.get('departement_id'),
#         "direction_centrale_id": user.get('direction_centrale_id'),
#         "direction_activite_id": user.get('direction_activite_id'),
#         "division_activite_id":  user.get('division_activite_id'),
#         "structure_id":          user.get('structure_id'),

#         # ── Objets juridiques complets ────────────────────────────────────────
#         "activite":           activite,
#         "direction":          direction,
#         "departement":        departement,
#         "direction_centrale": direction_centrale,
#         "direction_activite": direction_activite,
#         "division_activite":  division_activite,
#         "structure":          structure,   # contient type + division populated

#         # ── Flags de présence ─────────────────────────────────────────────────
#         "has_activite":           bool(user.get('activite_id')),
#         "has_direction":          bool(user.get('direction_id')),
#         "has_departement":        bool(user.get('departement_id')),
#         "has_direction_centrale": bool(user.get('direction_centrale_id')),
#         "has_direction_activite": bool(user.get('direction_activite_id')),
#         "has_division_activite":  bool(user.get('division_activite_id')),
#         "has_structure":          bool(user.get('structure_id')),
#     }


def _build_full_users(users: list, token: str) -> list:
    """Applique _build_full_user sur une liste."""
    return [_build_full_user(u, token) for u in users]

# ──────────────────────────────────────────────────────────────────────────────
# VIEW : ASSIGN ROLE
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def assign_role(request):
    """POST /affectation/assign-role/"""
    force_gateway = request.query_params.get('force_gateway', '').lower() == 'true'
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id = request.data.get('user_id')
    role    = request.data.get('role')

    if not user_id:
        return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
    if not role:
        return Response({"status": "error", "code": "MISSING_ROLE", "message": "role est obligatoire."}, status=400)
    if role not in VALID_ROLES:
        return Response({"status": "error", "code": "INVALID_ROLE", "message": f"Rôle '{role}' invalide.", "valid_roles": VALID_ROLES}, status=400)

    # Étape 1 : récupérer l'user
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token, use_gateway=force_gateway)
    if sc == 503:
        return Response(user_response, status=503)
    if sc == 404:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)
    if sc != 200:
        return Response({"status": "error", "code": "AUTH_SERVICE_ERROR", "message": f"Service Auth a retourné {sc}.", "detail": user_response}, status=sc)

    user_data = _deserialize_user(user_response.get('user', {}))

    if not user_data:
        return Response({"status": "error", "code": "INVALID_RESPONSE", "message": "Structure de réponse invalide du service Auth."}, status=500)
    if user_data['role'] == 'admin':
        return Response({"status": "error", "code": "CANNOT_MODIFY_ADMIN", "message": "Impossible de modifier le rôle d'un administrateur."}, status=400)

    previous_role = user_data['role']

    # Étape 2 : mettre à jour le rôle
    sc, updated = _call_auth('patch', f'/auth/users/{user_id}/update-role/', token, json={"role": role}, use_gateway=force_gateway)
    if sc == 503:
        return Response(updated, status=503)
    if sc not in (200, 201):
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": f"Impossible de mettre à jour le rôle (status {sc}).", "detail": updated}, status=sc)

    # Étape 3 : re-fetch pour avoir l'user avec le nouveau rôle + données juridiques
    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token, use_gateway=force_gateway)
    if sc2 == 200:
        user_data_updated = _deserialize_user(user_response2.get('user', {}))
        full_user = _build_full_user(user_data_updated, token)
    else:
        # fallback : on met à jour manuellement le rôle dans le dict existant
        user_data['role'] = role
        user_data['role_display'] = ROLE_DISPLAY.get(role, role)
        full_user = _build_full_user(user_data, token)

    admin_name = getattr(admin, 'nom_complet', None) or f"{getattr(admin, 'prenom', '')} {getattr(admin, 'nom', '')}".strip() or str(admin)

    return Response({
        "status": "success",
        "code": "ROLE_ASSIGNED",
        "message": f"Rôle '{ROLE_DISPLAY.get(role, role)}' affecté à {full_user['nom_complet']}.",
        "data": {
            **full_user,
            "previous_role":         previous_role,
            "previous_role_display": ROLE_DISPLAY.get(previous_role, previous_role) if previous_role else None,
            "assigned_by": {
                "id":   admin.id,
                "name": admin_name,
                "role": getattr(admin, 'role', 'unknown'),
            },
            "timestamp": datetime.now().isoformat(),
        },
        "metadata": {
            "source":           "gateway" if force_gateway else "eureka",
            "discovery_method": "gateway_forced" if force_gateway else "eureka",
            "service":          "affectation-service",
            "version":          "1.0.0",
        },
    }, status=200)


# ──────────────────────────────────────────────────────────────────────────────
# VIEW : GET USER
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def get_user(request, user_id):
    """GET /affectation/user/<user_id>/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    force_gateway = request.query_params.get('force_gateway', '').lower() == 'true'

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token, use_gateway=force_gateway)
    if sc != 200:
        return Response(user_response, status=sc)

    user_data = _deserialize_user(user_response.get('user', {}))
    full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success",
        "data": full_user,
        "metadata": {"source": "gateway" if force_gateway else "eureka"},
    })


# ──────────────────────────────────────────────────────────────────────────────
# AFFECTATION ACTIVITÉ
# ──────────────────────────────────────────────────────────────────────────────

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def assign_activite_to_user(request):
#     """PATCH /affectation/assign-activite/"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user

#     user_id    = request.data.get('user_id')
#     activite_id = request.data.get('activite_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
#     if not activite_id:
#         return Response({"status": "error", "code": "MISSING_ACTIVITE_ID", "message": "activite_id est obligatoire."}, status=400)

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     user_data = _deserialize_user(user_response.get('user', {}))

#     if user_data['role'] != 'vice_presedent':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": f"L'utilisateur a le rôle '{user_data['role']}', doit être 'vice_presedent'"}, status=400)

#     if user_data.get('activite_id'):
#         existing_activite_nom = "Inconnue"
#         sc_ex, ex_resp = _call_juridique('get', f'/juridique/activites/{user_data["activite_id"]}/', token)
#         if sc_ex == 200:
#             existing_activite_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')
#         return Response({
#             "status": "error", "code": "ALREADY_ASSIGNED",
#             "message": "L'utilisateur a déjà une activité affectée.",
#             "data": {
#                 "user_id": user_id, "user_name": user_data['nom_complet'],
#                 "existing_activite_id": user_data['activite_id'],
#                 "existing_activite_nom": existing_activite_nom,
#                 "suggestion": "Utilisez PUT /affectation/reassign-activite/ pour changer d'activité",
#             },
#         }, status=400)

#     sc_act, activite_resp = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
#     if sc_act == 404:
#         return Response({"status": "error", "code": "ACTIVITE_NOT_FOUND", "message": f"Activité {activite_id} non trouvée."}, status=404)
#     if sc_act != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": f"Service juridique indisponible (status {sc_act})."}, status=503)

#     sc_update, updated = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"activite_id": activite_id})
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour l'activite_id.", "detail": updated}, status=sc_update)

#     # Re-fetch user complet après mise à jour
#     sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc2 == 200:
#         full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
#     else:
#         user_data['activite_id'] = activite_id
#         full_user = _build_full_user(user_data, token)

#     return Response({
#         "status": "success",
#         "code": "ACTIVITE_ASSIGNED",
#         "message": f"Activité affectée à {full_user['nom_complet']}.",
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id":   admin.id,
#                 "name": getattr(admin, 'nom_complet', str(admin)),
#                 "role": getattr(admin, 'role', 'admin'),
#             },
#             "timestamp": datetime.now().isoformat(),
#         },
#     }, status=200)

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def assign_activite_to_user(request):
#     """PATCH /affectation/assign-activite/"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user

#     user_id = request.data.get('user_id')
#     activite_id = request.data.get('activite_id')

#     # ─────────────────────────────
#     # VALIDATION INPUT
#     # ─────────────────────────────
#     if not user_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_USER_ID",
#             "message": "user_id est obligatoire."
#         }, status=400)

#     if not activite_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_ACTIVITE_ID",
#             "message": "activite_id est obligatoire."
#         }, status=400)

#     # ─────────────────────────────
#     # GET USER FROM AUTH
#     # ─────────────────────────────
#     sc, user_response = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur {user_id} introuvable."
#         }, status=404)

#     user_data = _deserialize_user(user_response.get('user', {}))

#     # ─────────────────────────────
#     # ROLE CHECK
#     # ─────────────────────────────
#     if user_data.get('role') != 'vice_presedent':
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": f"Rôle invalide: {user_data.get('role')}"
#         }, status=400)

#     # ─────────────────────────────
#     # CHECK EXISTING ACTIVITE
#     # ─────────────────────────────
#     if user_data.get('activite_id'):
#         return Response({
#             "status": "error",
#             "code": "ALREADY_ASSIGNED",
#             "message": "Utilisateur déjà affecté à une activité.",
#             "data": {
#                 "user_id": user_id,
#                 "user_name": user_data.get('nom_complet'),
#                 "existing_activite_id": user_data.get('activite_id'),
#                 "suggestion": "Utilisez reassign endpoint"
#             }
#         }, status=400)

#     # ─────────────────────────────
#     # CHECK ACTIVITE EXISTS
#     # ─────────────────────────────
#     sc_act, activite_resp = _call_juridique(
#         'get',
#         f'/juridique/activites/{activite_id}/',
#         token
#     )

#     if sc_act == 404:
#         return Response({
#             "status": "error",
#             "code": "ACTIVITE_NOT_FOUND",
#             "message": "Activité introuvable."
#         }, status=404)

#     if sc_act != 200:
#         return Response({
#             "status": "error",
#             "code": "JURIDIQUE_ERROR",
#             "message": "Service juridique indisponible"
#         }, status=503)

#     # ─────────────────────────────
#     # UPDATE USER IN AUTH SERVICE
#     # ─────────────────────────────
#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={"activite_id": activite_id}
#     )

#     if sc_update != 200:
#         return Response({
#             "status": "error",
#             "code": "UPDATE_FAILED",
#             "message": "Impossible de mettre à jour l'utilisateur",
#             "detail": updated
#         }, status=sc_update)

#     # ─────────────────────────────
#     # VERIFY PERSISTENCE (IMPORTANT 🔥)
#     # ─────────────────────────────
#     sc_check, check_resp = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc_check != 200:
#         return Response({
#             "status": "error",
#             "code": "POST_CHECK_FAILED",
#             "message": "Impossible de vérifier la mise à jour"
#         }, status=503)

#     new_user = _deserialize_user(check_resp.get('user', {}))

#     if str(new_user.get('activite_id')) != str(activite_id):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "activite_id n'a pas été sauvegardé côté Auth (BUG BACKEND)",
#             "debug": {
#                 "sent": activite_id,
#                 "received": new_user.get('activite_id')
#             }
#         }, status=500)

#     # ─────────────────────────────
#     # BUILD FULL USER
#     # ─────────────────────────────
#     full_user = _build_full_user(new_user, token)

#     # ─────────────────────────────
#     # RESPONSE SUCCESS
#     # ─────────────────────────────
#     return Response({
#         "status": "success",
#         "code": "ACTIVITE_ASSIGNED",
#         "message": f"Activité affectée à {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id": admin.id,
#                 "name": getattr(admin, 'nom_complet', str(admin)),
#                 "role": getattr(admin, 'role', 'admin'),
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)
@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def assign_activite_to_user(request):

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id = request.data.get('user_id')
    activite_id = request.data.get('activite_id')

    # ── validation
    if not user_id or not activite_id:
        return Response({
            "status": "error",
            "code": "MISSING_FIELDS"
        }, status=400)

    # ── GET USER (RAW ONLY - IMPORTANT)
    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND"
        }, status=404)

    user_data = user_response.get('user', {})   # 🔥 RAW DICT (IMPORTANT)

    # ── ROLE CHECK
    if user_data.get('role') != 'vice_presedent':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE"
        }, status=400)

    # ── CHECK EXISTING
    if user_data.get('activite_id'):
        return Response({
            "status": "error",
            "code": "ALREADY_ASSIGNED"
        }, status=400)

    # ── CHECK ACTIVITE
    sc_act, _ = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)

    if sc_act != 200:
        return Response({
            "status": "error",
            "code": "ACTIVITE_NOT_FOUND"
        }, status=404)

    # ── UPDATE AUTH (FIXED URL)
    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={"activite_id": activite_id}
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "detail": updated
        }, status=500)

    # ── VERIFY (RAW AGAIN)
    sc_check, check_resp = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    new_user = check_resp.get('user', {})

    # 🔥 DEBUG IMPORTANT
    print("EXPECTED:", activite_id)
    print("GOT:", new_user.get('activite_id'))

    if str(new_user.get('activite_id')) != str(activite_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "debug": {
                "sent": activite_id,
                "received": new_user.get('activite_id')
            }
        }, status=500)

    # ── FINAL RESPONSE
    full_user = _build_full_user(new_user, token)

    return Response({
        "status": "success",
        "code": "ACTIVITE_ASSIGNED",
        "data": {
            **full_user,
            "assigned_by": {
                "id": admin.id,
                "role": admin.role
            }
        }
    }, status=200)
@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def reassign_activite_to_user(request):
    """PUT /affectation/reassign-activite/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id     = request.data.get('user_id')
    activite_id = request.data.get('activite_id')

    if not user_id:
        return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
    if not activite_id:
        return Response({"status": "error", "code": "MISSING_ACTIVITE_ID", "message": "activite_id est obligatoire."}, status=400)

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))

    if user_data['role'] != 'vice_presedent':
        return Response({"status": "error", "code": "INVALID_ROLE", "message": f"L'utilisateur a le rôle '{user_data['role']}', doit être 'vice_presedent'"}, status=400)

    # Ancienne activité
    old_activite_id  = user_data.get('activite_id')
    old_activite_nom = None
    if old_activite_id:
        sc_old, old_resp = _call_juridique('get', f'/juridique/activites/{old_activite_id}/', token)
        if sc_old == 200:
            old_activite_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

    sc_act, activite_resp = _call_juridique('get', f'/juridique/activites/{activite_id}/', token)
    if sc_act == 404:
        return Response({"status": "error", "code": "ACTIVITE_NOT_FOUND", "message": f"Activité {activite_id} non trouvée."}, status=404)
    if sc_act != 200:
        return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

    sc_update, updated = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"activite_id": activite_id})
    if sc_update != 200:
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour l'activite_id.", "detail": updated}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['activite_id'] = activite_id
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success",
        "code": "ACTIVITE_REASSIGNED",
        "message": f"Activité changée de '{old_activite_nom or 'aucune'}' vers '{full_user['activite']['nom'] if full_user.get('activite') else activite_id}' pour {full_user['nom_complet']}.",
        "data": {
            **full_user,
            "previous_activite_id":  old_activite_id,
            "previous_activite_nom": old_activite_nom,
            "assigned_by": {
                "id":   admin.id,
                "name": getattr(admin, 'nom_complet', str(admin)),
                "role": getattr(admin, 'role', 'admin'),
            },
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def remove_activite_from_user(request, user_id):
    """DELETE /affectation/users/<user_id>/remove-activite/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))

    current_activite_id = user_data.get('activite_id')
    if not current_activite_id:
        return Response({"status": "error", "code": "NO_ACTIVITE_ASSIGNED", "message": "Cet utilisateur n'a aucune activité affectée."}, status=400)

    activite_nom = "Inconnue"
    sc_act, activite_resp = _call_juridique('get', f'/juridique/activites/{current_activite_id}/', token)
    if sc_act == 200:
        activite_nom = activite_resp.get('data', {}).get('nom', 'Inconnue')

    sc_update, updated = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"activite_id": None})
    if sc_update != 200:
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de supprimer l'activite_id.", "detail": updated}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['activite_id'] = None
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success",
        "code": "ACTIVITE_REMOVED",
        "message": f"Activité '{activite_nom}' désaffectée de {full_user['nom_complet']}.",
        "data": {
            **full_user,
            "removed_activite_id":  current_activite_id,
            "removed_activite_nom": activite_nom,
            "removed_by": {
                "id":   admin.id,
                "name": getattr(admin, 'nom_complet', str(admin)),
                "role": getattr(admin, 'role', 'admin'),
            },
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


# ──────────────────────────────────────────────────────────────────────────────
# LISTES DIRECTEURS ACTIVITÉ (vice_presedent)
# ──────────────────────────────────────────────────────────────────────────────

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_activite(request):
#     """GET /affectation/users/directeurs-activite/ — SANS activité affectée"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "AUTH_SERVICE_ERROR", "message": "Impossible de récupérer la liste des utilisateurs"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'vice_presedent' and not u.get('activite_id')]
#     data = _build_full_users(cibles, token)

#     return Response({
#         "status": "success",
#         "code": "DIRECTEURS_SANS_ACTIVITE",
#         "message": f"{len(data)} directeur(s) d'activité sans activité affectée",
#         "data": {"count": len(data), "directeurs": data},
#         "timestamp": datetime.now().isoformat(),
#     }, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_activite_affectes(request):
#     """GET /affectation/users/directeurs-activite/affectes/ — AVEC activité affectée"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "AUTH_SERVICE_ERROR", "message": "Impossible de récupérer la liste des utilisateurs"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'vice_presedent' and u.get('activite_id')]
#     data = _build_full_users(cibles, token)

#     return Response({
#         "status": "success",
#         "code": "DIRECTEURS_AVEC_ACTIVITE",
#         "message": f"{len(data)} directeur(s) d'activité avec activité affectée",
#         "data": {"count": len(data), "directeurs": data},
#         "timestamp": datetime.now().isoformat(),
#     }, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_all_directeurs_activite(request):
#     """GET /affectation/users/directeurs-activite/all/ — TOUS"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     show_inactive = request.query_params.get('show_inactive', '').lower() == 'true'

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "AUTH_SERVICE_ERROR", "message": "Impossible de récupérer la liste des utilisateurs"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'vice_presedent']
#     if not show_inactive:
#         cibles = [u for u in cibles if u.get('is_active', True)]

#     data = _build_full_users(cibles, token)

#     total          = len(data)
#     avec_activite  = len([d for d in data if d['has_activite']])
#     sans_activite  = total - avec_activite
#     actifs         = len([d for d in data if d['is_active']])
#     inactifs       = total - actifs

#     return Response({
#         "status": "success",
#         "code": "ALL_DIRECTEURS_ACTIVITE",
#         "message": f"Total: {total} directeur(s) d'activité",
#         "data": {
#             "count": total,
#             "statistics": {
#                 "with_activite":    avec_activite,
#                 "without_activite": sans_activite,
#                 "active":           actifs,
#                 "inactive":         inactifs,
#             },
#             "directeurs": data,
#         },
#         "timestamp": datetime.now().isoformat(),
#     }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_activite(request):
    """GET /affectation/users/directeurs-activite/ — SANS activité affectée"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "code": "AUTH_SERVICE_ERROR",
             "message": "Impossible de récupérer la liste des utilisateurs"},
            status=503
        )

    users_raw = users_response.get('users', [])

    # ⚠️ FIX IMPORTANT: role correct
    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'vice_presedent'
        and not u.get('activite_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "DIRECTEURS_SANS_ACTIVITE",
        "message": f"{len(data)} directeur(s) sans activité affectée",
        "data": {
            "count": len(data),
            "directeurs": data
        },
        "timestamp": datetime.now().isoformat(),
    }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_activite_affectes(request):
    """GET /affectation/users/directeurs-activite/affectes/ — AVEC activité"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "code": "AUTH_SERVICE_ERROR",
             "message": "Impossible de récupérer la liste des utilisateurs"},
            status=503
        )

    users_raw = users_response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'vice_presedent'
        and u.get('activite_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "DIRECTEURS_AVEC_ACTIVITE",
        "message": f"{len(data)} directeur(s) avec activité affectée",
        "data": {
            "count": len(data),
            "directeurs": data
        },
        "timestamp": datetime.now().isoformat(),
    }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_all_directeurs_activite(request):
    """GET /affectation/users/directeurs-activite/all/ — TOUS"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    show_inactive = request.query_params.get('show_inactive', '').lower() == 'true'

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "code": "AUTH_SERVICE_ERROR",
             "message": "Impossible de récupérer la liste des utilisateurs"},
            status=503
        )

    users_raw = users_response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'vice_presedent'
    ]

    if not show_inactive:
        cibles = [
            u for u in cibles
            if u.get('is_active', True)
        ]

    data = _build_full_users(cibles, token)

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
                "inactive": inactifs,
            },
            "directeurs": data,
        },
        "timestamp": datetime.now().isoformat(),
    }, status=200)

# ──────────────────────────────────────────────────────────────────────────────
# DIRECTIONS — Assignation
# ──────────────────────────────────────────────────────────────────────────────

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def assign_direction_to_user(request):
#     """PATCH /affectation/assign-direction/"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     admin = request.user

#     user_id      = request.data.get('user_id')
#     direction_id = request.data.get('direction_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
#     if not direction_id:
#         return Response({"status": "error", "code": "MISSING_DIRECTION_ID", "message": "direction_id est obligatoire."}, status=400)

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     user_data = _deserialize_user(user_response.get('user', {}))

#     if user_data['role'] != 'directeur_direction':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": f"L'utilisateur doit être 'directeur_direction' (actuel: {user_data['role']})"}, status=400)

#     if user_data.get('direction_id'):
#         existing_nom = "Inconnue"
#         sc_ex, ex_resp = _call_juridique('get', f'/juridique/directions/{user_data["direction_id"]}/', token)
#         if sc_ex == 200:
#             existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')
#         return Response({"status": "error", "code": "ALREADY_ASSIGNED", "message": "L'utilisateur a déjà une direction affectée.", "data": {"existing_direction_id": user_data['direction_id'], "existing_direction_nom": existing_nom}}, status=400)

#     sc_dir, dir_resp = _call_juridique('get', f'/juridique/directions/{direction_id}/', token)
#     if sc_dir == 404:
#         return Response({"status": "error", "code": "DIRECTION_NOT_FOUND", "message": f"Direction {direction_id} non trouvée."}, status=404)
#     if sc_dir != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible"}, status=503)

#     sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": direction_id})
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour"}, status=sc_update)

#     sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc2 == 200:
#         full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
#     else:
#         user_data['direction_id'] = direction_id
#         full_user = _build_full_user(user_data, token)

#     return Response({
#         "status": "success", "code": "DIRECTION_ASSIGNED",
#         "message": f"Direction affectée à {full_user['nom_complet']}.",
#         "data": {
#             **full_user,
#             "assigned_by": {"id": admin.id, "name": getattr(admin, 'nom_complet', str(admin)), "role": getattr(admin, 'role', 'admin')},
#             "timestamp": datetime.now().isoformat(),
#         },
#     }, status=200)
@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def assign_direction_to_user(request):
    """PATCH /affectation/assign-direction/"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id = request.data.get('user_id')
    direction_id = request.data.get('direction_id')

    # ─────────────────────────────
    # VALIDATION
    # ─────────────────────────────
    if not user_id:
        return Response({
            "status": "error",
            "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)

    if not direction_id:
        return Response({
            "status": "error",
            "code": "MISSING_DIRECTION_ID",
            "message": "direction_id est obligatoire."
        }, status=400)

    # ─────────────────────────────
    # GET USER
    # ─────────────────────────────
    sc, user_response = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} introuvable."
        }, status=404)

    user_data = _deserialize_user(
        user_response.get('user', {})
    )

    # ─────────────────────────────
    # ROLE CHECK
    # ─────────────────────────────
    if user_data.get('role') != 'directeur_direction':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": f"L'utilisateur doit être 'directeur_direction' (actuel: {user_data.get('role')})"
        }, status=400)

    # ─────────────────────────────
    # ALREADY ASSIGNED
    # ─────────────────────────────
    if user_data.get('direction_id'):

        existing_nom = "Inconnue"

        sc_ex, ex_resp = _call_juridique(
            'get',
            f'/juridique/directions/{user_data["direction_id"]}/',
            token
        )

        if sc_ex == 200:
            existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')

        return Response({
            "status": "error",
            "code": "ALREADY_ASSIGNED",
            "message": "L'utilisateur a déjà une direction affectée.",
            "data": {
                "existing_direction_id": user_data.get('direction_id'),
                "existing_direction_nom": existing_nom
            }
        }, status=400)

    # ─────────────────────────────
    # CHECK DIRECTION EXISTS
    # ─────────────────────────────
    sc_dir, dir_resp = _call_juridique(
        'get',
        f'/juridique/directions/{direction_id}/',
        token
    )

    if sc_dir == 404:
        return Response({
            "status": "error",
            "code": "DIRECTION_NOT_FOUND",
            "message": f"Direction {direction_id} non trouvée."
        }, status=404)

    if sc_dir != 200:
        return Response({
            "status": "error",
            "code": "JURIDIQUE_SERVICE_ERROR",
            "message": "Service juridique indisponible"
        }, status=503)

    # ─────────────────────────────
    # UPDATE AUTH SERVICE
    # ─────────────────────────────
    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "direction_id": direction_id
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "message": "Impossible de mettre à jour l'utilisateur",
            "detail": updated
        }, status=sc_update)

    # ─────────────────────────────
    # VERIFY PERSISTENCE
    # ─────────────────────────────
    sc_check, check_resp = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc_check != 200:
        return Response({
            "status": "error",
            "code": "POST_CHECK_FAILED",
            "message": "Impossible de vérifier la mise à jour"
        }, status=503)

    # IMPORTANT 🔥
    # UTILISER RAW USER
    raw_user = check_resp.get('user', {})

    print("RAW USER =", raw_user)

    if str(raw_user.get('direction_id')) != str(direction_id):

        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "direction_id n'a pas été sauvegardé côté Auth",
            "debug": {
                "sent": direction_id,
                "received": raw_user.get('direction_id')
            }
        }, status=500)

    # ─────────────────────────────
    # BUILD FULL USER
    # ─────────────────────────────
    full_user = _build_full_user(
        raw_user,
        token
    )

    # ─────────────────────────────
    # SUCCESS
    # ─────────────────────────────
    return Response({
        "status": "success",
        "code": "DIRECTION_ASSIGNED",
        "message": f"Direction affectée à {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "assigned_by": {
                "id": admin.id,
                "name": getattr(admin, 'nom_complet', str(admin)),
                "role": getattr(admin, 'role', 'admin'),
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)

@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def reassign_direction_to_user(request):
    """PUT /affectation/reassign-direction/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id      = request.data.get('user_id')
    direction_id = request.data.get('direction_id')

    if not user_id or not direction_id:
        return Response({"status": "error", "message": "user_id et direction_id requis"}, status=400)

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))

    if user_data['role'] != 'directeur_direction':
        return Response({"status": "error", "message": "L'utilisateur doit être 'directeur_direction'"}, status=400)

    old_direction_id  = user_data.get('direction_id')
    old_direction_nom = None
    if old_direction_id:
        sc_old, old_resp = _call_juridique('get', f'/juridique/directions/{old_direction_id}/', token)
        if sc_old == 200:
            old_direction_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

    sc_dir, dir_resp = _call_juridique('get', f'/juridique/directions/{direction_id}/', token)
    if sc_dir != 200:
        return Response({"status": "error", "message": "Direction non trouvée"}, status=404)

    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": direction_id})
    if sc_update != 200:
        return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['direction_id'] = direction_id
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success", "code": "DIRECTION_REASSIGNED",
        "message": f"Direction changée de '{old_direction_nom or 'aucune'}' vers '{full_user['direction']['nom'] if full_user.get('direction') else direction_id}'",
        "data": {
            **full_user,
            "previous_direction_id":  old_direction_id,
            "previous_direction_nom": old_direction_nom,
            "assigned_by": {"id": admin.id, "name": getattr(admin, 'nom_complet', str(admin)), "role": getattr(admin, 'role', 'admin')},
            "timestamp": datetime.now().isoformat(),
        },
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

    user_data = _deserialize_user(user_response.get('user', {}))
    current_direction_id = user_data.get('direction_id')

    if not current_direction_id:
        return Response({"status": "error", "code": "NO_DIRECTION_ASSIGNED", "message": "Aucune direction affectée"}, status=400)

    direction_nom = "Inconnue"
    sc_dir, dir_resp = _call_juridique('get', f'/juridique/directions/{current_direction_id}/', token)
    if sc_dir == 200:
        direction_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_id": None})
    if sc_update != 200:
        return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['direction_id'] = None
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success", "code": "DIRECTION_REMOVED",
        "message": f"Direction '{direction_nom}' désaffectée de {full_user['nom_complet']}",
        "data": {
            **full_user,
            "removed_direction_id":  current_direction_id,
            "removed_direction_nom": direction_nom,
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


# ──────────────────────────────────────────────────────────────────────────────
# DIRECTIONS — Listes
# ──────────────────────────────────────────────────────────────────────────────

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_direction(request):
#     """GET /affectation/users/directeurs-direction/ — SANS direction"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'directeur_direction' and not u.get('direction_id')]
#     data = _build_full_users(cibles, token)

#     return Response({"status": "success", "code": "DIRECTEURS_DIRECTION_SANS", "message": f"{len(data)} directeur(s) de direction sans affectation", "data": {"count": len(data), "directeurs": data}}, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_directeurs_direction_affectes(request):
#     """GET /affectation/users/directeurs-direction/affectes/ — AVEC direction"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'directeur_direction' and u.get('direction_id')]
#     data = _build_full_users(cibles, token)

#     return Response({"status": "success", "code": "DIRECTEURS_DIRECTION_AVEC", "data": {"count": len(data), "directeurs": data}}, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsAdmin])
# def api_list_all_directeurs_direction(request):
#     """GET /affectation/users/directeurs-direction/all/ — TOUS"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'directeur_direction']
#     data = _build_full_users(cibles, token)

#     avec = len([x for x in data if x['has_direction']])
#     sans = len(data) - avec

#     return Response({"status": "success", "code": "ALL_DIRECTEURS_DIRECTION", "data": {"count": len(data), "statistics": {"with_direction": avec, "without_direction": sans}, "directeurs": data}}, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_direction(request):
    """GET /affectation/users/directeurs-direction/ — SANS direction"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "message": "Service Auth indisponible"},
            status=503
        )

    users_raw = users_response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_direction'
        and not u.get('direction_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "DIRECTEURS_DIRECTION_SANS",
        "message": f"{len(data)} directeur(s) de direction sans affectation",
        "data": {
            "count": len(data),
            "directeurs": data
        }
    }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_direction_affectes(request):
    """GET /affectation/users/directeurs-direction/affectes/ — AVEC direction"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "message": "Service Auth indisponible"},
            status=503
        )

    users_raw = users_response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_direction'
        and u.get('direction_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "DIRECTEURS_DIRECTION_AVEC",
        "data": {
            "count": len(data),
            "directeurs": data
        }
    }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_all_directeurs_direction(request):
    """GET /affectation/users/directeurs-direction/all/ — TOUS"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "message": "Service Auth indisponible"},
            status=503
        )

    users_raw = users_response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_direction'
    ]

    data = _build_full_users(cibles, token)

    avec = len([x for x in data if x.get('has_direction')])
    sans = len(data) - avec

    return Response({
        "status": "success",
        "code": "ALL_DIRECTEURS_DIRECTION",
        "data": {
            "count": len(data),
            "statistics": {
                "with_direction": avec,
                "without_direction": sans
            },
            "directeurs": data
        }
    }, status=200)

# ──────────────────────────────────────────────────────────────────────────────
# DÉPARTEMENTS — Helpers Auth
# ──────────────────────────────────────────────────────────────────────────────

def _call_auth_update_departement(user_id: int, departement_id, direction_id, token: str):
    base_url = get_auth_base_url()
    url = f"{base_url}/auth/users/{user_id}/update-departement/"
    headers = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.patch(url, headers=headers, json={"departement_id": departement_id, "direction_id": direction_id}, timeout=5)
        if resp.status_code == 200:
            return resp.status_code, resp.json()
        return resp.status_code, {"error": resp.text}
    except requests.RequestException as e:
        return 503, {"status": "error", "message": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# DÉPARTEMENTS — Assignation
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def assign_departement_to_user(request):
    """PATCH /affectation/assign-departement/"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user

    user_id = request.data.get('user_id')
    departement_id = request.data.get('departement_id')

    # ─────────────────────────────
    # VALIDATION
    # ─────────────────────────────
    if not user_id:
        return Response({
            "status": "error",
            "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)

    if not departement_id:
        return Response({
            "status": "error",
            "code": "MISSING_DEPARTEMENT_ID",
            "message": "departement_id est obligatoire."
        }, status=400)

    # ─────────────────────────────
    # DIRECTEUR MUST HAVE DIRECTION
    # ─────────────────────────────
    directeur_direction_id = getattr(directeur, 'direction_id', None)

    if not directeur_direction_id:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_NO_DIRECTION",
            "message": "Vous n'avez pas de direction associée."
        }, status=403)

    # ─────────────────────────────
    # GET USER
    # ─────────────────────────────
    sc, user_response = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} introuvable."
        }, status=404)

    user_data = _deserialize_user(
        user_response.get('user', {})
    )

    # ─────────────────────────────
    # ROLE CHECK
    # ─────────────────────────────
    if user_data.get('role') != 'responsable_departement':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": f"L'utilisateur doit être 'responsable_departement' (actuel: {user_data.get('role')})"
        }, status=400)

    # ─────────────────────────────
    # ALREADY ASSIGNED
    # ─────────────────────────────
    if user_data.get('departement_id'):

        existing_nom = "Inconnu"

        sc_ex, ex_resp = _call_juridique(
            'get',
            f'/juridique/departements/{user_data["departement_id"]}/',
            token
        )

        if sc_ex == 200:
            existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnu')

        return Response({
            "status": "error",
            "code": "ALREADY_ASSIGNED",
            "message": f"L'utilisateur a déjà un département: '{existing_nom}'",
            "suggestion": "Utilisez PUT /affectation/reassign-departement/ pour changer"
        }, status=400)

    # ─────────────────────────────
    # CHECK DEPARTEMENT EXISTS
    # ─────────────────────────────
    sc_dep, dep_resp = _call_juridique(
        'get',
        f'/juridique/departements/{departement_id}/',
        token
    )

    if sc_dep == 404:
        return Response({
            "status": "error",
            "code": "DEPARTEMENT_NOT_FOUND",
            "message": f"Département {departement_id} non trouvé."
        }, status=404)

    if sc_dep != 200:
        return Response({
            "status": "error",
            "code": "JURIDIQUE_SERVICE_ERROR",
            "message": "Service juridique indisponible"
        }, status=503)

    # ─────────────────────────────
    # CHECK DEPARTEMENT BELONGS TO DIRECTION
    # ─────────────────────────────
    departement_info = dep_resp.get('data', {})

    departement_direction_id = (
        departement_info.get('direction', {}).get('_id')
        if isinstance(departement_info.get('direction'), dict)
        else departement_info.get('direction')
    )

    if str(directeur_direction_id) != str(departement_direction_id):

        direction_nom = "Inconnue"

        sc_dir, dir_resp = _call_juridique(
            'get',
            f'/juridique/directions/{directeur_direction_id}/',
            token
        )

        if sc_dir == 200:
            direction_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

        return Response({
            "status": "error",
            "code": "DEPARTEMENT_NOT_IN_DIRECTION",
            "message": f"Ce département n'appartient pas à votre direction '{direction_nom}'."
        }, status=403)

    # ─────────────────────────────
    # UPDATE AUTH SERVICE
    # ─────────────────────────────
    sc_update, updated = _call_auth_update_departement(
        user_id,
        departement_id,
        directeur_direction_id,
        token
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "message": "Impossible de mettre à jour l'utilisateur.",
            "detail": updated
        }, status=sc_update)

    # ─────────────────────────────
    # VERIFY PERSISTENCE 🔥
    # ─────────────────────────────
    sc2, user_response2 = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc2 == 200:

        raw_user = user_response2.get('user', {})

        print("RAW USER =", raw_user)

        # VERIFY
        if (
            str(raw_user.get('departement_id')) != str(departement_id)
            or
            str(raw_user.get('direction_id')) != str(directeur_direction_id)
        ):
            return Response({
                "status": "error",
                "code": "UPDATE_NOT_PERSISTED",
                "message": "departement_id ou direction_id non sauvegardé côté Auth",
                "debug": {
                    "sent_departement_id": departement_id,
                    "received_departement_id": raw_user.get('departement_id'),

                    "sent_direction_id": directeur_direction_id,
                    "received_direction_id": raw_user.get('direction_id'),
                }
            }, status=500)

        # IMPORTANT ✅
        full_user = _build_full_user(
            raw_user,
            token
        )

    else:
        user_data['departement_id'] = departement_id
        user_data['direction_id'] = directeur_direction_id

        full_user = _build_full_user(
            user_data,
            token
        )

    # ─────────────────────────────
    # SUCCESS RESPONSE
    # ─────────────────────────────
    return Response({
        "status": "success",
        "code": "DEPARTEMENT_ASSIGNED",
        "message": f"Département affecté à {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "assigned_by": {
                "id": directeur.id,
                "name": getattr(directeur, 'nom_complet', str(directeur)),
                "role": directeur.role,
                "direction_id": directeur_direction_id,
            },
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def reassign_departement_to_user(request):
    """PUT /affectation/reassign-departement/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user

    user_id        = request.data.get('user_id')
    departement_id = request.data.get('departement_id')

    if not user_id or not departement_id:
        return Response({"status": "error", "message": "user_id et departement_id requis"}, status=400)

    directeur_direction_id = getattr(directeur, 'direction_id', None)
    if not directeur_direction_id:
        return Response({"status": "error", "code": "DIRECTEUR_NO_DIRECTION", "message": "Vous n'avez pas de direction associée."}, status=403)

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))

    if user_data['role'] != 'responsable_departement':
        return Response({"status": "error", "message": "L'utilisateur doit être 'responsable_departement'"}, status=400)

    old_departement_id  = user_data.get('departement_id')
    old_departement_nom = "Inconnu"
    if old_departement_id:
        sc_old, old_resp = _call_juridique('get', f'/juridique/departements/{old_departement_id}/', token)
        if sc_old == 200:
            old_departement_nom = old_resp.get('data', {}).get('nom', 'Inconnu')

    sc_dep, dep_resp = _call_juridique('get', f'/juridique/departements/{departement_id}/', token)
    if sc_dep != 200:
        return Response({"status": "error", "message": "Département non trouvé"}, status=404)

    departement_info = dep_resp.get('data', {})
    departement_direction_id = departement_info.get('direction', {}).get('_id') or departement_info.get('direction')
    if str(directeur_direction_id) != str(departement_direction_id):
        return Response({"status": "error", "code": "DEPARTEMENT_NOT_IN_DIRECTION", "message": "Ce département n'appartient pas à votre direction."}, status=403)

    sc_update, _ = _call_auth_update_departement(user_id, departement_id, directeur_direction_id, token)
    if sc_update != 200:
        return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['departement_id'] = departement_id
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success", "code": "DEPARTEMENT_REASSIGNED",
        "message": f"Département changé de '{old_departement_nom}' vers '{full_user['departement']['nom'] if full_user.get('departement') else departement_id}'",
        "data": {
            **full_user,
            "previous_departement_id":  old_departement_id,
            "previous_departement_nom": old_departement_nom,
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def remove_departement_from_user(request, user_id):
    """DELETE /affectation/users/<user_id>/remove-departement/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))
    current_departement_id = user_data.get('departement_id')

    if not current_departement_id:
        return Response({"status": "error", "message": "Aucun département affecté"}, status=400)

    departement_nom = "Inconnu"
    sc_dep, dep_resp = _call_juridique('get', f'/juridique/departements/{current_departement_id}/', token)
    if sc_dep == 200:
        departement_nom = dep_resp.get('data', {}).get('nom', 'Inconnu')

    sc_update, updated = _call_auth_update_departement(user_id, None, None, token)
    if sc_update != 200:
        return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)

    try:
        _call_auth('post', f'/auth/users/{user_id}/logout-all/', token)
    except Exception:
        pass

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['departement_id'] = None
        user_data['direction_id']   = None
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success", "code": "DEPARTEMENT_REMOVED",
        "message": f"Département '{departement_nom}' désaffecté de {full_user['nom_complet']}",
        "data": {
            **full_user,
            "removed_departement_id":  current_departement_id,
            "removed_departement_nom": departement_nom,
            "requires_relogin": True,
            "message_for_user": "Veuillez vous reconnecter pour que les changements prennent effet",
            "removed_by": {"id": directeur.id, "name": getattr(directeur, 'nom_complet', str(directeur)), "role": directeur.role},
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


# ──────────────────────────────────────────────────────────────────────────────
# DÉPARTEMENTS — Listes
# ──────────────────────────────────────────────────────────────────────────────

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def api_list_responsables_departement(request):
#     """GET /affectation/users/responsables-departement/ — SANS département"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'responsable_departement' and u.get('direction_id') is None and not u.get('departement_id')]
#     data = _build_full_users(cibles, token)

#     return Response({"status": "success", "code": "RESPONSABLES_SANS_DEPARTEMENT", "data": {"count": len(data), "responsables": data}}, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def api_list_responsables_departement_affectes(request):
#     """GET /affectation/users/responsables-departement/affectes/ — AVEC département"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
#     directeur_direction_id = getattr(directeur, 'direction_id', None)

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'responsable_departement' and u.get('departement_id')]
#     if directeur_direction_id:
#         cibles = [u for u in cibles if u.get('direction_id') == directeur_direction_id]

#     data = _build_full_users(cibles, token)

#     return Response({"status": "success", "code": "RESPONSABLES_AVEC_DEPARTEMENT", "data": {"count": len(data), "responsables": data}}, status=200)


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDirection])
# def api_list_all_responsables_departement(request):
#     """GET /affectation/users/responsables-departement/all/ — TOUS"""
#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user
#     directeur_direction_id = getattr(directeur, 'direction_id', None)

#     sc, users_response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

#     users = _deserialize_users(users_response.get('users', []))
#     cibles = [u for u in users if u['role'] == 'responsable_departement']
#     if directeur_direction_id:
#         cibles = [u for u in cibles if u.get('direction_id') == directeur_direction_id or u.get('direction_id') is None]

#     data = _build_full_users(cibles, token)

#     avec = len([x for x in data if x['has_departement']])
#     sans = len(data) - avec

#     return Response({
#         "status": "success", "code": "ALL_RESPONSABLES_DEPARTEMENT",
#         "data": {"count": len(data), "statistics": {"with_departement": avec, "without_departement": sans}, "responsables": data},
#     }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def api_list_responsables_departement(request):
    """GET /affectation/users/responsables-departement/ — SANS département"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

    users_raw = users_response.get('users', [])

    directeur_direction_id = getattr(request.user, 'direction_id', None)

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_departement'
        and not u.get('departement_id')
    ]

    # scope direction
    if directeur_direction_id:
        cibles = [
            u for u in cibles
            if u.get('direction_id') == directeur_direction_id
        ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "RESPONSABLES_SANS_DEPARTEMENT",
        "data": {
            "count": len(data),
            "responsables": data
        }
    }, status=200)

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def api_list_responsables_departement_affectes(request):
    """GET /affectation/users/responsables-departement/affectes/ — AVEC département"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

    users_raw = users_response.get('users', [])

    directeur_direction_id = getattr(request.user, 'direction_id', None)

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_departement'
        and u.get('departement_id')
    ]

    # scope direction
    if directeur_direction_id:
        cibles = [
            u for u in cibles
            if u.get('direction_id') == directeur_direction_id
        ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "RESPONSABLES_AVEC_DEPARTEMENT",
        "data": {
            "count": len(data),
            "responsables": data
        }
    }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDirection])
def api_list_all_responsables_departement(request):
    """GET /affectation/users/responsables-departement/all/ — TOUS"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Service Auth indisponible"}, status=503)

    users_raw = users_response.get('users', [])

    directeur_direction_id = getattr(request.user, 'direction_id', None)

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_departement'
    ]

    # scope direction
    if directeur_direction_id:
        cibles = [
            u for u in cibles
            if u.get('direction_id') == directeur_direction_id
            or u.get('direction_id') is None
        ]

    data = _build_full_users(cibles, token)

    avec = len([x for x in data if x.get('has_departement')])
    sans = len(data) - avec

    return Response({
        "status": "success",
        "code": "ALL_RESPONSABLES_DEPARTEMENT",
        "data": {
            "count": len(data),
            "statistics": {
                "with_departement": avec,
                "without_departement": sans
            },
            "responsables": data
        }
    }, status=200)

# ──────────────────────────────────────────────────────────────────────────────
# DIRECTION CENTRALE — Assignation
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def assign_direction_centrale_to_user(request):
    """PATCH /affectation/assign-direction-centrale/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id               = request.data.get('user_id')
    direction_centrale_id = request.data.get('direction_centrale_id')

    if not user_id:
        return Response({"status": "error", "code": "MISSING_USER_ID", "message": "user_id est obligatoire."}, status=400)
    if not direction_centrale_id:
        return Response({"status": "error", "code": "MISSING_DIRECTION_CENTRALE_ID", "message": "direction_centrale_id est obligatoire."}, status=400)

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))

    if user_data['role'] != 'directeur_centrale':
        return Response({"status": "error", "code": "INVALID_ROLE", "message": f"L'utilisateur doit être 'directeur_centrale' (actuel: {user_data['role']})"}, status=400)

    if user_data.get('direction_centrale_id'):
        existing_nom = "Inconnue"
        sc_ex, ex_resp = _call_juridique('get', f'/juridique/directions-centrales/{user_data["direction_centrale_id"]}/', token)
        if sc_ex == 200:
            existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')
        return Response({"status": "error", "code": "ALREADY_ASSIGNED", "message": "L'utilisateur a déjà une direction centrale affectée.", "data": {"existing_direction_centrale_id": user_data['direction_centrale_id'], "existing_direction_centrale_nom": existing_nom}}, status=400)

    sc_dir, dc_resp = _call_juridique('get', f'/juridique/directions-centrales/{direction_centrale_id}/', token)
    if sc_dir == 404:
        return Response({"status": "error", "code": "DIRECTION_CENTRALE_NOT_FOUND", "message": f"Direction centrale {direction_centrale_id} non trouvée."}, status=404)
    if sc_dir != 200:
        return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible"}, status=503)

    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_centrale_id": direction_centrale_id})
    if sc_update != 200:
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour"}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['direction_centrale_id'] = direction_centrale_id
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success", "code": "DIRECTION_CENTRALE_ASSIGNED",
        "message": f"Direction centrale affectée à {full_user['nom_complet']}.",
        "data": {
            **full_user,
            "assigned_by": {"id": admin.id, "name": getattr(admin, 'nom_complet', str(admin)), "role": getattr(admin, 'role', 'admin')},
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def reassign_direction_centrale_to_user(request):
    """PUT /affectation/reassign-direction-centrale/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    admin = request.user

    user_id               = request.data.get('user_id')
    direction_centrale_id = request.data.get('direction_centrale_id')

    if not user_id or not direction_centrale_id:
        return Response({"status": "error", "message": "user_id et direction_centrale_id requis"}, status=400)

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))

    if user_data['role'] != 'directeur_centrale':
        return Response({"status": "error", "message": "L'utilisateur doit être 'directeur_centrale'"}, status=400)

    old_dc_id  = user_data.get('direction_centrale_id')
    old_dc_nom = None
    if old_dc_id:
        sc_old, old_resp = _call_juridique('get', f'/juridique/directions-centrales/{old_dc_id}/', token)
        if sc_old == 200:
            old_dc_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

    sc_dir, dc_resp = _call_juridique('get', f'/juridique/directions-centrales/{direction_centrale_id}/', token)
    if sc_dir != 200:
        return Response({"status": "error", "message": "Direction centrale non trouvée"}, status=404)

    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_centrale_id": direction_centrale_id})
    if sc_update != 200:
        return Response({"status": "error", "message": "Mise à jour échouée"}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['direction_centrale_id'] = direction_centrale_id
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success", "code": "DIRECTION_CENTRALE_REASSIGNED",
        "message": f"Direction centrale changée de '{old_dc_nom or 'aucune'}' vers '{full_user['direction_centrale']['nom'] if full_user.get('direction_centrale') else direction_centrale_id}'",
        "data": {
            **full_user,
            "previous_direction_centrale_id":  old_dc_id,
            "previous_direction_centrale_nom": old_dc_nom,
            "assigned_by": {"id": admin.id, "name": getattr(admin, 'nom_complet', str(admin)), "role": getattr(admin, 'role', 'admin')},
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def remove_direction_centrale_from_user(request, user_id):
    """DELETE /affectation/users/<user_id>/remove-direction-centrale/"""
    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    user_data = _deserialize_user(user_response.get('user', {}))
    current_dc_id = user_data.get('direction_centrale_id')

    if not current_dc_id:
        return Response({"status": "error", "code": "NO_DIRECTION_CENTRALE_ASSIGNED", "message": "Aucune direction centrale affectée"}, status=400)

    dc_nom = "Inconnue"
    sc_dir, dc_resp = _call_juridique('get', f'/juridique/directions-centrales/{current_dc_id}/', token)
    if sc_dir == 200:
        dc_nom = dc_resp.get('data', {}).get('nom', 'Inconnue')

    sc_update, _ = _call_auth('patch', f'/auth/users/{user_id}/update/', token, json={"direction_centrale_id": None})
    if sc_update != 200:
        return Response({"status": "error", "message": "Suppression échouée"}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(_deserialize_user(user_response2.get('user', {})), token)
    else:
        user_data['direction_centrale_id'] = None
        full_user = _build_full_user(user_data, token)

    return Response({
        "status": "success", "code": "DIRECTION_CENTRALE_REMOVED",
        "message": f"Direction centrale '{dc_nom}' désaffectée de {full_user['nom_complet']}",
        "data": {
            **full_user,
            "removed_direction_centrale_id":  current_dc_id,
            "removed_direction_centrale_nom": dc_nom,
            "timestamp": datetime.now().isoformat(),
        },
    }, status=200)


# ──────────────────────────────────────────────────────────────────────────────
# DIRECTION CENTRALE — Listes
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_centrale(request):
    """GET /affectation/users/directeurs-centrale/ — SANS direction centrale"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "message": "Service Auth indisponible"},
            status=503
        )

    users_raw = users_response.get('users', [])

    # ✅ FILTER RAW DATA FIRST
    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_centrale'
        and not u.get('direction_centrale_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "DIRECTEURS_CENTRALE_SANS",
        "message": f"{len(data)} directeur(s) centrale sans affectation",
        "data": {
            "count": len(data),
            "directeurs": data
        }
    }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_directeurs_centrale_affectes(request):
    """GET /affectation/users/directeurs-centrale/affectes/ — AVEC direction centrale"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "message": "Service Auth indisponible"},
            status=503
        )

    users_raw = users_response.get('users', [])

    # ✅ FILTER RAW DATA FIRST
    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_centrale'
        and u.get('direction_centrale_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "code": "DIRECTEURS_CENTRALE_AVEC",
        "message": f"{len(data)} directeur(s) centrale avec affectation",
        "data": {
            "count": len(data),
            "directeurs": data
        }
    }, status=200)
@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsAdmin])
def api_list_all_directeurs_centrale(request):
    """GET /affectation/users/directeurs-centrale/all/ — TOUS"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    show_inactive = request.query_params.get('show_inactive', '').lower() == 'true'

    sc, users_response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response(
            {"status": "error", "message": "Service Auth indisponible"},
            status=503
        )

    users_raw = users_response.get('users', [])

    # ✅ FILTER RAW DATA FIRST
    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_centrale'
    ]

    # optional filter
    if not show_inactive:
        cibles = [
            u for u in cibles
            if u.get('is_active', True)
        ]

    data = _build_full_users(cibles, token)

    total = len(data)
    avec = len([x for x in data if x.get('has_direction_centrale')])
    sans = total - avec
    actifs = len([x for x in data if x.get('is_active')])

    return Response({
        "status": "success",
        "code": "ALL_DIRECTEURS_CENTRALE",
        "message": f"Total: {total} directeur(s) centrale",
        "data": {
            "count": total,
            "statistics": {
                "with_direction_centrale": avec,
                "without_direction_centrale": sans,
                "active": actifs,
                "inactive": total - actifs,
            },
            "directeurs": data,
        },
        "timestamp": datetime.now().isoformat(),
    }, status=200)

# =========================================================
# ASSIGN DIRECTION ACTIVITE
# Vice Président -> Directeur Direction Activité
# =========================================================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def assign_direction_activite_to_user(request):
#     """
#     PATCH /affectation/assign-direction-activite/

#     Body:
#     {
#         "user_id": 12,
#         "direction_activite_id": "682ab123456789abcdef0123"
#     }

#     Remplit automatiquement:
#     - direction_activite_id
#     - activite_id
#     """

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     vice_president = request.user

#     user_id = request.data.get('user_id')
#     direction_activite_id = request.data.get('direction_activite_id')

#     # =====================================================
#     # VALIDATION
#     # =====================================================

#     if not user_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_USER_ID",
#             "message": "user_id est obligatoire."
#         }, status=400)

#     if not direction_activite_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_DIRECTION_ACTIVITE_ID",
#             "message": "direction_activite_id est obligatoire."
#         }, status=400)

#     # =====================================================
#     # CHECK USER
#     # =====================================================

#     sc, user_response = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur {user_id} introuvable."
#         }, status=404)

#     user_data = _deserialize_user(
#         user_response.get('user', {})
#     )

#     # =====================================================
#     # ROLE CHECK
#     # =====================================================

#     if user_data.get('role') != 'directeur_direction_activite':
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": (
#                 "L'utilisateur doit être "
#                 "'directeur_direction_activite'"
#             )
#         }, status=400)

#     # =====================================================
#     # ALREADY ASSIGNED
#     # =====================================================

#     if user_data.get('direction_activite_id'):

#         return Response({
#             "status": "error",
#             "code": "ALREADY_ASSIGNED",
#             "message": (
#                 "Utilisateur déjà affecté "
#                 "à une direction activité."
#             )
#         }, status=400)

#     # =====================================================
#     # GET DIRECTION ACTIVITE
#     # =====================================================

#     sc_dir, dir_resp = _call_juridique(
#         'get',
#         f'/juridique/direction_activite/{direction_activite_id}/',
#         token
#     )

#     if sc_dir == 404:
#         return Response({
#             "status": "error",
#             "code": "DIRECTION_ACTIVITE_NOT_FOUND",
#             "message": "Direction activité introuvable."
#         }, status=404)

#     if sc_dir != 200:
#         return Response({
#             "status": "error",
#             "code": "JURIDIQUE_SERVICE_ERROR",
#             "message": "Service juridique indisponible."
#         }, status=503)

#     direction_activite_data = dir_resp.get('data', {})

#     # =====================================================
#     # GET ACTIVITE ID
#     # =====================================================

#     activite_id = (
#         direction_activite_data.get('activite', {})
#         .get('_id')
#     )

#     if not activite_id:
#         activite_id = direction_activite_data.get('activite')

#     if not activite_id:
#         return Response({
#             "status": "error",
#             "code": "ACTIVITE_NOT_FOUND_IN_DIRECTION_ACTIVITE",
#             "message": (
#                 "Impossible de récupérer activite_id "
#                 "depuis direction activité."
#             )
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={
#             "direction_activite_id": direction_activite_id,
#             "activite_id": activite_id
#         }
#     )

#     if sc_update != 200:
#         return Response({
#             "status": "error",
#             "code": "UPDATE_FAILED",
#             "message": "Impossible de mettre à jour l'utilisateur.",
#             "detail": updated
#         }, status=sc_update)

#     # =====================================================
#     # VERIFY SAVE
#     # =====================================================

#     sc_check, check_resp = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc_check != 200:
#         return Response({
#             "status": "error",
#             "code": "POST_CHECK_FAILED",
#             "message": "Impossible de vérifier la mise à jour."
#         }, status=503)

#     raw_user = check_resp.get('user', {})

#     if (
#         str(raw_user.get('direction_activite_id'))
#         != str(direction_activite_id)
#     ):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": (
#                 "direction_activite_id "
#                 "non sauvegardé"
#             )
#         }, status=500)

#     if str(raw_user.get('activite_id')) != str(activite_id):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "activite_id non sauvegardé"
#         }, status=500)

#     # =====================================================
#     # BUILD USER
#     # =====================================================

#     full_user = _build_full_user(
#         _deserialize_user(raw_user),
#         token
#     )

#     # =====================================================
#     # SUCCESS
#     # =====================================================

#     return Response({
#         "status": "success",
#         "code": "DIRECTION_ACTIVITE_ASSIGNED",
#         "message": (
#             f"Direction activité affectée "
#             f"à {full_user.get('nom_complet')}."
#         ),
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id": vice_president.id,
#                 "name": getattr(
#                     vice_president,
#                     'nom_complet',
#                     str(vice_president)
#                 ),
#                 "role": vice_president.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)
@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def assign_direction_activite_to_user(request):
    """
    PATCH /affectation/assign-direction-activite/

    Body:
    {
        "user_id": 9,
        "direction_activite_id": "682ab123456789abcdef1111"
    }

    Remplit automatiquement :
    - direction_activite_id
    - activite_id
    """

    token = request.headers.get(
        'Authorization',
        ''
    ).split(' ', 1)[1].strip()

    vice_president = request.user

    user_id = request.data.get('user_id')
    direction_activite_id = request.data.get(
        'direction_activite_id'
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not user_id:
        return Response({
            "status": "error",
            "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)

    if not direction_activite_id:
        return Response({
            "status": "error",
            "code": "MISSING_DIRECTION_ACTIVITE_ID",
            "message": (
                "direction_activite_id est obligatoire."
            )
        }, status=400)

    # =====================================================
    # GET USER
    # =====================================================

    sc, user_response = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": (
                f"Utilisateur {user_id} introuvable."
            )
        }, status=404)

    raw_user = user_response.get('user', {})

    user_data = _deserialize_user(raw_user)

    # =====================================================
    # ROLE CHECK
    # =====================================================

    if (
        user_data.get('role')
        != 'directeur_direction_activite'
    ):
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": (
                "L'utilisateur doit être "
                "'directeur_direction_activite'"
            )
        }, status=400)

    # =====================================================
    # ALREADY ASSIGNED
    # =====================================================

    if user_data.get('direction_activite_id'):

        existing_nom = "Inconnue"

        sc_ex, ex_resp = _call_juridique(
            'get',
            (
                f'/juridique/direction_activite/'
                f'{user_data["direction_activite_id"]}/'
            ),
            token
        )

        if sc_ex == 200:
            existing_nom = (
                ex_resp.get('data', {})
                .get('nom', 'Inconnue')
            )

        return Response({
            "status": "error",
            "code": "ALREADY_ASSIGNED",
            "message": (
                "Utilisateur déjà affecté "
                "à une direction activité."
            ),
            "data": {
                "existing_direction_activite_id":
                    user_data.get(
                        'direction_activite_id'
                    ),
                "existing_direction_activite_nom":
                    existing_nom
            }
        }, status=400)

    # =====================================================
    # GET DIRECTION ACTIVITE
    # =====================================================

    sc_dir, dir_resp = _call_juridique(
        'get',
        (
            f'/juridique/direction_activite/'
            f'{direction_activite_id}/'
        ),
        token
    )

    if sc_dir == 404:
        return Response({
            "status": "error",
            "code": "DIRECTION_ACTIVITE_NOT_FOUND",
            "message": (
                "Direction activité introuvable."
            )
        }, status=404)

    if sc_dir != 200:
        return Response({
            "status": "error",
            "code": "JURIDIQUE_SERVICE_ERROR",
            "message": (
                "Service juridique indisponible."
            )
        }, status=503)

    direction_activite_data = dir_resp.get(
        'data',
        {}
    )

    # =====================================================
    # GET ACTIVITE ID
    # =====================================================

    activite_data = (
        direction_activite_data.get('activite')
    )

    activite_id = None

    # Cas:
    # "activite": { "_id": "xxx" }

    if isinstance(activite_data, dict):
        activite_id = activite_data.get('_id')

    # Cas:
    # "activite": "xxx"

    elif isinstance(activite_data, str):
        activite_id = activite_data

    if not activite_id:
        return Response({
            "status": "error",
            "code": (
                "ACTIVITE_NOT_FOUND_IN_DIRECTION_ACTIVITE"
            ),
            "message": (
                "Impossible de récupérer activite_id."
            ),
            "debug": {
                "direction_activite":
                    direction_activite_data
            }
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "direction_activite_id":
                direction_activite_id,

            "activite_id":
                activite_id
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "message": (
                "Impossible de mettre à jour."
            ),
            "detail": updated
        }, status=sc_update)

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    sc_check, check_resp = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc_check != 200:
        return Response({
            "status": "error",
            "code": "POST_CHECK_FAILED",
            "message": (
                "Impossible de vérifier "
                "la sauvegarde."
            )
        }, status=503)

    raw_user = check_resp.get('user', {})

    print("RAW USER =", raw_user)

    # =====================================================
    # VERIFY direction_activite_id
    # =====================================================

    if (
        str(raw_user.get('direction_activite_id'))
        != str(direction_activite_id)
    ):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": (
                "direction_activite_id "
                "non sauvegardé"
            ),
            "debug": {
                "sent":
                    direction_activite_id,

                "received":
                    raw_user.get(
                        'direction_activite_id'
                    )
            }
        }, status=500)

    # =====================================================
    # VERIFY activite_id
    # =====================================================

    if (
        str(raw_user.get('activite_id'))
        != str(activite_id)
    ):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": (
                "activite_id non sauvegardé"
            ),
            "debug": {
                "sent": activite_id,
                "received":
                    raw_user.get('activite_id')
            }
        }, status=500)

    # =====================================================
    # BUILD USER
    # =====================================================

    full_user = _build_full_user(
        raw_user,
        token
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    return Response({
        "status": "success",
        "code": "DIRECTION_ACTIVITE_ASSIGNED",
        "message": (
            f"Direction activité affectée "
            f"à {full_user.get('nom_complet')}."
        ),
        "data": {
            **full_user,

            "assigned_by": {
                "id": vice_president.id,

                "name": getattr(
                    vice_president,
                    'nom_complet',
                    str(vice_president)
                ),

                "role": vice_president.role,
            },

            "timestamp":
                datetime.now().isoformat(),
        }
    }, status=200)
# =========================================================
# REASSIGN DIRECTION ACTIVITE
# =========================================================

@api_view(['PUT', 'PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def reassign_direction_activite_to_user(request):
    """
    PATCH /affectation/reassign-direction-activite/

    Body:
    {
        "user_id": 9,
        "direction_activite_id": "682ab123456789abcdef1111"
    }
    """

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    vice_president = request.user

    user_id = request.data.get('user_id')
    direction_activite_id = request.data.get('direction_activite_id')

    # =====================================================
    # VALIDATION
    # =====================================================

    if not user_id:
        return Response({
            "status": "error",
            "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)

    if not direction_activite_id:
        return Response({
            "status": "error",
            "code": "MISSING_DIRECTION_ACTIVITE_ID",
            "message": "direction_activite_id est obligatoire."
        }, status=400)

    # =====================================================
    # GET USER
    # =====================================================

    sc, user_response = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": "Utilisateur introuvable."
        }, status=404)

    user_data = _deserialize_user(
        user_response.get('user', {})
    )

    # =====================================================
    # ROLE CHECK
    # =====================================================

    if user_data.get('role') != 'directeur_direction_activite':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": (
                "L'utilisateur doit être "
                "'directeur_direction_activite'"
            )
        }, status=400)

    # =====================================================
    # GET DIRECTION ACTIVITE
    # =====================================================

    sc_dir, dir_resp = _call_juridique(
        'get',
        f'/juridique/direction-activite/{direction_activite_id}/',
        token
    )

    if sc_dir == 404:
        return Response({
            "status": "error",
            "code": "DIRECTION_ACTIVITE_NOT_FOUND",
            "message": "Direction activité introuvable."
        }, status=404)

    if sc_dir != 200:
        return Response({
            "status": "error",
            "code": "JURIDIQUE_SERVICE_ERROR",
            "message": "Service juridique indisponible."
        }, status=503)

    direction_activite_data = dir_resp.get('data', {})

    # =====================================================
    # GET ACTIVITE ID
    # =====================================================

    activite_field = direction_activite_data.get('activite')

    if isinstance(activite_field, dict):
        activite_id = activite_field.get('_id')
    else:
        activite_id = activite_field

    if not activite_id:
        return Response({
            "status": "error",
            "code": "ACTIVITE_NOT_FOUND",
            "message": "Impossible de récupérer activite_id."
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "direction_activite_id": direction_activite_id,
            "activite_id": activite_id
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "message": "Impossible de mettre à jour.",
            "detail": updated
        }, status=sc_update)

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    sc_check, check_resp = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc_check != 200:
        return Response({
            "status": "error",
            "code": "POST_CHECK_FAILED",
            "message": "Impossible de vérifier."
        }, status=503)

    raw_user = check_resp.get('user', {})

    if (
        str(raw_user.get('direction_activite_id'))
        != str(direction_activite_id)
    ):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "direction_activite_id non sauvegardé"
        }, status=500)

    if str(raw_user.get('activite_id')) != str(activite_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "activite_id non sauvegardé"
        }, status=500)

    # =====================================================
    # BUILD USER
    # =====================================================

    full_user = _build_full_user(
        _deserialize_user(raw_user),
        token
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    return Response({
        "status": "success",
        "code": "DIRECTION_ACTIVITE_REASSIGNED",
        "message": (
            f"Direction activité réaffectée "
            f"à {full_user.get('nom_complet')}."
        ),
        "data": {
            **full_user,
            "assigned_by": {
                "id": vice_president.id,
                "name": getattr(
                    vice_president,
                    'nom_complet',
                    str(vice_president)
                ),
                "role": vice_president.role,
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# REMOVE DIRECTION ACTIVITE
# =========================================================

@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def remove_direction_activite_from_user(request, user_id):

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    # =====================================================
    # GET USER
    # =====================================================

    sc, user_response = _call_auth(
        'get',
        f'/auth/users/{user_id}/',
        token
    )

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": "Utilisateur introuvable."
        }, status=404)

    user_data = _deserialize_user(
        user_response.get('user', {})
    )

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "direction_activite_id": None,
            "activite_id": None
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "REMOVE_FAILED",
            "message": "Impossible de supprimer.",
            "detail": updated
        }, status=sc_update)

    return Response({
        "status": "success",
        "code": "DIRECTION_ACTIVITE_REMOVED",
        "message": "Direction activité supprimée avec succès.",
        "data": {
            "user_id": user_id,
            "nom_complet": user_data.get('nom_complet')
        }
    }, status=200)


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def api_list_directeurs_direction_activite(request):
    """Directeurs direction activité NON affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "message": "Impossible de récupérer utilisateurs."
        }, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_direction_activite'
        and not u.get('direction_activite_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "count": len(data),
        "data": data
    })


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def api_list_directeurs_direction_activite_affectes(request):
    """Directeurs direction activité affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "message": "Impossible de récupérer utilisateurs."
        }, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_direction_activite'
        and u.get('direction_activite_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "count": len(data),
        "data": data
    })


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def api_list_all_directeurs_direction_activite(request):
    """Tous les directeurs direction activité"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "message": "Impossible de récupérer utilisateurs."
        }, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_direction_activite'
    ]

    data = _build_full_users(cibles, token)

    total = len(data)
    avec = len([x for x in data if x.get('has_direction_activite')])
    sans = total - avec
    actifs = len([x for x in data if x.get('is_active')])

    return Response({
        "status": "success",
        "count": total,
        "statistics": {
            "with_direction_activite": avec,
            "without_direction_activite": sans,
            "active": actifs,
            "inactive": total - actifs,
        },
        "data": data
    })


# =========================================================
# ASSIGN DIVISION ACTIVITE
# Vice Président -> Directeur Division Activité
# =========================================================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def assign_division_activite_to_user(request):
#     """
#     PATCH /affectation/assign-division-activite/

#     Body:
#     {
#         "user_id": 15,
#         "division_activite_id": "682ab123456789abcdef9999"
#     }

#     Remplit automatiquement:
#     - division_activite_id
#     - activite_id
#     """

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     vice_president = request.user

#     user_id = request.data.get('user_id')
#     division_activite_id = request.data.get('division_activite_id')

#     # =====================================================
#     # VALIDATION
#     # =====================================================

#     if not user_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_USER_ID",
#             "message": "user_id est obligatoire."
#         }, status=400)

#     if not division_activite_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_DIVISION_ACTIVITE_ID",
#             "message": "division_activite_id est obligatoire."
#         }, status=400)

#     # =====================================================
#     # GET USER
#     # =====================================================

#     sc, user_response = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur {user_id} introuvable."
#         }, status=404)

#     user_data = _deserialize_user(
#         user_response.get('user', {})
#     )

#     # =====================================================
#     # ROLE CHECK
#     # =====================================================

#     if user_data.get('role') != 'directeur_division_activite':
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": (
#                 "L'utilisateur doit être "
#                 "'directeur_division_activite'"
#             )
#         }, status=400)

#     # =====================================================
#     # ALREADY ASSIGNED
#     # =====================================================

#     if user_data.get('division_activite_id'):

#         return Response({
#             "status": "error",
#             "code": "ALREADY_ASSIGNED",
#             "message": (
#                 "Utilisateur déjà affecté "
#                 "à une division activité."
#             )
#         }, status=400)

#     # =====================================================
#     # GET DIVISION ACTIVITE
#     # =====================================================

#     sc_div, div_resp = _call_juridique(
#         'get',
#         f'/juridique/divisions-activite/{division_activite_id}/',
#         token
#     )

#     if sc_div == 404:
#         return Response({
#             "status": "error",
#             "code": "DIVISION_ACTIVITE_NOT_FOUND",
#             "message": "Division activité introuvable."
#         }, status=404)

#     if sc_div != 200:
#         return Response({
#             "status": "error",
#             "code": "JURIDIQUE_SERVICE_ERROR",
#             "message": "Service juridique indisponible."
#         }, status=503)

#     division_activite_data = div_resp.get('data', {})

#     # =====================================================
#     # GET ACTIVITE ID
#     # =====================================================

#     activite_id = (
#         division_activite_data.get('activite', {})
#         .get('_id')
#     )

#     if not activite_id:
#         activite_id = division_activite_data.get('activite')

#     if not activite_id:
#         return Response({
#             "status": "error",
#             "code": "ACTIVITE_NOT_FOUND_IN_DIVISION_ACTIVITE",
#             "message": (
#                 "Impossible de récupérer activite_id."
#             )
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={
#             "division_activite_id": division_activite_id,
#             "activite_id": activite_id
#         }
#     )

#     if sc_update != 200:
#         return Response({
#             "status": "error",
#             "code": "UPDATE_FAILED",
#             "message": "Impossible de mettre à jour.",
#             "detail": updated
#         }, status=sc_update)

#     # =====================================================
#     # VERIFY SAVE
#     # =====================================================

#     sc_check, check_resp = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc_check != 200:
#         return Response({
#             "status": "error",
#             "code": "POST_CHECK_FAILED",
#             "message": "Impossible de vérifier."
#         }, status=503)

#     raw_user = check_resp.get('user', {})

#     if (
#         str(raw_user.get('division_activite_id'))
#         != str(division_activite_id)
#     ):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "division_activite_id non sauvegardé"
#         }, status=500)

#     if str(raw_user.get('activite_id')) != str(activite_id):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "activite_id non sauvegardé"
#         }, status=500)

#     # =====================================================
#     # BUILD USER
#     # =====================================================

#     full_user = _build_full_user(
#         _deserialize_user(raw_user),
#         token
#     )

#     # =====================================================
#     # SUCCESS
#     # =====================================================

#     return Response({
#         "status": "success",
#         "code": "DIVISION_ACTIVITE_ASSIGNED",
#         "message": (
#             f"Division activité affectée "
#             f"à {full_user.get('nom_complet')}."
#         ),
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id": vice_president.id,
#                 "name": getattr(
#                     vice_president,
#                     'nom_complet',
#                     str(vice_president)
#                 ),
#                 "role": vice_president.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)

# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def reassign_division_activite_to_user(request):
#     """
#     PUT /affectation/reassign-division-activite/

#     Body:
#     {
#         "user_id": 9,
#         "division_activite_id": "682ab123456789abcdef9999"
#     }
#     """

#     token = request.headers.get(
#         'Authorization',
#         ''
#     ).split(' ', 1)[1].strip()

#     vice_president = request.user

#     user_id = request.data.get('user_id')
#     division_activite_id = request.data.get(
#         'division_activite_id'
#     )

#     # =====================================================
#     # VALIDATION
#     # =====================================================

#     if not user_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_USER_ID",
#             "message": "user_id est obligatoire."
#         }, status=400)

#     if not division_activite_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_DIVISION_ACTIVITE_ID",
#             "message": (
#                 "division_activite_id est obligatoire."
#             )
#         }, status=400)

#     # =====================================================
#     # GET USER
#     # =====================================================

#     sc, user_response = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": (
#                 f"Utilisateur {user_id} introuvable."
#             )
#         }, status=404)

#     raw_user = user_response.get('user', {})

#     user_data = _deserialize_user(raw_user)

#     # =====================================================
#     # ROLE CHECK
#     # =====================================================

#     if (
#         user_data.get('role')
#         != 'directeur_division_activite'
#     ):
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": (
#                 "L'utilisateur doit être "
#                 "'directeur_division_activite'"
#             )
#         }, status=400)

#     # =====================================================
#     # GET DIVISION ACTIVITE
#     # =====================================================

#     sc_div, div_resp = _call_juridique(
#         'get',
#         (
#             f'/juridique/divisions-activite/'
#             f'{division_activite_id}/'
#         ),
#         token
#     )

#     if sc_div == 404:
#         return Response({
#             "status": "error",
#             "code": "DIVISION_ACTIVITE_NOT_FOUND",
#             "message": (
#                 "Division activité introuvable."
#             )
#         }, status=404)

#     if sc_div != 200:
#         return Response({
#             "status": "error",
#             "code": "JURIDIQUE_SERVICE_ERROR",
#             "message": (
#                 "Service juridique indisponible."
#             )
#         }, status=503)

#     division_activite_data = div_resp.get(
#         'data',
#         {}
#     )

#     # =====================================================
#     # GET ACTIVITE ID
#     # =====================================================

#     activite_data = (
#         division_activite_data.get('activite')
#     )

#     activite_id = None

#     if isinstance(activite_data, dict):
#         activite_id = activite_data.get('_id')

#     elif isinstance(activite_data, str):
#         activite_id = activite_data

#     if not activite_id:
#         return Response({
#             "status": "error",
#             "code":
#                 "ACTIVITE_NOT_FOUND_IN_DIVISION_ACTIVITE",
#             "message":
#                 "Impossible de récupérer activite_id."
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={
#             "division_activite_id":
#                 division_activite_id,

#             "activite_id":
#                 activite_id
#         }
#     )

#     if sc_update != 200:
#         return Response({
#             "status": "error",
#             "code": "UPDATE_FAILED",
#             "message":
#                 "Impossible de mettre à jour.",
#             "detail": updated
#         }, status=sc_update)

#     # =====================================================
#     # GET UPDATED USER
#     # =====================================================

#     sc2, user_response2 = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc2 != 200:
#         return Response({
#             "status": "error",
#             "code": "POST_CHECK_FAILED",
#             "message":
#                 "Impossible de récupérer utilisateur."
#         }, status=503)

#     raw_user = user_response2.get('user', {})

#     full_user = _build_full_user(
#         raw_user,
#         token
#     )

#     # =====================================================
#     # SUCCESS
#     # =====================================================

#     return Response({
#         "status": "success",
#         "code": "DIVISION_ACTIVITE_REASSIGNED",
#         "message": (
#             f"Division activité réaffectée "
#             f"à {full_user.get('nom_complet')}."
#         ),
#         "data": {
#             **full_user,

#             "assigned_by": {
#                 "id": vice_president.id,

#                 "name": getattr(
#                     vice_president,
#                     'nom_complet',
#                     str(vice_president)
#                 ),

#                 "role": vice_president.role,
#             },

#             "timestamp":
#                 datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REMOVE DIVISION ACTIVITE
# # =========================================================

# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def remove_division_activite_from_user(
#     request,
#     user_id
# ):
#     """
#     DELETE
#     /affectation/users/<id>/remove-division-activite/
#     """

#     token = request.headers.get(
#         'Authorization',
#         ''
#     ).split(' ', 1)[1].strip()

#     # =====================================================
#     # GET USER
#     # =====================================================

#     sc, user_response = _call_auth(
#         'get',
#         f'/auth/users/{user_id}/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message":
#                 f"Utilisateur {user_id} introuvable."
#         }, status=404)

#     raw_user = user_response.get('user', {})

#     user_data = _deserialize_user(raw_user)

#     # =====================================================
#     # CHECK ASSIGNMENT
#     # =====================================================

#     if not user_data.get('division_activite_id'):
#         return Response({
#             "status": "error",
#             "code": "NO_DIVISION_ACTIVITE",
#             "message":
#                 "Utilisateur sans division activité."
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={
#             "division_activite_id": None,
#             "activite_id": None
#         }
#     )

#     if sc_update != 200:
#         return Response({
#             "status": "error",
#             "code": "UPDATE_FAILED",
#             "message":
#                 "Impossible de supprimer.",
#             "detail": updated
#         }, status=sc_update)

#     return Response({
#         "status": "success",
#         "code": "DIVISION_ACTIVITE_REMOVED",
#         "message":
#             "Division activité supprimée."
#     }, status=200)


# # =========================================================
# # LIST DIRECTEURS DIVISION ACTIVITE
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def api_list_directeurs_division_activite(
#     request
# ):
#     """
#     Utilisateurs avec rôle directeur_division_activite
#     NON affectés
#     """

#     token = request.headers.get(
#         'Authorization',
#         ''
#     ).split(' ', 1)[1].strip()

#     sc, response = _call_auth(
#         'get',
#         '/auth/users/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "AUTH_SERVICE_ERROR",
#             "message":
#                 "Impossible de récupérer utilisateurs."
#         }, status=503)

#     users = response.get('users', [])

#     filtered = []

#     for user in users:

#         if (
#             user.get('role')
#             == 'directeur_division_activite'
#             and not user.get('division_activite_id')
#         ):
#             filtered.append(user)

#     return Response({
#         "status": "success",
#         "count": len(filtered),
#         "data": filtered
#     })


# # =========================================================
# # LIST DIRECTEURS DIVISION ACTIVITE AFFECTES
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def api_list_directeurs_division_activite_affectes(
#     request
# ):
#     """
#     Directeurs division activité affectés
#     """

#     token = request.headers.get(
#         'Authorization',
#         ''
#     ).split(' ', 1)[1].strip()

#     sc, response = _call_auth(
#         'get',
#         '/auth/users/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "AUTH_SERVICE_ERROR",
#             "message":
#                 "Impossible de récupérer utilisateurs."
#         }, status=503)

#     users = response.get('users', [])

#     filtered = []

#     for user in users:

#         if (
#             user.get('role')
#             == 'directeur_division_activite'
#             and user.get('division_activite_id')
#         ):
#             filtered.append(user)

#     return Response({
#         "status": "success",
#         "count": len(filtered),
#         "data": filtered
#     })


# # =========================================================
# # LIST ALL DIRECTEURS DIVISION ACTIVITE
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def api_list_all_directeurs_division_activite(
#     request
# ):
#     """
#     Tous les directeurs division activité
#     """

#     token = request.headers.get(
#         'Authorization',
#         ''
#     ).split(' ', 1)[1].strip()

#     sc, response = _call_auth(
#         'get',
#         '/auth/users/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "AUTH_SERVICE_ERROR",
#             "message":
#                 "Impossible de récupérer utilisateurs."
#         }, status=503)

#     users = response.get('users', [])

#     filtered = []

#     for user in users:

#         if (
#             user.get('role')
#             == 'directeur_division_activite'
#         ):
#             filtered.append(user)

#     return Response({
#         "status": "success",
#         "count": len(filtered),
#         "data": filtered
#     })
# # =========================================================
# # LISTE DIRECTEURS DIVISION ACTIVITE AFFECTES
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsVicePresedent])
# def api_list_directeurs_division_activite_affectes(request):

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, users_response = _call_auth(
#         'get',
#         '/auth/users/',
#         token
#     )

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "message": "Service Auth indisponible"
#         }, status=503)

#     users = _deserialize_users(
#         users_response.get('users', [])
#     )

#     cibles = [
#         u for u in users
#         if u['role'] == 'directeur_division_activite'
#         and u.get('division_activite_id')
#     ]

#     data = _build_full_users(cibles, token)

#     return Response({
#         "status": "success",
#         "code": "DIRECTEURS_DIVISION_ACTIVITE_AVEC",
#         "message": (
#             f"{len(data)} directeur(s) division activité affecté(s)"
#         ),
#         "data": {
#             "count": len(data),
#             "directeurs": data
#         }
#     }, status=200)

# =========================================================
# ASSIGN DIVISION ACTIVITE
# =========================================================

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def assign_division_activite_to_user(request):
    """
    PATCH /affectation/assign-division-activite/

    Body:
    {
        "user_id": 15,
        "division_activite_id": "682ab123456789abcdef9999"
    }
    """

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    vice_president = request.user

    user_id = request.data.get('user_id')
    division_activite_id = request.data.get('division_activite_id')

    # =====================================================
    # VALIDATION
    # =====================================================

    if not user_id:
        return Response({
            "status": "error",
            "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)

    if not division_activite_id:
        return Response({
            "status": "error",
            "code": "MISSING_DIVISION_ACTIVITE_ID",
            "message": "division_activite_id est obligatoire."
        }, status=400)

    # =====================================================
    # GET USER
    # =====================================================

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} introuvable."
        }, status=404)

    raw_user = user_response.get('user', {})
    user_data = _deserialize_user(raw_user)

    # =====================================================
    # ROLE CHECK
    # =====================================================

    if user_data.get('role') != 'directeur_division_activite':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": "L'utilisateur doit être 'directeur_division_activite'"
        }, status=400)

    # =====================================================
    # ALREADY ASSIGNED
    # =====================================================

    if raw_user.get('division_activite_id'):

        existing_nom = "Inconnue"

        sc_ex, ex_resp = _call_juridique(
            'get',
            f'/juridique/division/{raw_user["division_activite_id"]}/',
            token
        )

        if sc_ex == 200:
            existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')

        return Response({
            "status": "error",
            "code": "ALREADY_ASSIGNED",
            "message": "Utilisateur déjà affecté à une division activité.",
            "data": {
                "existing_division_activite_id": raw_user.get('division_activite_id'),
                "existing_division_activite_nom": existing_nom
            }
        }, status=400)

    # =====================================================
    # GET DIVISION ACTIVITE
    # =====================================================

    sc_div, div_resp = _call_juridique(
        'get',
        f'/juridique/division/{division_activite_id}/',
        token
    )

    if sc_div == 404:
        return Response({
            "status": "error",
            "code": "DIVISION_ACTIVITE_NOT_FOUND",
            "message": "Division activité introuvable."
        }, status=404)

    if sc_div != 200:
        return Response({
            "status": "error",
            "code": "JURIDIQUE_SERVICE_ERROR",
            "message": "Service juridique indisponible."
        }, status=503)

    division_activite_data = div_resp.get('data', {})

    # =====================================================
    # GET ACTIVITE ID
    # =====================================================

    activite_data = division_activite_data.get('activite')
    activite_id = None

    if isinstance(activite_data, dict):
        activite_id = activite_data.get('_id')
    elif isinstance(activite_data, str):
        activite_id = activite_data

    if not activite_id:
        return Response({
            "status": "error",
            "code": "ACTIVITE_NOT_FOUND_IN_DIVISION_ACTIVITE",
            "message": "Impossible de récupérer activite_id.",
            "debug": {"division_activite": division_activite_data}
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "division_activite_id": division_activite_id,
            "activite_id": activite_id
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "message": "Impossible de mettre à jour.",
            "detail": updated
        }, status=sc_update)

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc_check != 200:
        return Response({
            "status": "error",
            "code": "POST_CHECK_FAILED",
            "message": "Impossible de vérifier la sauvegarde."
        }, status=503)

    raw_user = check_resp.get('user', {})

    if str(raw_user.get('division_activite_id')) != str(division_activite_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "division_activite_id non sauvegardé",
            "debug": {
                "sent": division_activite_id,
                "received": raw_user.get('division_activite_id')
            }
        }, status=500)

    if str(raw_user.get('activite_id')) != str(activite_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "activite_id non sauvegardé",
            "debug": {
                "sent": activite_id,
                "received": raw_user.get('activite_id')
            }
        }, status=500)

    # =====================================================
    # BUILD USER
    # =====================================================

    full_user = _build_full_user(raw_user, token)

    # =====================================================
    # SUCCESS
    # =====================================================

    return Response({
        "status": "success",
        "code": "DIVISION_ACTIVITE_ASSIGNED",
        "message": f"Division activité affectée à {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "assigned_by": {
                "id": vice_president.id,
                "name": getattr(vice_president, 'nom_complet', str(vice_president)),
                "role": vice_president.role,
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# REASSIGN DIVISION ACTIVITE
# =========================================================

@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def reassign_division_activite_to_user(request):
    """
    PUT /affectation/reassign-division-activite/

    Body:
    {
        "user_id": 15,
        "division_activite_id": "682ab123456789abcdef9999"
    }
    """

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    vice_president = request.user

    user_id = request.data.get('user_id')
    division_activite_id = request.data.get('division_activite_id')

    # =====================================================
    # VALIDATION
    # =====================================================

    if not user_id:
        return Response({
            "status": "error",
            "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)

    if not division_activite_id:
        return Response({
            "status": "error",
            "code": "MISSING_DIVISION_ACTIVITE_ID",
            "message": "division_activite_id est obligatoire."
        }, status=400)

    # =====================================================
    # GET USER
    # =====================================================

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} introuvable."
        }, status=404)

    raw_user = user_response.get('user', {})
    user_data = _deserialize_user(raw_user)

    # =====================================================
    # ROLE CHECK
    # =====================================================

    if user_data.get('role') != 'directeur_division_activite':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": "L'utilisateur doit être 'directeur_division_activite'"
        }, status=400)

    # =====================================================
    # SAVE OLD DIVISION ACTIVITE
    # =====================================================

    old_div_id = raw_user.get('division_activite_id')
    old_div_nom = None

    if old_div_id:
        sc_old, old_resp = _call_juridique(
            'get',
            f'/juridique/division/{old_div_id}/',
            token
        )
        if sc_old == 200:
            old_div_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

    # =====================================================
    # GET DIVISION ACTIVITE
    # =====================================================

    sc_div, div_resp = _call_juridique(
        'get',
        f'/juridique/division/{division_activite_id}/',
        token
    )

    if sc_div == 404:
        return Response({
            "status": "error",
            "code": "DIVISION_ACTIVITE_NOT_FOUND",
            "message": "Division activité introuvable."
        }, status=404)

    if sc_div != 200:
        return Response({
            "status": "error",
            "code": "JURIDIQUE_SERVICE_ERROR",
            "message": "Service juridique indisponible."
        }, status=503)

    division_activite_data = div_resp.get('data', {})

    # =====================================================
    # GET ACTIVITE ID
    # =====================================================

    activite_data = division_activite_data.get('activite')
    activite_id = None

    if isinstance(activite_data, dict):
        activite_id = activite_data.get('_id')
    elif isinstance(activite_data, str):
        activite_id = activite_data

    if not activite_id:
        return Response({
            "status": "error",
            "code": "ACTIVITE_NOT_FOUND_IN_DIVISION_ACTIVITE",
            "message": "Impossible de récupérer activite_id.",
            "debug": {"division_activite": division_activite_data}
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "division_activite_id": division_activite_id,
            "activite_id": activite_id
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "message": "Impossible de mettre à jour.",
            "detail": updated
        }, status=sc_update)

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc_check != 200:
        return Response({
            "status": "error",
            "code": "POST_CHECK_FAILED",
            "message": "Impossible de vérifier la sauvegarde."
        }, status=503)

    raw_user = check_resp.get('user', {})

    if str(raw_user.get('division_activite_id')) != str(division_activite_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "division_activite_id non sauvegardé",
            "debug": {
                "sent": division_activite_id,
                "received": raw_user.get('division_activite_id')
            }
        }, status=500)

    if str(raw_user.get('activite_id')) != str(activite_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "activite_id non sauvegardé",
            "debug": {
                "sent": activite_id,
                "received": raw_user.get('activite_id')
            }
        }, status=500)

    # =====================================================
    # BUILD USER
    # =====================================================

    full_user = _build_full_user(raw_user, token)

    # =====================================================
    # SUCCESS
    # =====================================================

    new_div_nom = full_user.get('division_activite', {})
    if isinstance(new_div_nom, dict):
        new_div_nom = new_div_nom.get('nom', division_activite_id)

    return Response({
        "status": "success",
        "code": "DIVISION_ACTIVITE_REASSIGNED",
        "message": f"Division activité changée de '{old_div_nom or 'aucune'}' vers '{new_div_nom}'.",
        "data": {
            **full_user,
            "previous_division_activite_id": old_div_id,
            "previous_division_activite_nom": old_div_nom,
            "assigned_by": {
                "id": vice_president.id,
                "name": getattr(vice_president, 'nom_complet', str(vice_president)),
                "role": vice_president.role,
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# REMOVE DIVISION ACTIVITE
# =========================================================

@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def remove_division_activite_from_user(request, user_id):
    """
    DELETE /affectation/users/<user_id>/remove-division-activite/
    """

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    # =====================================================
    # GET USER
    # =====================================================

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} introuvable."
        }, status=404)

    raw_user = user_response.get('user', {})

    # =====================================================
    # CHECK ASSIGNMENT (on raw data)
    # =====================================================

    if not raw_user.get('division_activite_id'):
        return Response({
            "status": "error",
            "code": "NO_DIVISION_ACTIVITE",
            "message": "Aucune division activité affectée à cet utilisateur."
        }, status=400)

    current_div_id = raw_user.get('division_activite_id')
    div_nom = "Inconnue"

    sc_dir, dir_resp = _call_juridique(
        'get',
        f'/juridique/division/{current_div_id}/',
        token
    )
    if sc_dir == 200:
        div_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "division_activite_id": None,
            "activite_id": None
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "REMOVE_FAILED",
            "message": "Impossible de supprimer.",
            "detail": updated
        }, status=sc_update)

    # =====================================================
    # BUILD USER
    # =====================================================

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc2 == 200:
        full_user = _build_full_user(user_response2.get('user', {}), token)
    else:
        raw_user['division_activite_id'] = None
        raw_user['activite_id'] = None
        full_user = _build_full_user(raw_user, token)

    # =====================================================
    # SUCCESS
    # =====================================================

    return Response({
        "status": "success",
        "code": "DIVISION_ACTIVITE_REMOVED",
        "message": f"Division activité '{div_nom}' désaffectée de {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "removed_division_activite_id": current_div_id,
            "removed_division_activite_nom": div_nom,
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# LIST DIRECTEURS DIVISION ACTIVITE — NON AFFECTES
# =========================================================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def api_list_directeurs_division_activite(request):
    """Directeurs division activité NON affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "message": "Impossible de récupérer utilisateurs."
        }, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_division_activite'
        and not u.get('division_activite_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "count": len(data),
        "data": data
    })


# =========================================================
# LIST DIRECTEURS DIVISION ACTIVITE — AFFECTES
# =========================================================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def api_list_directeurs_division_activite_affectes(request):
    """Directeurs division activité affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "message": "Impossible de récupérer utilisateurs."
        }, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_division_activite'
        and u.get('division_activite_id')
    ]

    data = _build_full_users(cibles, token)

    return Response({
        "status": "success",
        "count": len(data),
        "data": data
    })


# =========================================================
# LIST ALL DIRECTEURS DIVISION ACTIVITE
# =========================================================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsVicePresedent])
def api_list_all_directeurs_division_activite(request):
    """Tous les directeurs division activité"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "message": "Impossible de récupérer utilisateurs."
        }, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'directeur_division_activite'
    ]

    data = _build_full_users(cibles, token)

    total = len(data)
    avec = len([x for x in data if x.get('has_division_activite')])
    sans = total - avec
    actifs = len([x for x in data if x.get('is_active')])

    return Response({
        "status": "success",
        "count": total,
        "statistics": {
            "with_division_activite": avec,
            "without_division_activite": sans,
            "active": actifs,
            "inactive": total - actifs,
        },
        "data": data,
        "timestamp": datetime.now().isoformat(),
    })
# # =========================================================
# # ASSIGN STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# # directeur_division_activite -> responsable_direction_division
# # =========================================================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def assign_structure_direction_to_user(request):
#     """
#     PATCH /affectation/assign-structure-direction/

#     Body:
#     {
#         "user_id": 20,
#         "structure_id": "682ab123456789abcdef1111"
#     }

#     Remplit automatiquement :
#     - structure_id
#     - division_id   (depuis structure.division)
#     - direction_division_id = structure_id  (type=direction)
#     """

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     # =====================================================
#     # VALIDATION
#     # =====================================================

#     if not user_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_USER_ID",
#             "message": "user_id est obligatoire."
#         }, status=400)

#     if not structure_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_STRUCTURE_ID",
#             "message": "structure_id est obligatoire."
#         }, status=400)

#     # =====================================================
#     # GET USER
#     # =====================================================

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur {user_id} introuvable."
#         }, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     # =====================================================
#     # ROLE CHECK
#     # =====================================================

#     if user_data.get('role') != 'responsable_direction_division':
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": "L'utilisateur doit être 'responsable_direction_division'."
#         }, status=400)

#     # =====================================================
#     # ALREADY ASSIGNED
#     # =====================================================

#     if raw_user.get('structure_id'):

#         existing_nom = "Inconnue"
#         sc_ex, ex_resp = _call_juridique(
#             'get',
#             f'/juridique/structure/{raw_user["structure_id"]}/',
#             token
#         )
#         if sc_ex == 200:
#             existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')

#         return Response({
#             "status": "error",
#             "code": "ALREADY_ASSIGNED",
#             "message": "Utilisateur déjà affecté à une structure.",
#             "data": {
#                 "existing_structure_id":  raw_user.get('structure_id'),
#                 "existing_structure_nom": existing_nom
#             }
#         }, status=400)

#     # =====================================================
#     # GET STRUCTURE
#     # =====================================================

#     sc_str, str_resp = _call_juridique(
#         'get',
#         f'/juridique/structure/{structure_id}/',
#         token
#     )

#     if sc_str == 404:
#         return Response({
#             "status": "error",
#             "code": "STRUCTURE_NOT_FOUND",
#             "message": "Structure introuvable."
#         }, status=404)

#     if sc_str != 200:
#         return Response({
#             "status": "error",
#             "code": "JURIDIQUE_SERVICE_ERROR",
#             "message": "Service juridique indisponible."
#         }, status=503)

#     structure_data = str_resp.get('data', {})

#     # =====================================================
#     # VERIFY TYPE = direction
#     # =====================================================

#     if structure_data.get('type') != 'direction':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'direction' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     # =====================================================
#     # GET DIVISION ID
#     # =====================================================

#     division_data = structure_data.get('division')
#     division_id   = None

#     if isinstance(division_data, dict):
#         division_id = division_data.get('_id')
#     elif isinstance(division_data, str):
#         division_id = division_data

#     if not division_id:
#         return Response({
#             "status": "error",
#             "code": "DIVISION_NOT_FOUND_IN_STRUCTURE",
#             "message": "Impossible de récupérer division_id depuis la structure.",
#             "debug": {"structure": structure_data}
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={
#             "structure_id":         structure_id,
#             "division_id":          division_id,
#         }
#     )

#     if sc_update != 200:
#         return Response({
#             "status": "error",
#             "code": "UPDATE_FAILED",
#             "message": "Impossible de mettre à jour.",
#             "detail": updated
#         }, status=sc_update)

#     # =====================================================
#     # VERIFY SAVE
#     # =====================================================

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)

#     if sc_check != 200:
#         return Response({
#             "status": "error",
#             "code": "POST_CHECK_FAILED",
#             "message": "Impossible de vérifier la sauvegarde."
#         }, status=503)

#     raw_user = check_resp.get('user', {})

#     if str(raw_user.get('structure_id')) != str(structure_id):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "structure_id non sauvegardé",
#             "debug": {
#                 "sent":     structure_id,
#                 "received": raw_user.get('structure_id')
#             }
#         }, status=500)

#     if str(raw_user.get('division_id')) != str(division_id):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "division_id non sauvegardé",
#             "debug": {
#                 "sent":     division_id,
#                 "received": raw_user.get('division_id')
#             }
#         }, status=500)

#     # =====================================================
#     # BUILD USER
#     # =====================================================

#     full_user = _build_full_user(raw_user, token)

#     # =====================================================
#     # SUCCESS
#     # =====================================================

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DIRECTION_ASSIGNED",
#         "message": f"Structure (direction) affectée à {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REASSIGN STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# # =========================================================

# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def reassign_structure_direction_to_user(request):
#     """
#     PUT /affectation/reassign-structure-direction/
#     """

#     token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
#     if not structure_id:
#         return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     if user_data.get('role') != 'responsable_direction_division':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": "L'utilisateur doit être 'responsable_direction_division'."}, status=400)

#     # ancienne structure
#     old_str_id  = raw_user.get('structure_id')
#     old_str_nom = None
#     if old_str_id:
#         sc_old, old_resp = _call_juridique('get', f'/juridique/structure/{old_str_id}/', token)
#         if sc_old == 200:
#             old_str_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

#     # nouvelle structure
#     sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
#     if sc_str == 404:
#         return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
#     if sc_str != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

#     structure_data = str_resp.get('data', {})

#     if structure_data.get('type') != 'direction':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'direction' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     division_data = structure_data.get('division')
#     division_id   = division_data.get('_id') if isinstance(division_data, dict) else division_data

#     if not division_id:
#         return Response({"status": "error", "code": "DIVISION_NOT_FOUND_IN_STRUCTURE", "message": "Impossible de récupérer division_id."}, status=400)

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": structure_id, "division_id": division_id}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc_check != 200:
#         return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

#     raw_user  = check_resp.get('user', {})
#     full_user = _build_full_user(raw_user, token)

#     new_str_nom = structure_data.get('nom', structure_id)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DIRECTION_REASSIGNED",
#         "message": f"Structure changée de '{old_str_nom or 'aucune'}' vers '{new_str_nom}'.",
#         "data": {
#             **full_user,
#             "previous_structure_id":  old_str_id,
#             "previous_structure_nom": old_str_nom,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REMOVE STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# # =========================================================

# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def remove_structure_direction_from_user(request, user_id):
#     """
#     DELETE /affectation/users/<user_id>/remove-structure-direction/
#     """

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user = user_response.get('user', {})

#     if not raw_user.get('structure_id'):
#         return Response({"status": "error", "code": "NO_STRUCTURE", "message": "Aucune structure affectée."}, status=400)

#     current_str_id  = raw_user.get('structure_id')
#     str_nom         = "Inconnue"
#     sc_dir, dir_resp = _call_juridique('get', f'/juridique/structure/{current_str_id}/', token)
#     if sc_dir == 200:
#         str_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": None, "division_id": None}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "REMOVE_FAILED", "message": "Impossible de supprimer.", "detail": updated}, status=sc_update)

#     sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc2 == 200:
#         full_user = _build_full_user(user_response2.get('user', {}), token)
#     else:
#         raw_user['structure_id'] = None
#         raw_user['division_id']  = None
#         full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DIRECTION_REMOVED",
#         "message": f"Structure '{str_nom}' désaffectée de {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "removed_structure_id":  current_str_id,
#             "removed_structure_nom": str_nom,
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # LIST RESPONSABLES DIRECTION DIVISION — NON AFFECTES
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_direction_division(request):
#     """Responsables direction division NON affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_direction_division'
#         and not u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)

#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_direction_division_affectes(request):
#     """Responsables direction division affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_direction_division'
#         and u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)

#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_all_responsables_direction_division(request):
#     """Tous les responsables direction division"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_direction_division'
#     ]

#     data   = _build_full_users(cibles, token)
#     total  = len(data)
#     avec   = len([x for x in data if x.get('structure_id')])
#     actifs = len([x for x in data if x.get('is_active')])

#     return Response({
#         "status": "success",
#         "count": total,
#         "statistics": {
#             "with_structure":    avec,
#             "without_structure": total - avec,
#             "active":            actifs,
#             "inactive":          total - actifs,
#         },
#         "data": data,
#         "timestamp": datetime.now().isoformat(),
#     })


# # =========================================================
# # ASSIGN STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# # directeur_division_activite -> responsable_departement_division
# # =========================================================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def assign_structure_departement_to_user(request):
#     """
#     PATCH /affectation/assign-structure-departement/

#     Body:
#     {
#         "user_id": 21,
#         "structure_id": "682ab123456789abcdef2222"
#     }

#     Remplit automatiquement :
#     - structure_id
#     - division_id   (depuis structure.division)
#     - type vérifié = departement
#     """

#     token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
#     if not structure_id:
#         return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     if user_data.get('role') != 'responsable_departement_division':
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": "L'utilisateur doit être 'responsable_departement_division'."
#         }, status=400)

#     if raw_user.get('structure_id'):
#         existing_nom = "Inconnue"
#         sc_ex, ex_resp = _call_juridique('get', f'/juridique/structure/{raw_user["structure_id"]}/', token)
#         if sc_ex == 200:
#             existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')
#         return Response({
#             "status": "error",
#             "code": "ALREADY_ASSIGNED",
#             "message": "Utilisateur déjà affecté à une structure.",
#             "data": {
#                 "existing_structure_id":  raw_user.get('structure_id'),
#                 "existing_structure_nom": existing_nom
#             }
#         }, status=400)

#     sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
#     if sc_str == 404:
#         return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
#     if sc_str != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

#     structure_data = str_resp.get('data', {})

#     if structure_data.get('type') != 'departement':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'departement' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     division_data = structure_data.get('division')
#     division_id   = division_data.get('_id') if isinstance(division_data, dict) else division_data

#     if not division_id:
#         return Response({"status": "error", "code": "DIVISION_NOT_FOUND_IN_STRUCTURE", "message": "Impossible de récupérer division_id.", "debug": {"structure": structure_data}}, status=400)

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": structure_id, "division_id": division_id}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc_check != 200:
#         return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

#     raw_user = check_resp.get('user', {})

#     if str(raw_user.get('structure_id')) != str(structure_id):
#         return Response({"status": "error", "code": "UPDATE_NOT_PERSISTED", "message": "structure_id non sauvegardé", "debug": {"sent": structure_id, "received": raw_user.get('structure_id')}}, status=500)
#     if str(raw_user.get('division_id')) != str(division_id):
#         return Response({"status": "error", "code": "UPDATE_NOT_PERSISTED", "message": "division_id non sauvegardé",  "debug": {"sent": division_id,  "received": raw_user.get('division_id')}},  status=500)

#     full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DEPARTEMENT_ASSIGNED",
#         "message": f"Structure (département) affectée à {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REASSIGN STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# # =========================================================

# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def reassign_structure_departement_to_user(request):
#     """
#     PUT /affectation/reassign-structure-departement/
#     """

#     token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
#     if not structure_id:
#         return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     if user_data.get('role') != 'responsable_departement_division':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": "L'utilisateur doit être 'responsable_departement_division'."}, status=400)

#     old_str_id  = raw_user.get('structure_id')
#     old_str_nom = None
#     if old_str_id:
#         sc_old, old_resp = _call_juridique('get', f'/juridique/structure/{old_str_id}/', token)
#         if sc_old == 200:
#             old_str_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

#     sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
#     if sc_str == 404:
#         return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
#     if sc_str != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

#     structure_data = str_resp.get('data', {})

#     if structure_data.get('type') != 'departement':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'departement' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     division_data = structure_data.get('division')
#     division_id   = division_data.get('_id') if isinstance(division_data, dict) else division_data

#     if not division_id:
#         return Response({"status": "error", "code": "DIVISION_NOT_FOUND_IN_STRUCTURE", "message": "Impossible de récupérer division_id."}, status=400)

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": structure_id, "division_id": division_id}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc_check != 200:
#         return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

#     raw_user  = check_resp.get('user', {})
#     full_user = _build_full_user(raw_user, token)

#     new_str_nom = structure_data.get('nom', structure_id)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DEPARTEMENT_REASSIGNED",
#         "message": f"Structure changée de '{old_str_nom or 'aucune'}' vers '{new_str_nom}'.",
#         "data": {
#             **full_user,
#             "previous_structure_id":  old_str_id,
#             "previous_structure_nom": old_str_nom,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REMOVE STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# # =========================================================

# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def remove_structure_departement_from_user(request, user_id):
#     """
#     DELETE /affectation/users/<user_id>/remove-structure-departement/
#     """

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user = user_response.get('user', {})

#     if not raw_user.get('structure_id'):
#         return Response({"status": "error", "code": "NO_STRUCTURE", "message": "Aucune structure affectée."}, status=400)

#     current_str_id = raw_user.get('structure_id')
#     str_nom        = "Inconnue"
#     sc_dir, dir_resp = _call_juridique('get', f'/juridique/structure/{current_str_id}/', token)
#     if sc_dir == 200:
#         str_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": None, "division_id": None}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "REMOVE_FAILED", "message": "Impossible de supprimer.", "detail": updated}, status=sc_update)

#     sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc2 == 200:
#         full_user = _build_full_user(user_response2.get('user', {}), token)
#     else:
#         raw_user['structure_id'] = None
#         raw_user['division_id']  = None
#         full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DEPARTEMENT_REMOVED",
#         "message": f"Structure '{str_nom}' désaffectée de {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "removed_structure_id":  current_str_id,
#             "removed_structure_nom": str_nom,
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # LIST RESPONSABLES DEPARTEMENT DIVISION — NON AFFECTES
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_departement_division(request):
#     """Responsables département division NON affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_departement_division'
#         and not u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)
#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_departement_division_affectes(request):
#     """Responsables département division affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_departement_division'
#         and u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)
#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_all_responsables_departement_division(request):
#     """Tous les responsables département division"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_departement_division'
#     ]

#     data   = _build_full_users(cibles, token)
#     total  = len(data)
#     avec   = len([x for x in data if x.get('structure_id')])
#     actifs = len([x for x in data if x.get('is_active')])

#     return Response({
#         "status": "success",
#         "count": total,
#         "statistics": {
#             "with_structure":    avec,
#             "without_structure": total - avec,
#             "active":            actifs,
#             "inactive":          total - actifs,
#         },
#         "data": data,
#         "timestamp": datetime.now().isoformat(),
#     })








# # =========================================================
# # ASSIGN STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# # =========================================================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def assign_structure_direction_to_user(request):
#     """
#     PATCH /affectation/assign-structure-direction/

#     Body:
#     {
#         "user_id": 20,
#         "structure_id": "682ab123456789abcdef1111"
#     }

#     Remplit automatiquement :
#     - structure_id
#     - division_id  (depuis le directeur_division_activite connecté)
#     """

#     token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user  # directeur_division_activite connecté

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     # =====================================================
#     # VALIDATION
#     # =====================================================

#     if not user_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_USER_ID",
#             "message": "user_id est obligatoire."
#         }, status=400)

#     if not structure_id:
#         return Response({
#             "status": "error",
#             "code": "MISSING_STRUCTURE_ID",
#             "message": "structure_id est obligatoire."
#         }, status=400)

#     # =====================================================
#     # GET DIVISION ID FROM CONNECTED DIRECTEUR
#     # =====================================================

#     sc_dir, dir_response = _call_auth(
#         'get',
#         f'/auth/users/{directeur.id}/',
#         token
#     )

#     if sc_dir != 200:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_NOT_FOUND",
#             "message": "Impossible de récupérer le directeur connecté."
#         }, status=503)

#     directeur_raw = dir_response.get('user', {})
#     division_id   = directeur_raw.get('division_activite_id')

#     if not division_id:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_HAS_NO_DIVISION",
#             "message": "Le directeur connecté n'a pas de division_activite_id affectée."
#         }, status=400)

#     # =====================================================
#     # GET TARGET USER
#     # =====================================================

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)

#     if sc != 200:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur {user_id} introuvable."
#         }, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     # =====================================================
#     # ROLE CHECK
#     # =====================================================

#     if user_data.get('role') != 'responsable_direction_division':
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": "L'utilisateur doit être 'responsable_direction_division'."
#         }, status=400)

#     # =====================================================
#     # ALREADY ASSIGNED
#     # =====================================================

#     if raw_user.get('structure_id'):

#         existing_nom = "Inconnue"
#         sc_ex, ex_resp = _call_juridique(
#             'get',
#             f'/juridique/structure/{raw_user["structure_id"]}/',
#             token
#         )
#         if sc_ex == 200:
#             existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')

#         return Response({
#             "status": "error",
#             "code": "ALREADY_ASSIGNED",
#             "message": "Utilisateur déjà affecté à une structure.",
#             "data": {
#                 "existing_structure_id":  raw_user.get('structure_id'),
#                 "existing_structure_nom": existing_nom
#             }
#         }, status=400)

#     # =====================================================
#     # GET STRUCTURE & VERIFY TYPE = direction
#     # =====================================================

#     sc_str, str_resp = _call_juridique(
#         'get',
#         f'/juridique/structure/{structure_id}/',
#         token
#     )

#     if sc_str == 404:
#         return Response({
#             "status": "error",
#             "code": "STRUCTURE_NOT_FOUND",
#             "message": "Structure introuvable."
#         }, status=404)

#     if sc_str != 200:
#         return Response({
#             "status": "error",
#             "code": "JURIDIQUE_SERVICE_ERROR",
#             "message": "Service juridique indisponible."
#         }, status=503)

#     structure_data = str_resp.get('data', {})

#     if structure_data.get('type') != 'direction':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'direction' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch',
#         f'/auth/users/{user_id}/update/',
#         token,
#         json={
#             "structure_id": structure_id,
#             "division_id":  division_id,
#         }
#     )

#     if sc_update != 200:
#         return Response({
#             "status": "error",
#             "code": "UPDATE_FAILED",
#             "message": "Impossible de mettre à jour.",
#             "detail": updated
#         }, status=sc_update)

#     # =====================================================
#     # VERIFY SAVE
#     # =====================================================

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)

#     if sc_check != 200:
#         return Response({
#             "status": "error",
#             "code": "POST_CHECK_FAILED",
#             "message": "Impossible de vérifier la sauvegarde."
#         }, status=503)

#     raw_user = check_resp.get('user', {})

#     if str(raw_user.get('structure_id')) != str(structure_id):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "structure_id non sauvegardé",
#             "debug": {
#                 "sent":     structure_id,
#                 "received": raw_user.get('structure_id')
#             }
#         }, status=500)

#     if str(raw_user.get('division_id')) != str(division_id):
#         return Response({
#             "status": "error",
#             "code": "UPDATE_NOT_PERSISTED",
#             "message": "division_id non sauvegardé",
#             "debug": {
#                 "sent":     division_id,
#                 "received": raw_user.get('division_id')
#             }
#         }, status=500)

#     # =====================================================
#     # BUILD USER
#     # =====================================================

#     full_user = _build_full_user(raw_user, token)

#     # =====================================================
#     # SUCCESS
#     # =====================================================

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DIRECTION_ASSIGNED",
#         "message": f"Structure (direction) affectée à {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REASSIGN STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# # =========================================================

# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def reassign_structure_direction_to_user(request):
#     """
#     PUT /affectation/reassign-structure-direction/
#     """

#     token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
#     if not structure_id:
#         return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

#     # =====================================================
#     # GET DIVISION ID FROM CONNECTED DIRECTEUR
#     # =====================================================

#     sc_dir, dir_response = _call_auth('get', f'/auth/users/{directeur.id}/', token)

#     if sc_dir != 200:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_NOT_FOUND",
#             "message": "Impossible de récupérer le directeur connecté."
#         }, status=503)

#     directeur_raw = dir_response.get('user', {})
#     division_id   = directeur_raw.get('division_activite_id')

#     if not division_id:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_HAS_NO_DIVISION",
#             "message": "Le directeur connecté n'a pas de division_activite_id affectée."
#         }, status=400)

#     # =====================================================
#     # GET TARGET USER
#     # =====================================================

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     if user_data.get('role') != 'responsable_direction_division':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": "L'utilisateur doit être 'responsable_direction_division'."}, status=400)

#     # ancienne structure
#     old_str_id  = raw_user.get('structure_id')
#     old_str_nom = None
#     if old_str_id:
#         sc_old, old_resp = _call_juridique('get', f'/juridique/structure/{old_str_id}/', token)
#         if sc_old == 200:
#             old_str_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

#     # =====================================================
#     # GET STRUCTURE & VERIFY TYPE
#     # =====================================================

#     sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
#     if sc_str == 404:
#         return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
#     if sc_str != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

#     structure_data = str_resp.get('data', {})

#     if structure_data.get('type') != 'direction':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'direction' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": structure_id, "division_id": division_id}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

#     # =====================================================
#     # VERIFY SAVE
#     # =====================================================

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc_check != 200:
#         return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

#     raw_user  = check_resp.get('user', {})
#     full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DIRECTION_REASSIGNED",
#         "message": f"Structure changée de '{old_str_nom or 'aucune'}' vers '{structure_data.get('nom', structure_id)}'.",
#         "data": {
#             **full_user,
#             "previous_structure_id":  old_str_id,
#             "previous_structure_nom": old_str_nom,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REMOVE STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# # =========================================================

# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def remove_structure_direction_from_user(request, user_id):
#     """
#     DELETE /affectation/users/<user_id>/remove-structure-direction/
#     """

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user = user_response.get('user', {})

#     if not raw_user.get('structure_id'):
#         return Response({"status": "error", "code": "NO_STRUCTURE", "message": "Aucune structure affectée."}, status=400)

#     current_str_id = raw_user.get('structure_id')
#     str_nom        = "Inconnue"
#     sc_dir, dir_resp = _call_juridique('get', f'/juridique/structure/{current_str_id}/', token)
#     if sc_dir == 200:
#         str_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": None, "division_id": None}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "REMOVE_FAILED", "message": "Impossible de supprimer.", "detail": updated}, status=sc_update)

#     sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc2 == 200:
#         full_user = _build_full_user(user_response2.get('user', {}), token)
#     else:
#         raw_user['structure_id'] = None
#         raw_user['division_id']  = None
#         full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DIRECTION_REMOVED",
#         "message": f"Structure '{str_nom}' désaffectée de {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "removed_structure_id":  current_str_id,
#             "removed_structure_nom": str_nom,
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # LIST RESPONSABLES DIRECTION DIVISION
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_direction_division(request):
#     """Responsables direction division NON affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_direction_division'
#         and not u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)
#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_direction_division_affectes(request):
#     """Responsables direction division affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_direction_division'
#         and u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)
#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_all_responsables_direction_division(request):
#     """Tous les responsables direction division"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_direction_division'
#     ]

#     data   = _build_full_users(cibles, token)
#     total  = len(data)
#     avec   = len([x for x in data if x.get('structure_id')])
#     actifs = len([x for x in data if x.get('is_active')])

#     return Response({
#         "status": "success",
#         "count": total,
#         "statistics": {
#             "with_structure":    avec,
#             "without_structure": total - avec,
#             "active":            actifs,
#             "inactive":          total - actifs,
#         },
#         "data": data,
#         "timestamp": datetime.now().isoformat(),
#     })


# # =========================================================
# # ASSIGN STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# # =========================================================

# @api_view(['PATCH'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def assign_structure_departement_to_user(request):
#     """
#     PATCH /affectation/assign-structure-departement/

#     Body:
#     {
#         "user_id": 21,
#         "structure_id": "682ab123456789abcdef2222"
#     }

#     Remplit automatiquement :
#     - structure_id
#     - division_id  (depuis le directeur_division_activite connecté)
#     """

#     token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
#     if not structure_id:
#         return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

#     # =====================================================
#     # GET DIVISION ID FROM CONNECTED DIRECTEUR
#     # =====================================================

#     sc_dir, dir_response = _call_auth('get', f'/auth/users/{directeur.id}/', token)

#     if sc_dir != 200:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_NOT_FOUND",
#             "message": "Impossible de récupérer le directeur connecté."
#         }, status=503)

#     directeur_raw = dir_response.get('user', {})
#     division_id   = directeur_raw.get('division_activite_id')

#     if not division_id:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_HAS_NO_DIVISION",
#             "message": "Le directeur connecté n'a pas de division_activite_id affectée."
#         }, status=400)

#     # =====================================================
#     # GET TARGET USER
#     # =====================================================

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     if user_data.get('role') != 'responsable_departement_division':
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": "L'utilisateur doit être 'responsable_departement_division'."
#         }, status=400)

#     if raw_user.get('structure_id'):
#         existing_nom = "Inconnue"
#         sc_ex, ex_resp = _call_juridique('get', f'/juridique/structure/{raw_user["structure_id"]}/', token)
#         if sc_ex == 200:
#             existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')
#         return Response({
#             "status": "error",
#             "code": "ALREADY_ASSIGNED",
#             "message": "Utilisateur déjà affecté à une structure.",
#             "data": {
#                 "existing_structure_id":  raw_user.get('structure_id'),
#                 "existing_structure_nom": existing_nom
#             }
#         }, status=400)

#     # =====================================================
#     # GET STRUCTURE & VERIFY TYPE = departement
#     # =====================================================

#     sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
#     if sc_str == 404:
#         return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
#     if sc_str != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

#     structure_data = str_resp.get('data', {})

#     if structure_data.get('type') != 'departement':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'departement' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": structure_id, "division_id": division_id}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

#     # =====================================================
#     # VERIFY SAVE
#     # =====================================================

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc_check != 200:
#         return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

#     raw_user = check_resp.get('user', {})

#     if str(raw_user.get('structure_id')) != str(structure_id):
#         return Response({"status": "error", "code": "UPDATE_NOT_PERSISTED", "message": "structure_id non sauvegardé", "debug": {"sent": structure_id, "received": raw_user.get('structure_id')}}, status=500)
#     if str(raw_user.get('division_id')) != str(division_id):
#         return Response({"status": "error", "code": "UPDATE_NOT_PERSISTED", "message": "division_id non sauvegardé",  "debug": {"sent": division_id,  "received": raw_user.get('division_id')}},  status=500)

#     full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DEPARTEMENT_ASSIGNED",
#         "message": f"Structure (département) affectée à {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REASSIGN STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# # =========================================================

# @api_view(['PUT'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def reassign_structure_departement_to_user(request):
#     """
#     PUT /affectation/reassign-structure-departement/
#     """

#     token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
#     directeur = request.user

#     user_id      = request.data.get('user_id')
#     structure_id = request.data.get('structure_id')

#     if not user_id:
#         return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
#     if not structure_id:
#         return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

#     # =====================================================
#     # GET DIVISION ID FROM CONNECTED DIRECTEUR
#     # =====================================================

#     sc_dir, dir_response = _call_auth('get', f'/auth/users/{directeur.id}/', token)

#     if sc_dir != 200:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_NOT_FOUND",
#             "message": "Impossible de récupérer le directeur connecté."
#         }, status=503)

#     directeur_raw = dir_response.get('user', {})
#     division_id   = directeur_raw.get('division_activite_id')

#     if not division_id:
#         return Response({
#             "status": "error",
#             "code": "DIRECTEUR_HAS_NO_DIVISION",
#             "message": "Le directeur connecté n'a pas de division_activite_id affectée."
#         }, status=400)

#     # =====================================================
#     # GET TARGET USER
#     # =====================================================

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user  = user_response.get('user', {})
#     user_data = _deserialize_user(raw_user)

#     if user_data.get('role') != 'responsable_departement_division':
#         return Response({"status": "error", "code": "INVALID_ROLE", "message": "L'utilisateur doit être 'responsable_departement_division'."}, status=400)

#     old_str_id  = raw_user.get('structure_id')
#     old_str_nom = None
#     if old_str_id:
#         sc_old, old_resp = _call_juridique('get', f'/juridique/structure/{old_str_id}/', token)
#         if sc_old == 200:
#             old_str_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

#     # =====================================================
#     # GET STRUCTURE & VERIFY TYPE
#     # =====================================================

#     sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
#     if sc_str == 404:
#         return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
#     if sc_str != 200:
#         return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

#     structure_data = str_resp.get('data', {})

#     if structure_data.get('type') != 'departement':
#         return Response({
#             "status": "error",
#             "code": "INVALID_STRUCTURE_TYPE",
#             "message": f"La structure doit être de type 'departement' (actuel: '{structure_data.get('type')}')."
#         }, status=400)

#     # =====================================================
#     # UPDATE USER
#     # =====================================================

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": structure_id, "division_id": division_id}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

#     sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc_check != 200:
#         return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

#     raw_user  = check_resp.get('user', {})
#     full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DEPARTEMENT_REASSIGNED",
#         "message": f"Structure changée de '{old_str_nom or 'aucune'}' vers '{structure_data.get('nom', structure_id)}'.",
#         "data": {
#             **full_user,
#             "previous_structure_id":  old_str_id,
#             "previous_structure_nom": old_str_nom,
#             "assigned_by": {
#                 "id":   directeur.id,
#                 "name": getattr(directeur, 'nom_complet', str(directeur)),
#                 "role": directeur.role,
#             },
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # REMOVE STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# # =========================================================

# @api_view(['DELETE'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def remove_structure_departement_from_user(request, user_id):
#     """
#     DELETE /affectation/users/<user_id>/remove-structure-departement/
#     """

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc != 200:
#         return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

#     raw_user = user_response.get('user', {})

#     if not raw_user.get('structure_id'):
#         return Response({"status": "error", "code": "NO_STRUCTURE", "message": "Aucune structure affectée."}, status=400)

#     current_str_id = raw_user.get('structure_id')
#     str_nom        = "Inconnue"
#     sc_dir, dir_resp = _call_juridique('get', f'/juridique/structure/{current_str_id}/', token)
#     if sc_dir == 200:
#         str_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

#     sc_update, updated = _call_auth(
#         'patch', f'/auth/users/{user_id}/update/', token,
#         json={"structure_id": None, "division_id": None}
#     )
#     if sc_update != 200:
#         return Response({"status": "error", "code": "REMOVE_FAILED", "message": "Impossible de supprimer.", "detail": updated}, status=sc_update)

#     sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
#     if sc2 == 200:
#         full_user = _build_full_user(user_response2.get('user', {}), token)
#     else:
#         raw_user['structure_id'] = None
#         raw_user['division_id']  = None
#         full_user = _build_full_user(raw_user, token)

#     return Response({
#         "status": "success",
#         "code": "STRUCTURE_DEPARTEMENT_REMOVED",
#         "message": f"Structure '{str_nom}' désaffectée de {full_user.get('nom_complet')}.",
#         "data": {
#             **full_user,
#             "removed_structure_id":  current_str_id,
#             "removed_structure_nom": str_nom,
#             "timestamp": datetime.now().isoformat(),
#         }
#     }, status=200)


# # =========================================================
# # LIST RESPONSABLES DEPARTEMENT DIVISION
# # =========================================================

# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_departement_division(request):
#     """Responsables département division NON affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_departement_division'
#         and not u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)
#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_responsables_departement_division_affectes(request):
#     """Responsables département division affectés"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_departement_division'
#         and u.get('structure_id')
#     ]

#     data = _build_full_users(cibles, token)
#     return Response({"status": "success", "count": len(data), "data": data})


# @api_view(['GET'])
# @authentication_classes([RemoteJWTAuthentication])
# @permission_classes([IsDirecteurDivisionActivite])
# def api_list_all_responsables_departement_division(request):
#     """Tous les responsables département division"""

#     token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

#     sc, response = _call_auth('get', '/auth/users/', token)
#     if sc != 200:
#         return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

#     users_raw = response.get('users', [])

#     cibles = [
#         u for u in users_raw
#         if isinstance(u, dict)
#         and u.get('role') == 'responsable_departement_division'
#     ]

#     data   = _build_full_users(cibles, token)
#     total  = len(data)
#     avec   = len([x for x in data if x.get('structure_id')])
#     actifs = len([x for x in data if x.get('is_active')])

#     return Response({
#         "status": "success",
#         "count": total,
#         "statistics": {
#             "with_structure":    avec,
#             "without_structure": total - avec,
#             "active":            actifs,
#             "inactive":          total - actifs,
#         },
#         "data": data,
#         "timestamp": datetime.now().isoformat(),
#     })
# =========================================================
# ASSIGN STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# =========================================================

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def assign_structure_direction_to_user(request):
    """
    PATCH /affectation/assign-structure-direction/

    Body:
    {
        "user_id": 20,
        "structure_id": "682ab123456789abcdef1111"
    }

    Remplit automatiquement :
    - structure_id
    - division_activite_id  (depuis le directeur_division_activite connecté)
    """

    token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user

    user_id      = request.data.get('user_id')
    structure_id = request.data.get('structure_id')

    # =====================================================
    # VALIDATION
    # =====================================================

    if not user_id:
        return Response({
            "status": "error",
            "code": "MISSING_USER_ID",
            "message": "user_id est obligatoire."
        }, status=400)

    if not structure_id:
        return Response({
            "status": "error",
            "code": "MISSING_STRUCTURE_ID",
            "message": "structure_id est obligatoire."
        }, status=400)

    # =====================================================
    # GET DIVISION_ACTIVITE_ID FROM CONNECTED DIRECTEUR
    # =====================================================

    sc_dir, dir_response = _call_auth(
        'get', f'/auth/users/{directeur.id}/', token
    )

    if sc_dir != 200:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_NOT_FOUND",
            "message": "Impossible de récupérer le directeur connecté."
        }, status=503)

    directeur_raw      = dir_response.get('user', {})
    division_activite_id = directeur_raw.get('division_activite_id')

    if not division_activite_id:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_HAS_NO_DIVISION",
            "message": "Le directeur connecté n'a pas de division_activite_id affectée."
        }, status=400)

    # =====================================================
    # GET TARGET USER
    # =====================================================

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc != 200:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} introuvable."
        }, status=404)

    raw_user  = user_response.get('user', {})
    user_data = _deserialize_user(raw_user)

    # =====================================================
    # ROLE CHECK
    # =====================================================

    if user_data.get('role') != 'responsable_direction_division':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": "L'utilisateur doit être 'responsable_direction_division'."
        }, status=400)

    # =====================================================
    # ALREADY ASSIGNED
    # =====================================================

    if raw_user.get('structure_id'):

        existing_nom = "Inconnue"
        sc_ex, ex_resp = _call_juridique(
            'get',
            f'/juridique/structure/{raw_user["structure_id"]}/',
            token
        )
        if sc_ex == 200:
            existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')

        return Response({
            "status": "error",
            "code": "ALREADY_ASSIGNED",
            "message": "Utilisateur déjà affecté à une structure.",
            "data": {
                "existing_structure_id":  raw_user.get('structure_id'),
                "existing_structure_nom": existing_nom
            }
        }, status=400)

    # =====================================================
    # GET STRUCTURE & VERIFY TYPE = direction
    # =====================================================

    sc_str, str_resp = _call_juridique(
        'get', f'/juridique/structure/{structure_id}/', token
    )

    if sc_str == 404:
        return Response({
            "status": "error",
            "code": "STRUCTURE_NOT_FOUND",
            "message": "Structure introuvable."
        }, status=404)

    if sc_str != 200:
        return Response({
            "status": "error",
            "code": "JURIDIQUE_SERVICE_ERROR",
            "message": "Service juridique indisponible."
        }, status=503)

    structure_data = str_resp.get('data', {})

    if structure_data.get('type') != 'direction':
        return Response({
            "status": "error",
            "code": "INVALID_STRUCTURE_TYPE",
            "message": f"La structure doit être de type 'direction' (actuel: '{structure_data.get('type')}')."
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch',
        f'/auth/users/{user_id}/update/',
        token,
        json={
            "structure_id":         structure_id,
            "division_activite_id": division_activite_id,
        }
    )

    if sc_update != 200:
        return Response({
            "status": "error",
            "code": "UPDATE_FAILED",
            "message": "Impossible de mettre à jour.",
            "detail": updated
        }, status=sc_update)

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)

    if sc_check != 200:
        return Response({
            "status": "error",
            "code": "POST_CHECK_FAILED",
            "message": "Impossible de vérifier la sauvegarde."
        }, status=503)

    raw_user = check_resp.get('user', {})

    if str(raw_user.get('structure_id')) != str(structure_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "structure_id non sauvegardé",
            "debug": {
                "sent":     structure_id,
                "received": raw_user.get('structure_id')
            }
        }, status=500)

    if str(raw_user.get('division_activite_id')) != str(division_activite_id):
        return Response({
            "status": "error",
            "code": "UPDATE_NOT_PERSISTED",
            "message": "division_activite_id non sauvegardé",
            "debug": {
                "sent":     division_activite_id,
                "received": raw_user.get('division_activite_id')
            }
        }, status=500)

    # =====================================================
    # BUILD USER
    # =====================================================

    full_user = _build_full_user(raw_user, token)

    # =====================================================
    # SUCCESS
    # =====================================================

    return Response({
        "status": "success",
        "code": "STRUCTURE_DIRECTION_ASSIGNED",
        "message": f"Structure (direction) affectée à {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "assigned_by": {
                "id":   directeur.id,
                "name": getattr(directeur, 'nom_complet', str(directeur)),
                "role": directeur.role,
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# REASSIGN STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# =========================================================

@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def reassign_structure_direction_to_user(request):
    """
    PUT /affectation/reassign-structure-direction/
    """

    token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user

    user_id      = request.data.get('user_id')
    structure_id = request.data.get('structure_id')

    if not user_id:
        return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
    if not structure_id:
        return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

    # =====================================================
    # GET DIVISION_ACTIVITE_ID FROM CONNECTED DIRECTEUR
    # =====================================================

    sc_dir, dir_response = _call_auth('get', f'/auth/users/{directeur.id}/', token)

    if sc_dir != 200:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_NOT_FOUND",
            "message": "Impossible de récupérer le directeur connecté."
        }, status=503)

    directeur_raw        = dir_response.get('user', {})
    division_activite_id = directeur_raw.get('division_activite_id')

    if not division_activite_id:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_HAS_NO_DIVISION",
            "message": "Le directeur connecté n'a pas de division_activite_id affectée."
        }, status=400)

    # =====================================================
    # GET TARGET USER
    # =====================================================

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    raw_user  = user_response.get('user', {})
    user_data = _deserialize_user(raw_user)

    if user_data.get('role') != 'responsable_direction_division':
        return Response({"status": "error", "code": "INVALID_ROLE", "message": "L'utilisateur doit être 'responsable_direction_division'."}, status=400)

    # ancienne structure
    old_str_id  = raw_user.get('structure_id')
    old_str_nom = None
    if old_str_id:
        sc_old, old_resp = _call_juridique('get', f'/juridique/structure/{old_str_id}/', token)
        if sc_old == 200:
            old_str_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

    # =====================================================
    # GET STRUCTURE & VERIFY TYPE
    # =====================================================

    sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
    if sc_str == 404:
        return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
    if sc_str != 200:
        return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

    structure_data = str_resp.get('data', {})

    if structure_data.get('type') != 'direction':
        return Response({
            "status": "error",
            "code": "INVALID_STRUCTURE_TYPE",
            "message": f"La structure doit être de type 'direction' (actuel: '{structure_data.get('type')}')."
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch', f'/auth/users/{user_id}/update/', token,
        json={
            "structure_id":         structure_id,
            "division_activite_id": division_activite_id,
        }
    )
    if sc_update != 200:
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc_check != 200:
        return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

    raw_user  = check_resp.get('user', {})
    full_user = _build_full_user(raw_user, token)

    return Response({
        "status": "success",
        "code": "STRUCTURE_DIRECTION_REASSIGNED",
        "message": f"Structure changée de '{old_str_nom or 'aucune'}' vers '{structure_data.get('nom', structure_id)}'.",
        "data": {
            **full_user,
            "previous_structure_id":  old_str_id,
            "previous_structure_nom": old_str_nom,
            "assigned_by": {
                "id":   directeur.id,
                "name": getattr(directeur, 'nom_complet', str(directeur)),
                "role": directeur.role,
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# REMOVE STRUCTURE (RESPONSABLE_DIRECTION_DIVISION)
# =========================================================

@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def remove_structure_direction_from_user(request, user_id):
    """
    DELETE /affectation/users/<user_id>/remove-structure-direction/
    """

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    raw_user = user_response.get('user', {})

    if not raw_user.get('structure_id'):
        return Response({"status": "error", "code": "NO_STRUCTURE", "message": "Aucune structure affectée."}, status=400)

    current_str_id = raw_user.get('structure_id')
    str_nom        = "Inconnue"
    sc_dir, dir_resp = _call_juridique('get', f'/juridique/structure/{current_str_id}/', token)
    if sc_dir == 200:
        str_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

    sc_update, updated = _call_auth(
        'patch', f'/auth/users/{user_id}/update/', token,
        json={
            "structure_id":         None,
            "division_activite_id": None,
        }
    )
    if sc_update != 200:
        return Response({"status": "error", "code": "REMOVE_FAILED", "message": "Impossible de supprimer.", "detail": updated}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(user_response2.get('user', {}), token)
    else:
        raw_user['structure_id']         = None
        raw_user['division_activite_id'] = None
        full_user = _build_full_user(raw_user, token)

    return Response({
        "status": "success",
        "code": "STRUCTURE_DIRECTION_REMOVED",
        "message": f"Structure '{str_nom}' désaffectée de {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "removed_structure_id":  current_str_id,
            "removed_structure_nom": str_nom,
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# LIST RESPONSABLES DIRECTION DIVISION
# =========================================================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def api_list_responsables_direction_division(request):
    """Responsables direction division NON affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_direction_division'
        and not u.get('structure_id')
    ]

    data = _build_full_users(cibles, token)
    return Response({"status": "success", "count": len(data), "data": data})


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def api_list_responsables_direction_division_affectes(request):
    """Responsables direction division affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_direction_division'
        and u.get('structure_id')
    ]

    data = _build_full_users(cibles, token)
    return Response({"status": "success", "count": len(data), "data": data})


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def api_list_all_responsables_direction_division(request):
    """Tous les responsables direction division"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_direction_division'
    ]

    data   = _build_full_users(cibles, token)
    total  = len(data)
    avec   = len([x for x in data if x.get('structure_id')])
    actifs = len([x for x in data if x.get('is_active')])

    return Response({
        "status": "success",
        "count": total,
        "statistics": {
            "with_structure":    avec,
            "without_structure": total - avec,
            "active":            actifs,
            "inactive":          total - actifs,
        },
        "data": data,
        "timestamp": datetime.now().isoformat(),
    })


# =========================================================
# ASSIGN STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# =========================================================

@api_view(['PATCH'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def assign_structure_departement_to_user(request):
    """
    PATCH /affectation/assign-structure-departement/

    Body:
    {
        "user_id": 21,
        "structure_id": "682ab123456789abcdef2222"
    }

    Remplit automatiquement :
    - structure_id
    - division_activite_id  (depuis le directeur_division_activite connecté)
    """

    token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user

    user_id      = request.data.get('user_id')
    structure_id = request.data.get('structure_id')

    if not user_id:
        return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
    if not structure_id:
        return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

    # =====================================================
    # GET DIVISION_ACTIVITE_ID FROM CONNECTED DIRECTEUR
    # =====================================================

    sc_dir, dir_response = _call_auth('get', f'/auth/users/{directeur.id}/', token)

    if sc_dir != 200:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_NOT_FOUND",
            "message": "Impossible de récupérer le directeur connecté."
        }, status=503)

    directeur_raw        = dir_response.get('user', {})
    division_activite_id = directeur_raw.get('division_activite_id')

    if not division_activite_id:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_HAS_NO_DIVISION",
            "message": "Le directeur connecté n'a pas de division_activite_id affectée."
        }, status=400)

    # =====================================================
    # GET TARGET USER
    # =====================================================

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    raw_user  = user_response.get('user', {})
    user_data = _deserialize_user(raw_user)

    if user_data.get('role') != 'responsable_departement_division':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": "L'utilisateur doit être 'responsable_departement_division'."
        }, status=400)

    if raw_user.get('structure_id'):
        existing_nom = "Inconnue"
        sc_ex, ex_resp = _call_juridique('get', f'/juridique/structure/{raw_user["structure_id"]}/', token)
        if sc_ex == 200:
            existing_nom = ex_resp.get('data', {}).get('nom', 'Inconnue')
        return Response({
            "status": "error",
            "code": "ALREADY_ASSIGNED",
            "message": "Utilisateur déjà affecté à une structure.",
            "data": {
                "existing_structure_id":  raw_user.get('structure_id'),
                "existing_structure_nom": existing_nom
            }
        }, status=400)

    # =====================================================
    # GET STRUCTURE & VERIFY TYPE = departement
    # =====================================================

    sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
    if sc_str == 404:
        return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
    if sc_str != 200:
        return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

    structure_data = str_resp.get('data', {})

    if structure_data.get('type') != 'departement':
        return Response({
            "status": "error",
            "code": "INVALID_STRUCTURE_TYPE",
            "message": f"La structure doit être de type 'departement' (actuel: '{structure_data.get('type')}')."
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch', f'/auth/users/{user_id}/update/', token,
        json={
            "structure_id":         structure_id,
            "division_activite_id": division_activite_id,
        }
    )
    if sc_update != 200:
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

    # =====================================================
    # VERIFY SAVE
    # =====================================================

    sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc_check != 200:
        return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

    raw_user = check_resp.get('user', {})

    if str(raw_user.get('structure_id')) != str(structure_id):
        return Response({"status": "error", "code": "UPDATE_NOT_PERSISTED", "message": "structure_id non sauvegardé",         "debug": {"sent": structure_id,         "received": raw_user.get('structure_id')}},         status=500)
    if str(raw_user.get('division_activite_id')) != str(division_activite_id):
        return Response({"status": "error", "code": "UPDATE_NOT_PERSISTED", "message": "division_activite_id non sauvegardé", "debug": {"sent": division_activite_id, "received": raw_user.get('division_activite_id')}}, status=500)

    full_user = _build_full_user(raw_user, token)

    return Response({
        "status": "success",
        "code": "STRUCTURE_DEPARTEMENT_ASSIGNED",
        "message": f"Structure (département) affectée à {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "assigned_by": {
                "id":   directeur.id,
                "name": getattr(directeur, 'nom_complet', str(directeur)),
                "role": directeur.role,
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# REASSIGN STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# =========================================================

@api_view(['PUT'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def reassign_structure_departement_to_user(request):
    """
    PUT /affectation/reassign-structure-departement/
    """

    token     = request.headers.get('Authorization', '').split(' ', 1)[1].strip()
    directeur = request.user

    user_id      = request.data.get('user_id')
    structure_id = request.data.get('structure_id')

    if not user_id:
        return Response({"status": "error", "code": "MISSING_USER_ID",      "message": "user_id est obligatoire."},      status=400)
    if not structure_id:
        return Response({"status": "error", "code": "MISSING_STRUCTURE_ID", "message": "structure_id est obligatoire."}, status=400)

    # =====================================================
    # GET DIVISION_ACTIVITE_ID FROM CONNECTED DIRECTEUR
    # =====================================================

    sc_dir, dir_response = _call_auth('get', f'/auth/users/{directeur.id}/', token)

    if sc_dir != 200:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_NOT_FOUND",
            "message": "Impossible de récupérer le directeur connecté."
        }, status=503)

    directeur_raw        = dir_response.get('user', {})
    division_activite_id = directeur_raw.get('division_activite_id')

    if not division_activite_id:
        return Response({
            "status": "error",
            "code": "DIRECTEUR_HAS_NO_DIVISION",
            "message": "Le directeur connecté n'a pas de division_activite_id affectée."
        }, status=400)

    # =====================================================
    # GET TARGET USER
    # =====================================================

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    raw_user  = user_response.get('user', {})
    user_data = _deserialize_user(raw_user)

    if user_data.get('role') != 'responsable_departement_division':
        return Response({"status": "error", "code": "INVALID_ROLE", "message": "L'utilisateur doit être 'responsable_departement_division'."}, status=400)

    old_str_id  = raw_user.get('structure_id')
    old_str_nom = None
    if old_str_id:
        sc_old, old_resp = _call_juridique('get', f'/juridique/structure/{old_str_id}/', token)
        if sc_old == 200:
            old_str_nom = old_resp.get('data', {}).get('nom', 'Inconnue')

    # =====================================================
    # GET STRUCTURE & VERIFY TYPE
    # =====================================================

    sc_str, str_resp = _call_juridique('get', f'/juridique/structure/{structure_id}/', token)
    if sc_str == 404:
        return Response({"status": "error", "code": "STRUCTURE_NOT_FOUND",     "message": "Structure introuvable."},          status=404)
    if sc_str != 200:
        return Response({"status": "error", "code": "JURIDIQUE_SERVICE_ERROR", "message": "Service juridique indisponible."}, status=503)

    structure_data = str_resp.get('data', {})

    if structure_data.get('type') != 'departement':
        return Response({
            "status": "error",
            "code": "INVALID_STRUCTURE_TYPE",
            "message": f"La structure doit être de type 'departement' (actuel: '{structure_data.get('type')}')."
        }, status=400)

    # =====================================================
    # UPDATE USER
    # =====================================================

    sc_update, updated = _call_auth(
        'patch', f'/auth/users/{user_id}/update/', token,
        json={
            "structure_id":         structure_id,
            "division_activite_id": division_activite_id,
        }
    )
    if sc_update != 200:
        return Response({"status": "error", "code": "UPDATE_FAILED", "message": "Impossible de mettre à jour.", "detail": updated}, status=sc_update)

    sc_check, check_resp = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc_check != 200:
        return Response({"status": "error", "code": "POST_CHECK_FAILED", "message": "Impossible de vérifier."}, status=503)

    raw_user  = check_resp.get('user', {})
    full_user = _build_full_user(raw_user, token)

    return Response({
        "status": "success",
        "code": "STRUCTURE_DEPARTEMENT_REASSIGNED",
        "message": f"Structure changée de '{old_str_nom or 'aucune'}' vers '{structure_data.get('nom', structure_id)}'.",
        "data": {
            **full_user,
            "previous_structure_id":  old_str_id,
            "previous_structure_nom": old_str_nom,
            "assigned_by": {
                "id":   directeur.id,
                "name": getattr(directeur, 'nom_complet', str(directeur)),
                "role": directeur.role,
            },
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# REMOVE STRUCTURE (RESPONSABLE_DEPARTEMENT_DIVISION)
# =========================================================

@api_view(['DELETE'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def remove_structure_departement_from_user(request, user_id):
    """
    DELETE /affectation/users/<user_id>/remove-structure-departement/
    """

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, user_response = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc != 200:
        return Response({"status": "error", "code": "USER_NOT_FOUND", "message": f"Utilisateur {user_id} introuvable."}, status=404)

    raw_user = user_response.get('user', {})

    if not raw_user.get('structure_id'):
        return Response({"status": "error", "code": "NO_STRUCTURE", "message": "Aucune structure affectée."}, status=400)

    current_str_id = raw_user.get('structure_id')
    str_nom        = "Inconnue"
    sc_dir, dir_resp = _call_juridique('get', f'/juridique/structure/{current_str_id}/', token)
    if sc_dir == 200:
        str_nom = dir_resp.get('data', {}).get('nom', 'Inconnue')

    sc_update, updated = _call_auth(
        'patch', f'/auth/users/{user_id}/update/', token,
        json={
            "structure_id":         None,
            "division_activite_id": None,
        }
    )
    if sc_update != 200:
        return Response({"status": "error", "code": "REMOVE_FAILED", "message": "Impossible de supprimer.", "detail": updated}, status=sc_update)

    sc2, user_response2 = _call_auth('get', f'/auth/users/{user_id}/', token)
    if sc2 == 200:
        full_user = _build_full_user(user_response2.get('user', {}), token)
    else:
        raw_user['structure_id']         = None
        raw_user['division_activite_id'] = None
        full_user = _build_full_user(raw_user, token)

    return Response({
        "status": "success",
        "code": "STRUCTURE_DEPARTEMENT_REMOVED",
        "message": f"Structure '{str_nom}' désaffectée de {full_user.get('nom_complet')}.",
        "data": {
            **full_user,
            "removed_structure_id":  current_str_id,
            "removed_structure_nom": str_nom,
            "timestamp": datetime.now().isoformat(),
        }
    }, status=200)


# =========================================================
# LIST RESPONSABLES DEPARTEMENT DIVISION
# =========================================================

@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def api_list_responsables_departement_division(request):
    """Responsables département division NON affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_departement_division'
        and not u.get('structure_id')
    ]

    data = _build_full_users(cibles, token)
    return Response({"status": "success", "count": len(data), "data": data})


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def api_list_responsables_departement_division_affectes(request):
    """Responsables département division affectés"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_departement_division'
        and u.get('structure_id')
    ]

    data = _build_full_users(cibles, token)
    return Response({"status": "success", "count": len(data), "data": data})


@api_view(['GET'])
@authentication_classes([RemoteJWTAuthentication])
@permission_classes([IsDirecteurDivisionActivite])
def api_list_all_responsables_departement_division(request):
    """Tous les responsables département division"""

    token = request.headers.get('Authorization', '').split(' ', 1)[1].strip()

    sc, response = _call_auth('get', '/auth/users/', token)
    if sc != 200:
        return Response({"status": "error", "message": "Impossible de récupérer utilisateurs."}, status=503)

    users_raw = response.get('users', [])

    cibles = [
        u for u in users_raw
        if isinstance(u, dict)
        and u.get('role') == 'responsable_departement_division'
    ]

    data   = _build_full_users(cibles, token)
    total  = len(data)
    avec   = len([x for x in data if x.get('structure_id')])
    actifs = len([x for x in data if x.get('is_active')])

    return Response({
        "status": "success",
        "count": total,
        "statistics": {
            "with_structure":    avec,
            "without_structure": total - avec,
            "active":            actifs,
            "inactive":          total - actifs,
        },
        "data": data,
        "timestamp": datetime.now().isoformat(),
    })