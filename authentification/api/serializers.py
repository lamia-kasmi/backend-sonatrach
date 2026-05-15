
# from rest_framework import serializers
# from .models import  User
# import cloudinary.uploader
# from django.contrib.auth.hashers import make_password
# import secrets



# # ==================================================
# # USER SERIALIZER
# # ==================================================
# class UserSerializer(serializers.ModelSerializer):
#     photo_profil = serializers.ImageField(required=False)

#     class Meta:
#         model = User
#         fields = [
#             "id", "email", "nom", "prenom", "password",
#             "role", "activite_id",
#             "direction_id", "departement_id",
#             "is_staff", "is_superuser", "photo_profil"
#         ]
#         extra_kwargs = {
#             "password":     {"write_only": True, "required": False},
#             "role":         {"required": True},
#             "activite_id":    {"required": False, "allow_null": True},
#             "direction_id":    {"required": False, "allow_null": True},
#             "departement_id":  {"required": False, "allow_null": True},

#         }

#     # ==================================================
#     # VALIDATION GLOBALE
#     # ==================================================
#     def validate(self, data):
#         role         = data.get('role', getattr(self.instance, 'role', None))
#         activite_id    = data.get('activite_id')
#         direction_id   = data.get('direction_id')
#         departement_id = data.get('departement_id')
        

#         if role == 'directeur_activite':
#             if activite_id:
#                 # Fourni → on vérifie
#                 self._verify_activite(activite_id)
#             data['direction_id']   = None
#             data['departement_id'] = None
        
#         elif role == 'directeur_direction':
#             if not direction_id:
#                 raise serializers.ValidationError({
#                     "direction_id": "Obligatoire pour directeur_direction"
#                 })

            
#             data['departement_id'] = None
        
#         elif role == 'responsable_departement':
#             if not departement_id:
#                 raise serializers.ValidationError({
#                     "departement_id": "Obligatoire pour responsable_departement"
#                 })

#             if not direction_id:
#                 raise serializers.ValidationError({
#                     "direction_id": "Un département doit appartenir à une direction"
#                 })


#             if activite_id:
#                 self._verify_activite(activite_id)


#         else:
#             data['activite_id']    = None
#             data['direction_id']   = None
#             data['departement_id'] = None


#         return data
    
#     # ==================================================
#     # CREATE
#     # ==================================================
#     def create(self, validated_data):
#         photo = validated_data.pop("photo_profil", None)

#         if not validated_data.get("password"):
#             generated_password         = secrets.token_urlsafe(8)
#             validated_data["password"] = make_password(generated_password)
#             self.generated_password    = generated_password

#         if photo:
#             result = cloudinary.uploader.upload(photo)
#             validated_data["photo_profil"] = result["secure_url"]

#         user = super().create(validated_data)
#         user.generated_password = getattr(self, "generated_password", None)
#         return user

#     # ==================================================
#     # UPDATE
#     # ==================================================
#     def update(self, instance, validated_data):
#         photo = validated_data.pop("photo_profil", None)

#         if photo:
#             result = cloudinary.uploader.upload(photo)
#             validated_data["photo_profil"] = result["secure_url"]

#         password = validated_data.pop("password", None)
#         if password:
#             validated_data["password"] = make_password(password)

#         return super().update(instance, validated_data)


from rest_framework import serializers
from .models import User
import cloudinary.uploader
from django.contrib.auth.hashers import make_password
import secrets
import requests
from django.core.cache import cache
from .discovery import get_juridique_base_url, get_gateway_url
# ==================================================
# VALIDATEURS POUR LES RÉFÉRENCES MONGODB
# ==================================================

def _get_juridique_url(path: str) -> str:
    """Helper pour construire l'URL juridique"""
    try:
        base_url = get_juridique_base_url()
    except Exception:
        import os
        base_url = os.getenv('GATEWAY_URL', 'http://localhost:8083')
    return f"{base_url}{path}"


# def _juridique_get(path: str, token: str = None) -> dict | None:
#     """Helper générique GET vers le service juridique"""
#     try:
#         url     = _get_juridique_url(path)
#         headers = {'Authorization': f'Bearer {token}'} if token else {}
#         resp    = requests.get(url, headers=headers, timeout=5)
#         if resp.status_code == 200:
#             data = resp.json()
#             return data.get('data', data)
#         return None
#     except Exception:
#         return None
def _juridique_get(path: str, token: str = None) -> dict | None:
    """Helper générique GET vers le service juridique"""
    try:
        url = _get_juridique_url(path)
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        print(f"[JURIDIQUE] 🚀 GET: {url}")
        print(f"[JURIDIQUE] 📋 Headers: {headers}")
        
        resp = requests.get(url, headers=headers, timeout=5)
        
        print(f"[JURIDIQUE] 📡 Status: {resp.status_code}")
        print(f"[JURIDIQUE] 📄 Response text: {resp.text[:500]}")
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get('data', data)
            print(f"[JURIDIQUE] ✅ Success: {type(result)} - {result.get('nom') if result else 'None'}")
            return result
        else:
            print(f"[JURIDIQUE] ❌ Failed with status {resp.status_code}")
            return None
    except Exception as e:
        print(f"[JURIDIQUE] 💥 Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def verify_activite(activite_id: str, token: str = None) -> dict | None:
    return _juridique_get(f'/juridique/activites/{activite_id}/', token)


def verify_direction(direction_id: str, token: str = None) -> dict | None:
    return _juridique_get(f'/juridique/directions/{direction_id}/', token)


def verify_departement(departement_id: str, token: str = None) -> dict | None:
    return _juridique_get(f'/juridique/departements/{departement_id}/', token)


def verify_direction_centrale(direction_centrale_id: str, token: str = None) -> dict | None:
    return _juridique_get(f'/juridique/directions-centrales/{direction_centrale_id}/', token)


def verify_direction_activite(direction_activite_id: str, token: str = None) -> dict | None:
    return _juridique_get(f'/juridique/direction_activite/{direction_activite_id}/', token)


def verify_division_activite(division_activite_id: str, token: str = None) -> dict | None:
    return _juridique_get(f'/juridique/division_activite/{division_activite_id}/', token)


# def verify_structure(structure_id: str, token: str = None) -> dict | None:
#     # ✅ structures (avec s) — correspond au router Express
#     return _juridique_get(f'/juridique/structure/{structure_id}/', token)
def verify_structure(structure_id: str, token: str = None) -> dict | None:
    print(f"[DEBUG] verify_structure called with id: {structure_id}")  # ← Debug
    url_path = f'/juridique/structure/{structure_id}/'
    print(f"[DEBUG] Calling URL: {url_path}")  # ← Debug
    result = _juridique_get(url_path, token)
    print(f"[DEBUG] Result: {result}")  # ← Debug
    return result

# ==================================================
# SERIALIZERS SIMPLES (READ-ONLY)
# ==================================================

class ActiviteSimpleSerializer(serializers.Serializer):
    _id         = serializers.CharField(read_only=True)
    id          = serializers.CharField(read_only=True)
    code        = serializers.CharField(read_only=True)
    nom         = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    actif       = serializers.BooleanField(read_only=True)


class DirectionSimpleSerializer(serializers.Serializer):
    _id         = serializers.CharField(read_only=True)
    id          = serializers.CharField(read_only=True)
    code        = serializers.CharField(read_only=True)
    nom         = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    actif       = serializers.BooleanField(read_only=True)


class DepartementSimpleSerializer(serializers.Serializer):
    _id         = serializers.CharField(read_only=True)
    id          = serializers.CharField(read_only=True)
    code        = serializers.CharField(read_only=True)
    nom         = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    actif       = serializers.BooleanField(read_only=True)


class DirectionCentraleSimpleSerializer(serializers.Serializer):
    _id         = serializers.CharField(read_only=True)
    id          = serializers.CharField(read_only=True)
    code        = serializers.CharField(read_only=True)
    nom         = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    actif       = serializers.BooleanField(read_only=True)


class DirectionActiviteSimpleSerializer(serializers.Serializer):
    _id         = serializers.CharField(read_only=True)
    id          = serializers.CharField(read_only=True)
    code        = serializers.CharField(read_only=True)
    nom         = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    actif       = serializers.BooleanField(read_only=True)


class DivisionActiviteSimpleSerializer(serializers.Serializer):
    _id         = serializers.CharField(read_only=True)
    id          = serializers.CharField(read_only=True)
    code        = serializers.CharField(read_only=True)
    nom         = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    actif       = serializers.BooleanField(read_only=True)


class StructureSimpleSerializer(serializers.Serializer):
    _id         = serializers.CharField(read_only=True)
    id          = serializers.CharField(read_only=True)
    code        = serializers.CharField(read_only=True)
    nom         = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    type        = serializers.CharField(read_only=True)   # 'direction' | 'departement'
    actif       = serializers.BooleanField(read_only=True)
    division    = serializers.DictField(read_only=True, required=False, allow_null=True)


# ==================================================
# USER SERIALIZER PRINCIPAL
# ==================================================

class UserSerializer(serializers.ModelSerializer):

    # Détails juridiques enrichis (read-only)
    activite_detail           = serializers.SerializerMethodField(read_only=True)
    direction_detail          = serializers.SerializerMethodField(read_only=True)
    departement_detail        = serializers.SerializerMethodField(read_only=True)
    direction_centrale_detail = serializers.SerializerMethodField(read_only=True)
    direction_activite_detail = serializers.SerializerMethodField(read_only=True)
    division_activite_detail  = serializers.SerializerMethodField(read_only=True)
    structure_detail          = serializers.SerializerMethodField(read_only=True)

    photo_profil = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            # Identité
            "id", "email", "nom", "prenom", "password",
            "role",
            # IDs MongoDB
            "activite_id",
            "direction_id",
            "departement_id",
            "direction_centrale_id",
            "direction_activite_id",
            "division_activite_id",
            "structure_id",
            # Détails enrichis
            "activite_detail",
            "direction_detail",
            "departement_detail",
            "direction_centrale_detail",
            "direction_activite_detail",
            "division_activite_detail",
            "structure_detail",
            # Flags
            "is_staff", "is_superuser", "is_active",
            # Profil
            "photo_profil", "adresse", "date_naissance",
            "sexe", "telephone", "matricule",
        ]
        extra_kwargs = {
            "password":               {"write_only": True, "required": False},
            "role":                   {"required": True},
            "activite_id":            {"required": False, "allow_null": True},
            "direction_id":           {"required": False, "allow_null": True},
            "departement_id":         {"required": False, "allow_null": True},
            "direction_centrale_id":  {"required": False, "allow_null": True},
            "direction_activite_id":  {"required": False, "allow_null": True},
            "division_activite_id":   {"required": False, "allow_null": True},
            "structure_id":           {"required": False, "allow_null": True},
            "is_active":              {"read_only": True},
        }

    # ─────────────────────────────────────────────
    # Helper : récupère le token depuis le contexte
    # ─────────────────────────────────────────────

    # def _get_token(self) -> str | None:
    #     request = self.context.get('request')
    #     if not request:
    #         return None
    #     auth = request.headers.get('Authorization', '')
    #     if auth.startswith('Bearer '):
    #         return auth[7:]
    #     return None
    def _get_token(self) -> str | None:
        """Récupère le token depuis le contexte de la requête"""
        request = self.context.get('request')
        
        # Méthode 1: Token explicite dans le contexte
        access_token = self.context.get('access_token')
        if access_token:
            print(f"[TOKEN] Using explicit token from context: {access_token[:20]}...")
            return access_token
        
        if not request:
            print("[TOKEN] No request in context")
            return None
        
        # Méthode 2: Depuis les headers
        auth_header = None
        
        # Essayer différents endroits où le token pourrait se trouver
        if hasattr(request, 'headers'):
            auth_header = request.headers.get('Authorization', '')
            print(f"[TOKEN] From headers: {auth_header[:50] if auth_header else 'None'}")
        
        if not auth_header and hasattr(request, 'META'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            print(f"[TOKEN] From META: {auth_header[:50] if auth_header else 'None'}")
        
        if not auth_header and hasattr(request, 'auth'):
            token_obj = getattr(request.auth, 'token', None)
            if token_obj:
                auth_header = f'Bearer {token_obj}'
                print(f"[TOKEN] From auth: {auth_header[:50]}")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            print(f"[TOKEN] ✅ Token extracted: {token[:20]}...")
            return token
        
        print("[TOKEN] ❌ No valid token found")
        return None

    # ─────────────────────────────────────────────
    # SerializerMethodFields
    # ─────────────────────────────────────────────

    def get_activite_detail(self, obj):
        if not obj.activite_id:
            return None
        return verify_activite(obj.activite_id, self._get_token())

    def get_direction_detail(self, obj):
        if not obj.direction_id:
            return None
        return verify_direction(obj.direction_id, self._get_token())

    def get_departement_detail(self, obj):
        if not obj.departement_id:
            return None
        return verify_departement(obj.departement_id, self._get_token())

    def get_direction_centrale_detail(self, obj):
        if not obj.direction_centrale_id:
            return None
        return verify_direction_centrale(obj.direction_centrale_id, self._get_token())

    def get_direction_activite_detail(self, obj):
        if not obj.direction_activite_id:
            return None
        return verify_direction_activite(obj.direction_activite_id, self._get_token())

    def get_division_activite_detail(self, obj):
        if not obj.division_activite_id:
            return None
        return verify_division_activite(obj.division_activite_id, self._get_token())

    def get_structure_detail(self, obj):
        if not obj.structure_id:
            return None
        return verify_structure(obj.structure_id, self._get_token())

    # ─────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────

    def validate(self, data):
        role                  = data.get('role', getattr(self.instance, 'role', None))
        token                 = self._get_token()
        activite_id           = data.get('activite_id')
        direction_id          = data.get('direction_id')
        departement_id        = data.get('departement_id')
        direction_centrale_id = data.get('direction_centrale_id')
        direction_activite_id = data.get('direction_activite_id')
        division_activite_id  = data.get('division_activite_id')
        structure_id          = data.get('structure_id')

        def clear_all_except(*keep):
            """Met à None tous les IDs sauf ceux listés."""
            all_ids = [
                'activite_id', 'direction_id', 'departement_id',
                'direction_centrale_id', 'direction_activite_id',
                'division_activite_id', 'structure_id',
            ]
            for f in all_ids:
                if f not in keep:
                    data[f] = None

        if role == 'directeur_centrale':
            if not direction_centrale_id:
                raise serializers.ValidationError({"direction_centrale_id": "Obligatoire pour directeur_centrale."})
            if not verify_direction_centrale(direction_centrale_id, token):
                raise serializers.ValidationError({"direction_centrale_id": "Direction centrale invalide."})
            clear_all_except('direction_centrale_id')

        elif role == 'directeur_direction_activite':
            if not direction_activite_id:
                raise serializers.ValidationError({"direction_activite_id": "Obligatoire pour directeur_direction_activite."})
            if not verify_direction_activite(direction_activite_id, token):
                raise serializers.ValidationError({"direction_activite_id": "Direction activité invalide."})
            clear_all_except('direction_activite_id')

        elif role == 'directeur_division_activite':
            if not division_activite_id:
                raise serializers.ValidationError({"division_activite_id": "Obligatoire pour directeur_division_activite."})
            if not verify_division_activite(division_activite_id, token):
                raise serializers.ValidationError({"division_activite_id": "Division activité invalide."})
            clear_all_except('division_activite_id')

        elif role == 'directeur_direction':
            if not direction_id:
                raise serializers.ValidationError({"direction_id": "Obligatoire pour directeur_direction."})
            if not verify_direction(direction_id, token):
                raise serializers.ValidationError({"direction_id": "Direction invalide."})
            clear_all_except('direction_id')

        elif role == 'responsable_departement':
            if not departement_id:
                raise serializers.ValidationError({"departement_id": "Obligatoire pour responsable_departement."})
            if not verify_departement(departement_id, token):
                raise serializers.ValidationError({"departement_id": "Département invalide."})
            clear_all_except('departement_id', 'direction_id')

        elif role == 'responsable_direction_division':
            if not structure_id:
                raise serializers.ValidationError({"structure_id": "Obligatoire pour responsable_direction_division."})
            structure = verify_structure(structure_id, token)
            if not structure:
                raise serializers.ValidationError({"structure_id": "Structure invalide."})
            if structure.get('type') != 'direction':
                raise serializers.ValidationError({"structure_id": "La structure doit être de type 'direction'."})
            clear_all_except('structure_id', 'division_activite_id')

        elif role == 'responsable_departement_division':
            if not structure_id:
                raise serializers.ValidationError({"structure_id": "Obligatoire pour responsable_departement_division."})
            structure = verify_structure(structure_id, token)
            if not structure:
                raise serializers.ValidationError({"structure_id": "Structure invalide."})
            if structure.get('type') != 'departement':
                raise serializers.ValidationError({"structure_id": "La structure doit être de type 'departement'."})
            clear_all_except('structure_id', 'division_activite_id')

        return data

    # ─────────────────────────────────────────────
    # Create / Update
    # ─────────────────────────────────────────────

    def create(self, validated_data):
        photo = validated_data.pop("photo_profil", None)

        if not validated_data.get("password"):
            generated          = secrets.token_urlsafe(8)
            validated_data["password"] = make_password(generated)
            self.generated_password    = generated

        if photo:
            result = cloudinary.uploader.upload(photo)
            validated_data["photo_profil"] = result["secure_url"]

        user = super().create(validated_data)
        user.generated_password = getattr(self, "generated_password", None)
        return user

    def update(self, instance, validated_data):
        photo    = validated_data.pop("photo_profil", None)
        password = validated_data.pop("password", None)

        if photo:
            result = cloudinary.uploader.upload(photo)
            validated_data["photo_profil"] = result["secure_url"]

        if password:
            validated_data["password"] = make_password(password)

        return super().update(instance, validated_data)


# ==================================================
# SERIALIZER LISTE (VERSION LÉGÈRE)
# ==================================================

class UserListSerializer(serializers.ModelSerializer):
    nom_complet   = serializers.SerializerMethodField()
    structure_nom = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            "id", "email", "nom", "prenom", "nom_complet",
            "role", "matricule", "is_active", "structure_nom",
        ]

    def _get_token(self):
        request = self.context.get('request')
        if request:
            auth = request.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                return auth[7:]
        return None

    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}".strip()

    def get_structure_nom(self, obj):
        if not obj.structure_id:
            return None
        structure = verify_structure(obj.structure_id, self._get_token())
        return structure.get('nom') if structure else None


# ==================================================
# SERIALIZER RÉPONSE LOGIN
# ==================================================

class UserLoginResponseSerializer(serializers.Serializer):
    status      = serializers.CharField()
    message     = serializers.CharField()
    refresh     = serializers.CharField()
    access      = serializers.CharField()
    user_id     = serializers.CharField()
    role        = serializers.CharField(allow_null=True)
    nom_complet = serializers.CharField()
    photo_profil = serializers.CharField(allow_null=True)

    # IDs
    activite_id           = serializers.CharField(allow_null=True)
    direction_id          = serializers.CharField(allow_null=True)
    departement_id        = serializers.CharField(allow_null=True)
    direction_centrale_id = serializers.CharField(allow_null=True)
    structure_id          = serializers.CharField(allow_null=True)
    direction_activite_id = serializers.CharField(allow_null=True)
    division_activite_id  = serializers.CharField(allow_null=True)

    # Données enrichies
    activite_detail           = serializers.DictField(allow_null=True, required=False)
    direction_detail          = serializers.DictField(allow_null=True, required=False)
    departement_detail        = serializers.DictField(allow_null=True, required=False)
    direction_centrale_detail = serializers.DictField(allow_null=True, required=False)
    direction_activite_detail = serializers.DictField(allow_null=True, required=False)
    division_activite_detail  = serializers.DictField(allow_null=True, required=False)
    structure_detail          = serializers.DictField(allow_null=True, required=False)