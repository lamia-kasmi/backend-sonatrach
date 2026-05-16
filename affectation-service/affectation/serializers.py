


# # serializers.py — Service Affectation
# # Lecture seule — miroir exact des réponses JSON du service d'authentification
# # Basé sur views.py du service auth (api_get_user, api_list_users, api_login...)
# # Aucun modèle User local — appels via discovery.py

# from rest_framework import serializers
# import requests
# from .discovery import get_auth_base_url


# # ══════════════════════════════════════════════════════════════════════
# # BLOC COMMUN — champs organisationnels partagés par tous les endpoints
# # ══════════════════════════════════════════════════════════════════════
# ORG_FIELDS = [
#     'activite_id',
#     'direction_id',
#     'departement_id',
#     'direction_centrale_id',
#     'direction_division_id',
#     'departement_division_id',
#     'direction_activite_id',
#     'division_activite_id',
# ]


# # ══════════════════════════════════════════════════════════════════════
# # 1. USER SUMMARY
# #    Correspond à la réponse de api_list_users / api_list_all_users_public
# #    Utilisé en nested dans les listes d'affectations (léger)
# # ══════════════════════════════════════════════════════════════════════
# class UserSummarySerializer(serializers.Serializer):
#     """
#     Shape retournée par api_list_users / api_list_all_users_public :
#     {
#         "id", "email", "nom", "prenom", "nom_complet",
#         "role", "role_display", "matricule", "telephone",
#         "activite_id", ...(org ids)..., "is_active", "photo_profil"
#     }
#     """
#     id           = serializers.IntegerField(read_only=True)
#     email        = serializers.EmailField(read_only=True)
#     nom          = serializers.CharField(read_only=True)
#     prenom       = serializers.CharField(read_only=True)
#     nom_complet  = serializers.CharField(read_only=True)
#     role         = serializers.CharField(read_only=True, allow_null=True)
#     role_display = serializers.CharField(read_only=True, allow_null=True)
#     matricule    = serializers.CharField(read_only=True, allow_null=True)
#     telephone    = serializers.CharField(read_only=True, allow_null=True)
#     is_active    = serializers.BooleanField(read_only=True)
#     is_superuser = serializers.BooleanField(read_only=True, required=False)
#     photo_profil = serializers.CharField(read_only=True, allow_null=True)

#     # IDs organisationnels
#     activite_id             = serializers.CharField(read_only=True, allow_null=True)
#     direction_id            = serializers.CharField(read_only=True, allow_null=True)
#     departement_id          = serializers.CharField(read_only=True, allow_null=True)
#     direction_centrale_id   = serializers.CharField(read_only=True, allow_null=True)
#     direction_division_id   = serializers.CharField(read_only=True, allow_null=True)
#     departement_division_id = serializers.CharField(read_only=True, allow_null=True)
#     direction_activite_id   = serializers.CharField(read_only=True, allow_null=True)
#     division_activite_id    = serializers.CharField(read_only=True, allow_null=True)


# # ══════════════════════════════════════════════════════════════════════
# # 2. USER DETAIL
# #    Correspond à la réponse de api_get_user (vue détail)
# #    Inclut account_stats, admin_info/other_info, groups, age...
# # ══════════════════════════════════════════════════════════════════════
# class AccountStatsSerializer(serializers.Serializer):
#     has_photo       = serializers.BooleanField(read_only=True)
#     has_matricule   = serializers.BooleanField(read_only=True)
#     has_telephone   = serializers.BooleanField(read_only=True)
#     has_adresse     = serializers.BooleanField(read_only=True)
#     profile_complete = serializers.BooleanField(read_only=True)


# class AdminInfoSerializer(serializers.Serializer):
#     is_admin         = serializers.BooleanField(read_only=True)
#     has_full_access  = serializers.BooleanField(read_only=True)
#     can_manage_users = serializers.BooleanField(read_only=True)
#     can_manage_roles = serializers.BooleanField(read_only=True)


# class OtherInfoSerializer(serializers.Serializer):
#     role_type             = serializers.CharField(read_only=True, allow_null=True)
#     needs_role_assignment = serializers.BooleanField(read_only=True)


# class UserDetailSerializer(serializers.Serializer):
#     """
#     Shape retournée par api_get_user (réponse dans la clé "user") :
#     {
#         "id", "email", "nom", "prenom", "nom_complet",
#         "role", "role_display", "is_active", "is_staff", "is_superuser",
#         "matricule", "telephone", "adresse",
#         "sexe", "sexe_display", "date_naissance", "age",
#         ...(org ids)...,
#         "photo_profil", "last_login", "date_joined",
#         "groups", "user_permissions",
#         "account_stats", "admin_info" | "other_info"
#     }
#     """
#     # ── Identité ──────────────────────────────────────────────────────
#     id          = serializers.IntegerField(read_only=True)
#     email       = serializers.EmailField(read_only=True)
#     nom         = serializers.CharField(read_only=True)
#     prenom      = serializers.CharField(read_only=True)
#     nom_complet = serializers.CharField(read_only=True)

#     # ── Rôle & flags ──────────────────────────────────────────────────
#     role         = serializers.CharField(read_only=True, allow_null=True)
#     role_display = serializers.CharField(read_only=True, allow_null=True)
#     is_active    = serializers.BooleanField(read_only=True)
#     is_staff     = serializers.BooleanField(read_only=True)
#     is_superuser = serializers.BooleanField(read_only=True)

#     # ── Informations professionnelles ─────────────────────────────────
#     matricule = serializers.CharField(read_only=True, allow_null=True)
#     telephone = serializers.CharField(read_only=True, allow_null=True)
#     adresse   = serializers.CharField(read_only=True, allow_null=True)

#     # ── Informations personnelles ─────────────────────────────────────
#     sexe           = serializers.CharField(read_only=True, allow_null=True)
#     sexe_display   = serializers.CharField(read_only=True, allow_null=True)
#     date_naissance = serializers.DateField(read_only=True, allow_null=True)
#     age            = serializers.IntegerField(read_only=True, allow_null=True)

#     # ── IDs organisationnels ──────────────────────────────────────────
#     activite_id             = serializers.CharField(read_only=True, allow_null=True)
#     direction_id            = serializers.CharField(read_only=True, allow_null=True)
#     departement_id          = serializers.CharField(read_only=True, allow_null=True)
#     direction_centrale_id   = serializers.CharField(read_only=True, allow_null=True)
#     direction_division_id   = serializers.CharField(read_only=True, allow_null=True)
#     departement_division_id = serializers.CharField(read_only=True, allow_null=True)
#     direction_activite_id   = serializers.CharField(read_only=True, allow_null=True)
#     division_activite_id    = serializers.CharField(read_only=True, allow_null=True)

#     # ── Médias & dates système ────────────────────────────────────────
#     photo_profil = serializers.CharField(read_only=True, allow_null=True)
#     last_login   = serializers.DateTimeField(read_only=True, allow_null=True)
#     date_joined  = serializers.DateTimeField(read_only=True, allow_null=True)

#     # ── Groupes & permissions ─────────────────────────────────────────
#     groups           = serializers.ListField(child=serializers.DictField(), read_only=True, required=False)
#     user_permissions = serializers.ListField(child=serializers.DictField(), read_only=True, required=False)

#     # ── Statistiques & infos rôle ─────────────────────────────────────
#     account_stats = AccountStatsSerializer(read_only=True, required=False)
#     admin_info    = AdminInfoSerializer(read_only=True, required=False)
#     other_info    = OtherInfoSerializer(read_only=True, required=False)


# # ══════════════════════════════════════════════════════════════════════
# # 3. USER BY ID
# #    Correspond à api_get_user_by_id (format plus compact, sans metadata)
# # ══════════════════════════════════════════════════════════════════════
# class UserByIdSerializer(serializers.Serializer):
#     """
#     Shape retournée par api_get_user_by_id :
#     {
#         "id", "email", "nom", "prenom", "nom_complet",
#         "role", "role_display",
#         ...(org ids)...,
#         "is_active", "is_staff", "is_superuser", "photo_profil"
#     }
#     """
#     id           = serializers.IntegerField(read_only=True)
#     email        = serializers.EmailField(read_only=True)
#     nom          = serializers.CharField(read_only=True)
#     prenom       = serializers.CharField(read_only=True)
#     nom_complet  = serializers.CharField(read_only=True)
#     role         = serializers.CharField(read_only=True, allow_null=True)
#     role_display = serializers.CharField(read_only=True, allow_null=True)
#     is_active    = serializers.BooleanField(read_only=True)
#     is_staff     = serializers.BooleanField(read_only=True)
#     is_superuser = serializers.BooleanField(read_only=True)
#     photo_profil = serializers.CharField(read_only=True, allow_null=True)

#     activite_id             = serializers.CharField(read_only=True, allow_null=True)
#     direction_id            = serializers.CharField(read_only=True, allow_null=True)
#     departement_id          = serializers.CharField(read_only=True, allow_null=True)
#     direction_centrale_id   = serializers.CharField(read_only=True, allow_null=True)
#     direction_division_id   = serializers.CharField(read_only=True, allow_null=True)
#     departement_division_id = serializers.CharField(read_only=True, allow_null=True)
#     direction_activite_id   = serializers.CharField(read_only=True, allow_null=True)
#     division_activite_id    = serializers.CharField(read_only=True, allow_null=True)


# # ══════════════════════════════════════════════════════════════════════
# # 4. USER ME (profil propre)
# #    Correspond à api_get_own_profile (clé "data")
# # ══════════════════════════════════════════════════════════════════════
# class UserMeSerializer(serializers.Serializer):
#     """
#     Shape retournée par api_get_own_profile (clé "data") :
#     Inclut date_joined, last_login, tous les org ids, sexe, adresse...
#     """
#     id          = serializers.IntegerField(read_only=True)
#     email       = serializers.EmailField(read_only=True)
#     nom         = serializers.CharField(read_only=True)
#     prenom      = serializers.CharField(read_only=True)
#     nom_complet = serializers.CharField(read_only=True)
#     role        = serializers.CharField(read_only=True, allow_null=True)
#     adresse     = serializers.CharField(read_only=True, allow_null=True)
#     telephone   = serializers.CharField(read_only=True, allow_null=True)
#     matricule   = serializers.CharField(read_only=True, allow_null=True)
#     sexe        = serializers.CharField(read_only=True, allow_null=True)

#     date_naissance = serializers.DateField(read_only=True, allow_null=True)
#     is_active      = serializers.BooleanField(read_only=True)
#     photo_profil   = serializers.CharField(read_only=True, allow_null=True)
#     date_joined    = serializers.DateTimeField(read_only=True, allow_null=True)
#     last_login     = serializers.DateTimeField(read_only=True, allow_null=True)

#     activite_id             = serializers.CharField(read_only=True, allow_null=True)
#     direction_id            = serializers.CharField(read_only=True, allow_null=True)
#     departement_id          = serializers.CharField(read_only=True, allow_null=True)
#     direction_centrale_id   = serializers.CharField(read_only=True, allow_null=True)
#     direction_division_id   = serializers.CharField(read_only=True, allow_null=True)
#     departement_division_id = serializers.CharField(read_only=True, allow_null=True)
#     direction_activite_id   = serializers.CharField(read_only=True, allow_null=True)
#     division_activite_id    = serializers.CharField(read_only=True, allow_null=True)


# # ══════════════════════════════════════════════════════════════════════
# # 5. AFFECTATION SERIALIZER
# #    Entité principale du service affectation
# #    Le champ `user` est enrichi dynamiquement depuis le service auth
# # ══════════════════════════════════════════════════════════════════════
# class AffectationSerializer(serializers.Serializer):
#     """
#     Sérialise une affectation en lecture seule.

#     Utilisation :
#         # Liste  → user summary (léger)
#         AffectationSerializer(queryset, many=True)

#         # Détail → user complet avec account_stats etc.
#         AffectationSerializer(instance, context={'detail': True})
#     """
#     id         = serializers.IntegerField(read_only=True)
#     poste      = serializers.CharField(read_only=True)
#     date_debut = serializers.DateField(read_only=True)
#     date_fin   = serializers.DateField(read_only=True, allow_null=True)
#     statut     = serializers.CharField(read_only=True)
#     user_id    = serializers.IntegerField(read_only=True)

#     # Résolu dynamiquement selon le context
#     user = serializers.SerializerMethodField()

#     def get_user(self, obj):
#         user_id = obj.get('user_id') if isinstance(obj, dict) else getattr(obj, 'user_id', None)
#         if not user_id:
#             return None

#         is_detail = self.context.get('detail', False)

#         if is_detail:
#             # Appel api_get_user → enveloppé dans {"user": {...}}
#             data = fetch_user_detail(user_id)
#             if data:
#                 s = UserDetailSerializer(data=data)
#                 return s.data if s.is_valid() else None
#         else:
#             # Appel api_get_user_by_id → réponse directe (flat)
#             data = fetch_user_by_id(user_id)
#             if data:
#                 s = UserByIdSerializer(data=data)
#                 return s.data if s.is_valid() else None

#         return None


# # ══════════════════════════════════════════════════════════════════════
# # 6. WRAPPERS DE RÉPONSE
# #    Désérialisent les enveloppes {"status", "user": {...}} retournées
# #    par le service auth
# # ══════════════════════════════════════════════════════════════════════
# class AuthUserDetailResponseSerializer(serializers.Serializer):
#     """Enveloppe complète de api_get_user : {"status", "code", "message", "user": {...}}"""
#     status  = serializers.CharField(read_only=True)
#     code    = serializers.CharField(read_only=True)
#     message = serializers.CharField(read_only=True)
#     user    = UserDetailSerializer(read_only=True)


# class AuthUsersListResponseSerializer(serializers.Serializer):
#     """Enveloppe complète de api_list_users : {"status", "count", "total_users", "users": [...]}"""
#     status      = serializers.CharField(read_only=True)
#     count       = serializers.IntegerField(read_only=True)
#     total_users = serializers.IntegerField(read_only=True, required=False)
#     users       = UserSummarySerializer(many=True, read_only=True)


# # ══════════════════════════════════════════════════════════════════════
# # HELPERS — fetch functions pour les views du service affectation
# # ══════════════════════════════════════════════════════════════════════

# def fetch_user_by_id(user_id: int) -> dict | None:
#     """
#     Appelle api_get_user_by_id → GET /api/users/<id>/by-id/
#     Retourne le dict plat (sans enveloppe status/code).

#     Utilisé pour les listes d'affectations (UserByIdSerializer).
#     """
#     try:
#         url = f'{get_auth_base_url()}/api/users/{user_id}/by-id/'
#         resp = requests.get(url, timeout=3, headers={'Accept': 'application/json'})
#         if resp.status_code == 200:
#             return resp.json()
#         print(f'[AUTH] ⚠️ fetch_user_by_id({user_id}) → HTTP {resp.status_code}')
#     except Exception as e:
#         print(f'[AUTH] ❌ fetch_user_by_id({user_id}): {e}')
#     return None


# def fetch_user_detail(user_id: int) -> dict | None:
#     """
#     Appelle api_get_user → GET /api/users/<id>/
#     Extrait et retourne uniquement la clé "user" de l'enveloppe.

#     Utilisé pour les vues détail d'affectation (UserDetailSerializer).
#     """
#     try:
#         url = f'{get_auth_base_url()}/api/users/{user_id}/'
#         resp = requests.get(url, timeout=3, headers={'Accept': 'application/json'})
#         if resp.status_code == 200:
#             return resp.json().get('user')  # extrait la clé "user" de l'enveloppe
#         print(f'[AUTH] ⚠️ fetch_user_detail({user_id}) → HTTP {resp.status_code}')
#     except Exception as e:
#         print(f'[AUTH] ❌ fetch_user_detail({user_id}): {e}')
#     return None


# def fetch_users_list(filters: dict = None) -> list[dict]:
#     """
#     Appelle api_list_users → GET /api/users/
#     Extrait la clé "users" de l'enveloppe et valide chaque entrée.

#     Filtres supportés (query params) :
#         fetch_users_list({'role': 'agent'})
#         fetch_users_list({'role': 'directeur_direction', 'is_active': True})
#         fetch_users_list({'activite_id': '6639abc...'})

#     Retourne une liste de dicts validés par UserSummarySerializer.
#     """
#     try:
#         url = f'{get_auth_base_url()}/api/users/'
#         resp = requests.get(
#             url,
#             params=filters or {},
#             timeout=5,
#             headers={'Accept': 'application/json'},
#         )
#         if resp.status_code == 200:
#             data = resp.json()
#             # api_list_users retourne {"status", "count", "total_users", "users": [...]}
#             items = data.get('users', data) if isinstance(data, dict) else data
#             s = UserSummarySerializer(data=items, many=True)
#             if s.is_valid():
#                 return s.data
#             print(f'[AUTH] ⚠️ Validation errors: {s.errors}')
#     except Exception as e:
#         print(f'[AUTH] ❌ fetch_users_list({filters}): {e}')
#     return []


# def fetch_user_me(access_token: str) -> dict | None:
#     """
#     Appelle api_get_own_profile → GET /api/users/me/
#     Nécessite le JWT de l'utilisateur dans Authorization header.
#     Extrait la clé "data" de l'enveloppe.

#     Utile si le service affectation doit agir au nom de l'utilisateur connecté.
#     """
#     try:
#         url = f'{get_auth_base_url()}/api/users/me/'
#         resp = requests.get(
#             url,
#             timeout=3,
#             headers={
#                 'Accept': 'application/json',
#                 'Authorization': f'Bearer {access_token}',
#             },
#         )
#         if resp.status_code == 200:
#             return resp.json().get('data')  # extrait la clé "data"
#         print(f'[AUTH] ⚠️ fetch_user_me → HTTP {resp.status_code}')
#     except Exception as e:
#         print(f'[AUTH] ❌ fetch_user_me: {e}')
#     return None
# serializers.py — Service Affectation
# Lecture seule — miroir exact des réponses JSON du service d'authentification
# Basé sur views.py du service auth (api_get_user, api_list_users, api_login...)
# Aucun modèle User local — appels via discovery.py

from rest_framework import serializers
import requests
from .discovery import get_auth_base_url


# ══════════════════════════════════════════════════════════════════════
# NOTE IMPORTANTE — read_only vs required=False
# ══════════════════════════════════════════════════════════════════════
# Ces serializers sont utilisés en MODE DÉSÉRIALISATION uniquement :
#   s = UserSummarySerializer(data=dict_from_auth_service)
#   s.is_valid()
#   user = s.data
#
# En DRF, read_only=True sur un champ utilisé avec data= cause deux problèmes :
#   1. Le champ est ignoré lors de la validation → absent de s.data
#   2. Si le champ est requis (required=True, défaut), is_valid() retourne False
#
# Solution : NE PAS utiliser read_only=True ici. Utiliser required=False + allow_null=True.
# ══════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════
# CHAMPS ORGANISATIONNELS — partagés par tous les serializers
# ══════════════════════════════════════════════════════════════════════
ORG_FIELDS = [
    'activite_id',
    'direction_id',
    'departement_id',
    'direction_centrale_id',
    'direction_division_id',
    'departement_division_id',
    'direction_activite_id',
    'division_activite_id',
]


# ══════════════════════════════════════════════════════════════════════
# MIXIN — IDs organisationnels (évite la répétition)
# ══════════════════════════════════════════════════════════════════════
class OrgFieldsMixin:
    """
    Mixin qui déclare tous les champs d'IDs organisationnels.
    À inclure dans chaque serializer via héritage multiple.
    """
    activite_id             = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    direction_id            = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    departement_id          = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    direction_centrale_id   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    direction_division_id   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    departement_division_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    direction_activite_id   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    division_activite_id    = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    structure_id            = serializers.CharField(required=False, allow_null=True, allow_blank=True)

# ══════════════════════════════════════════════════════════════════════
# 1. USER SUMMARY
#    Correspond à la réponse de api_list_users / api_list_all_users_public
#    Utilisé en nested dans les listes d'affectations (léger)
# ══════════════════════════════════════════════════════════════════════
class UserSummarySerializer(OrgFieldsMixin, serializers.Serializer):
    """
    Shape retournée par api_list_users / api_list_all_users_public :
    {
        "id", "email", "nom", "prenom", "nom_complet",
        "role", "role_display", "matricule", "telephone",
        "activite_id", ...(org ids)..., "is_active", "photo_profil"
    }
    """
    id           = serializers.IntegerField(required=True)
    email        = serializers.EmailField(required=True)
    nom          = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    prenom       = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    nom_complet  = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    role         = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    role_display = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    matricule    = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    telephone    = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_active    = serializers.BooleanField(required=False, default=True)
    is_superuser = serializers.BooleanField(required=False, default=False)
    photo_profil = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Champs présents dans api_list_users mais pas toujours dans api_list_all_users_public
    adresse      = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sexe         = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sexe_display = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_naissance = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    last_login   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_staff     = serializers.BooleanField(required=False, default=False)


# ══════════════════════════════════════════════════════════════════════
# 2. USER DETAIL
#    Correspond à la réponse de api_get_user (vue détail)
#    Inclut account_stats, admin_info/other_info, groups, age...
# ══════════════════════════════════════════════════════════════════════
class AccountStatsSerializer(serializers.Serializer):
    has_photo        = serializers.BooleanField(required=False, default=False)
    has_matricule    = serializers.BooleanField(required=False, default=False)
    has_telephone    = serializers.BooleanField(required=False, default=False)
    has_adresse      = serializers.BooleanField(required=False, default=False)
    profile_complete = serializers.BooleanField(required=False, default=False)


class AdminInfoSerializer(serializers.Serializer):
    is_admin         = serializers.BooleanField(required=False, default=False)
    has_full_access  = serializers.BooleanField(required=False, default=False)
    can_manage_users = serializers.BooleanField(required=False, default=False)
    can_manage_roles = serializers.BooleanField(required=False, default=False)


class OtherInfoSerializer(serializers.Serializer):
    role_type             = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    needs_role_assignment = serializers.BooleanField(required=False, default=False)


class UserDetailSerializer(OrgFieldsMixin, serializers.Serializer):
    """
    Shape retournée par api_get_user (réponse dans la clé "user") :
    {
        "id", "email", "nom", "prenom", "nom_complet",
        "role", "role_display", "is_active", "is_staff", "is_superuser",
        "matricule", "telephone", "adresse",
        "sexe", "sexe_display", "date_naissance", "age",
        ...(org ids)...,
        "photo_profil", "last_login", "date_joined",
        "groups", "user_permissions",
        "account_stats", "admin_info" | "other_info"
    }
    """
    # ── Identité ──────────────────────────────────────────────────────
    id          = serializers.IntegerField(required=True)
    email       = serializers.EmailField(required=True)
    nom         = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    prenom      = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    nom_complet = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # ── Rôle & flags ──────────────────────────────────────────────────
    role         = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    role_display = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_active    = serializers.BooleanField(required=False, default=True)
    is_staff     = serializers.BooleanField(required=False, default=False)
    is_superuser = serializers.BooleanField(required=False, default=False)

    # ── Informations professionnelles ─────────────────────────────────
    matricule = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    telephone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    adresse   = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # ── Informations personnelles ─────────────────────────────────────
    sexe           = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sexe_display   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_naissance = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    age            = serializers.IntegerField(required=False, allow_null=True)

    # ── Médias & dates système ────────────────────────────────────────
    photo_profil = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    last_login   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_joined  = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # ── Groupes & permissions ─────────────────────────────────────────
    groups           = serializers.ListField(child=serializers.DictField(), required=False, default=list)
    user_permissions = serializers.ListField(child=serializers.DictField(), required=False, default=list)

    # ── Statistiques & infos rôle ─────────────────────────────────────
    account_stats = AccountStatsSerializer(required=False)
    admin_info    = AdminInfoSerializer(required=False)
    other_info    = OtherInfoSerializer(required=False)


# ══════════════════════════════════════════════════════════════════════
# 3. USER BY ID
#    Correspond à api_get_user_by_id (format plus compact, sans metadata)
# ══════════════════════════════════════════════════════════════════════
class UserByIdSerializer(OrgFieldsMixin, serializers.Serializer):
    """
    Shape retournée par api_get_user_by_id :
    {
        "id", "email", "nom", "prenom", "nom_complet",
        "role", "role_display",
        ...(org ids)...,
        "is_active", "is_staff", "is_superuser", "photo_profil"
    }
    """
    id           = serializers.IntegerField(required=True)
    email        = serializers.EmailField(required=True)
    nom          = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    prenom       = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    nom_complet  = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    role         = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    role_display = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_active    = serializers.BooleanField(required=False, default=True)
    is_staff     = serializers.BooleanField(required=False, default=False)
    is_superuser = serializers.BooleanField(required=False, default=False)
    photo_profil = serializers.CharField(required=False, allow_null=True, allow_blank=True)


# ══════════════════════════════════════════════════════════════════════
# 4. USER ME (profil propre)
#    Correspond à api_get_own_profile (clé "data")
# ══════════════════════════════════════════════════════════════════════
class UserMeSerializer(OrgFieldsMixin, serializers.Serializer):
    """
    Shape retournée par api_get_own_profile (clé "data")
    """
    id          = serializers.IntegerField(required=True)
    email       = serializers.EmailField(required=True)
    nom         = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    prenom      = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    nom_complet = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    role        = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    adresse     = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    telephone   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    matricule   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sexe        = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    date_naissance = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_active      = serializers.BooleanField(required=False, default=True)
    photo_profil   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_joined    = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    last_login     = serializers.CharField(required=False, allow_null=True, allow_blank=True)


# ══════════════════════════════════════════════════════════════════════
# 5. AFFECTATION SERIALIZER
# ══════════════════════════════════════════════════════════════════════
class AffectationSerializer(serializers.Serializer):
    """
    Sérialise une affectation en lecture seule.
    """
    id         = serializers.IntegerField(required=False)
    poste      = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_debut = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_fin   = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    statut     = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user_id    = serializers.IntegerField(required=False, allow_null=True)
    user       = serializers.SerializerMethodField()

    def get_user(self, obj):
        user_id = obj.get('user_id') if isinstance(obj, dict) else getattr(obj, 'user_id', None)
        if not user_id:
            return None

        is_detail = self.context.get('detail', False)

        if is_detail:
            data = fetch_user_detail(user_id)
            if data:
                s = UserDetailSerializer(data=data)
                return s.data if s.is_valid() else data
        else:
            data = fetch_user_by_id(user_id)
            if data:
                s = UserByIdSerializer(data=data)
                return s.data if s.is_valid() else data

        return None


# ══════════════════════════════════════════════════════════════════════
# 6. WRAPPERS DE RÉPONSE
# ══════════════════════════════════════════════════════════════════════
class AuthUserDetailResponseSerializer(serializers.Serializer):
    """Enveloppe complète de api_get_user : {"status", "code", "message", "user": {...}}"""
    status  = serializers.CharField(required=False)
    code    = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    message = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user    = UserDetailSerializer(required=False)


class AuthUsersListResponseSerializer(serializers.Serializer):
    """Enveloppe complète de api_list_users : {"status", "count", "total_users", "users": [...]}"""
    status      = serializers.CharField(required=False)
    count       = serializers.IntegerField(required=False)
    total_users = serializers.IntegerField(required=False)
    users       = UserSummarySerializer(many=True, required=False, default=list)


# ══════════════════════════════════════════════════════════════════════
# HELPERS — fetch functions pour les views du service affectation
# ══════════════════════════════════════════════════════════════════════

def fetch_user_by_id(user_id: int) -> dict | None:
    """
    Appelle api_get_user_by_id → GET /api/users/<id>/by-id/
    Retourne le dict plat (sans enveloppe status/code).
    """
    try:
        url = f'{get_auth_base_url()}/api/users/{user_id}/by-id/'
        resp = requests.get(url, timeout=3, headers={'Accept': 'application/json'})
        if resp.status_code == 200:
            return resp.json()
        print(f'[AUTH] ⚠️ fetch_user_by_id({user_id}) → HTTP {resp.status_code}')
    except Exception as e:
        print(f'[AUTH] ❌ fetch_user_by_id({user_id}): {e}')
    return None


def fetch_user_detail(user_id: int) -> dict | None:
    """
    Appelle api_get_user → GET /api/users/<id>/
    Extrait et retourne uniquement la clé "user" de l'enveloppe.
    """
    try:
        url = f'{get_auth_base_url()}/api/users/{user_id}/'
        resp = requests.get(url, timeout=3, headers={'Accept': 'application/json'})
        if resp.status_code == 200:
            return resp.json().get('user')
        print(f'[AUTH] ⚠️ fetch_user_detail({user_id}) → HTTP {resp.status_code}')
    except Exception as e:
        print(f'[AUTH] ❌ fetch_user_detail({user_id}): {e}')
    return None


def fetch_users_list(filters: dict = None) -> list[dict]:
    """
    Appelle api_list_users → GET /api/users/
    Extrait la clé "users" et valide chaque entrée.
    """
    try:
        url = f'{get_auth_base_url()}/api/users/'
        resp = requests.get(
            url,
            params=filters or {},
            timeout=5,
            headers={'Accept': 'application/json'},
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('users', data) if isinstance(data, dict) else data
            s = UserSummarySerializer(data=items, many=True)
            if s.is_valid():
                return list(s.data)
            print(f'[AUTH] ⚠️ Validation errors: {s.errors}')
            return items  # fallback : retourner les données brutes
    except Exception as e:
        print(f'[AUTH] ❌ fetch_users_list({filters}): {e}')
    return []


def fetch_user_me(access_token: str) -> dict | None:
    """
    Appelle api_get_own_profile → GET /api/users/me/
    Extrait la clé "data" de l'enveloppe.
    """
    try:
        url = f'{get_auth_base_url()}/api/users/me/'
        resp = requests.get(
            url,
            timeout=3,
            headers={
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
            },
        )
        if resp.status_code == 200:
            return resp.json().get('data')
        print(f'[AUTH] ⚠️ fetch_user_me → HTTP {resp.status_code}')
    except Exception as e:
        print(f'[AUTH] ❌ fetch_user_me: {e}')
    return None
