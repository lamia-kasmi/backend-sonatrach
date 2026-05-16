
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from datetime import datetime

from .models import User

# views.py
from .serializers import UserSerializer, UserLoginResponseSerializer
# ==========================
# UTILS
# ==========================
def nom_complet(obj):
    return f"{obj.prenom} {obj.nom}"


# ==========================
# LOGIN API (JWT)
# ==========================

# @api_view(['POST'])
# def api_login(request):
#     data = request.data
#     email = data.get('email')
#     password = data.get('password')

#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     if not user.check_password(password):
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     refresh = RefreshToken.for_user(user)
#     #code ajouter
    
#     refresh['activite_id']    = str(user.activite_id)    if user.activite_id    else None
#     refresh['direction_id']   = str(user.direction_id)   if user.direction_id else None   # ✅ NEW
#     refresh['role']         = user.role
#     refresh['user_id']      = str(user.id)


#     return Response({
#         "status": "success",
#         "role": getattr(user, 'role', None),
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#         "user_id":str(user.id),
#         "message": f"Logged in as {nom_complet(user)}",
#         "nom_complet": nom_complet(user),
#         "photo_profil": user.photo_profil.url if user.photo_profil else None,   # ✅
#         "activite_id":    str(user.activite_id)    if user.activite_id    else None,   # ✅
#         "direction_id":   str(user.direction_id)   if user.direction_id else None,   # ✅ NEW
#         "departement_id": str(user.departement_id) if user.departement_id else None   # ✅ NEW

#     })
# @api_view(['POST'])
# def api_login(request):
#     data = request.data
#     email = data.get('email')
#     password = data.get('password')

#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     if not user.check_password(password):
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     refresh = RefreshToken.for_user(user)
    
#     # ✅ Ajouter tous les champs dans le refresh token
#     refresh['user_id'] = str(user.id)
#     refresh['role'] = user.role
#     refresh['activite_id'] = str(user.activite_id) if user.activite_id else None
#     refresh['direction_id'] = str(user.direction_id) if user.direction_id else None
#     refresh['departement_id'] = str(user.departement_id) if user.departement_id else None
#     refresh['direction_centrale_id'] = str(user.direction_centrale_id) if user.direction_centrale_id else None
#     refresh['structure_id'] = str(user.structure_id) if user.structure_id else None

#     # refresh['direction_division_id'] = str(user.direction_division_id) if user.direction_division_id else None
#     # refresh['departement_division_id'] = str(user.departement_division_id) if user.departement_division_id else None
#     refresh['direction_activite_id'] = str(user.direction_activite_id) if user.direction_activite_id else None
#     refresh['division_activite_id'] = str(user.division_activite_id) if user.division_activite_id else None

#     # ✅ Les mêmes champs seront automatiquement dans l'access token
#     # car refresh.access_token copie les claims du refresh

#     return Response({
#         "status": "success",
#         "role": user.role,
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#         "user_id": str(user.id),
#         "message": f"Logged in as {nom_complet(user)}",
#         "nom_complet": nom_complet(user),
#         "photo_profil": user.photo_profil.url if user.photo_profil else None,
#         "activite_id": str(user.activite_id) if user.activite_id else None,
#         "direction_id": str(user.direction_id) if user.direction_id else None,
#         "departement_id": str(user.departement_id) if user.departement_id else None,
#         "direction_centrale_id": str(user.direction_centrale_id) if user.direction_centrale_id else None,
#         "structure_id": str(user.structure_id) if user.structure_id else None,

#         # "direction_division_id": str(user.direction_division_id) if user.direction_division_id else None,
#         # "departement_division_id": str(user.departement_division_id) if user.departement_division_id else None,
#         "direction_activite_id": str(user.direction_activite_id) if user.direction_activite_id else None,
#         "division_activite_id": str(user.division_activite_id) if user.division_activite_id else None,
#     })

# @api_view(['POST'])
# def api_login(request):
#     data = request.data
#     email = data.get('email')
#     password = data.get('password')

#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     if not user.check_password(password):
#         return Response(
#             {"status": "error", "message": "Email ou mot de passe incorrect."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     # Vérifier si le compte est actif
#     if not user.is_active:
#         return Response(
#             {"status": "error", "message": "Compte désactivé. Contactez l'administrateur."},
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     # Utiliser le serializer pour les données utilisateur
#     user_serializer = UserSerializer(user, context={'request': request})
#     user_data = user_serializer.data

#     refresh = RefreshToken.for_user(user)
    
#     # Ajouter les claims dans le token
#     refresh['user_id'] = str(user.id)
#     refresh['email'] = user.email
#     refresh['role'] = user.role or ''
#     refresh['nom'] = user.nom
#     refresh['prenom'] = user.prenom
#     refresh['activite_id'] = str(user.activite_id) if user.activite_id else ''
#     refresh['direction_id'] = str(user.direction_id) if user.direction_id else ''
#     refresh['departement_id'] = str(user.departement_id) if user.departement_id else ''
#     refresh['direction_centrale_id'] = str(user.direction_centrale_id) if user.direction_centrale_id else ''
#     refresh['structure_id'] = str(user.structure_id) if user.structure_id else ''
#     refresh['direction_activite_id'] = str(user.direction_activite_id) if user.direction_activite_id else ''
#     refresh['division_activite_id'] = str(user.division_activite_id) if user.division_activite_id else ''

#     # Construire la réponse
#     response_data = {
#         "status": "success",
#         "message": f"Logged in as {user.prenom} {user.nom}",
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#         "user_id": str(user.id),
#         "role": user.role,
#         "nom_complet": f"{user.prenom} {user.nom}".strip(),
#         "photo_profil": user.photo_profil.url if user.photo_profil else None,
        
#         # IDs
#         "activite_id": str(user.activite_id) if user.activite_id else None,
#         "direction_id": str(user.direction_id) if user.direction_id else None,
#         "departement_id": str(user.departement_id) if user.departement_id else None,
#         "direction_centrale_id": str(user.direction_centrale_id) if user.direction_centrale_id else None,
#         "structure_id": str(user.structure_id) if user.structure_id else None,
#         "direction_activite_id": str(user.direction_activite_id) if user.direction_activite_id else None,
#         "division_activite_id": str(user.division_activite_id) if user.division_activite_id else None,
        
#         # Données enrichies (via le serializer)
#         "activite_detail": user_data.get("activite_detail"),
#         "direction_detail": user_data.get("direction_detail"),
#         "departement_detail": user_data.get("departement_detail"),
#         "direction_centrale_detail": user_data.get("direction_centrale_detail"),
#         "direction_activite_detail": user_data.get("direction_activite_detail"),
#         "division_activite_detail": user_data.get("division_activite_detail"),
#         "structure_detail": user_data.get("structure_detail"),
#     }
    
#     # Valider la réponse avec le serializer (optionnel mais recommandé)
#     response_serializer = UserLoginResponseSerializer(data=response_data)
#     if response_serializer.is_valid():
#         return Response(response_serializer.data)
#     else:
#         # En cas d'erreur de validation, retourner quand même les données
#         print(f"[LOGIN] Validation error: {response_serializer.errors}")
#         return Response(response_data)
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, UserLoginResponseSerializer

@api_view(['POST'])
def api_login(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "Email ou mot de passe incorrect."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        return Response(
            {"status": "error", "message": "Email ou mot de passe incorrect."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Vérifier si le compte est actif
    if not user.is_active:
        return Response(
            {"status": "error", "message": "Compte désactivé. Contactez l'administrateur."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Créer les tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Ajouter les claims dans le refresh token
    refresh['user_id'] = str(user.id)
    refresh['email'] = user.email
    refresh['role'] = user.role or ''
    refresh['nom'] = user.nom
    refresh['prenom'] = user.prenom
    refresh['activite_id'] = str(user.activite_id) if user.activite_id else ''
    refresh['direction_id'] = str(user.direction_id) if user.direction_id else ''
    refresh['departement_id'] = str(user.departement_id) if user.departement_id else ''
    refresh['direction_centrale_id'] = str(user.direction_centrale_id) if user.direction_centrale_id else ''
    refresh['structure_id'] = str(user.structure_id) if user.structure_id else ''
    refresh['direction_activite_id'] = str(user.direction_activite_id) if user.direction_activite_id else ''
    refresh['division_activite_id'] = str(user.division_activite_id) if user.division_activite_id else ''

    # ✅ IMPORTANT: Créer un contexte avec le token d'accès
    # Ajouter le token dans les headers de la requête pour que le serializer puisse le récupérer
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    
    # Créer le contexte pour le serializer avec la requête modifiée
    context = {
        'request': request,
        'access_token': access_token  # Token explicite en cas de besoin
    }
    
    # Utiliser le serializer avec le contexte enrichi
    user_serializer = UserSerializer(user, context=context)
    user_data = user_serializer.data

    # Construire la réponse
    response_data = {
        "status": "success",
        "message": f"Logged in as {user.prenom} {user.nom}",
        "refresh": str(refresh),
        "access": access_token,
        "user_id": str(user.id),
        "role": user.role,
        "nom_complet": f"{user.prenom} {user.nom}".strip(),
        "photo_profil": user.photo_profil.url if user.photo_profil else None,
        
        # IDs
        "activite_id": str(user.activite_id) if user.activite_id else None,
        "direction_id": str(user.direction_id) if user.direction_id else None,
        "departement_id": str(user.departement_id) if user.departement_id else None,
        "direction_centrale_id": str(user.direction_centrale_id) if user.direction_centrale_id else None,
        "structure_id": str(user.structure_id) if user.structure_id else None,
        "direction_activite_id": str(user.direction_activite_id) if user.direction_activite_id else None,
        "division_activite_id": str(user.division_activite_id) if user.division_activite_id else None,
        
        # Données enrichies (via le serializer)
        "activite_detail": user_data.get("activite_detail"),
        "direction_detail": user_data.get("direction_detail"),
        "departement_detail": user_data.get("departement_detail"),
        "direction_centrale_detail": user_data.get("direction_centrale_detail"),
        "direction_activite_detail": user_data.get("direction_activite_detail"),
        "division_activite_detail": user_data.get("division_activite_detail"),
        "structure_detail": user_data.get("structure_detail"),
    }
    
    # Valider la réponse avec le serializer (optionnel)
    response_serializer = UserLoginResponseSerializer(data=response_data)
    if response_serializer.is_valid():
        return Response(response_serializer.data)
    else:
        # En cas d'erreur de validation, retourner quand même les données
        print(f"[LOGIN] Validation error: {response_serializer.errors}")
        return Response(response_data)
# ==========================
# LOGOUT
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"status": "success", "message": "Logged out successfully"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=400)


# ==========================
# CHANGE PASSWORD
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not user.check_password(old_password):
        return Response({"status": "error", "message": "Old password incorrect"}, status=400)

    user.set_password(new_password)
    user.save()
    return Response({"status": "success", "message": "Password changed successfully"})


# ==========================
# RESET PASSWORD
# ==========================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_reset_password(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    token = PasswordResetTokenGenerator().make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    reset_url = f"http://localhost:3000/reset-confirm/{uid}/{token}"
    subject = "Réinitialisation de mot de passe"
    message = f"Bonjour {user.prenom},\n\nPour réinitialiser votre mot de passe, cliquez sur ce lien :\n{reset_url}\n\nSi vous n'avez pas demandé cette réinitialisation, ignorez cet email."

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

    return Response({"status": "success", "message": "Email de réinitialisation envoyé."})


# ==========================
# desactiver le compte user
# ==========================
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def api_toggle_user_active(request, user_id):
    """
    Désactiver ou réactiver un utilisateur
    Body: {"is_active": false} pour désactiver, true pour réactiver
    """
    # Vérifier que l'admin fait la requête
    if request.user.role != 'admin':
        return Response({
            "status": "error",
            "code": "FORBIDDEN",
            "message": "Accès admin uniquement"
        }, status=403)
    
    # Récupérer l'utilisateur cible
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": "Utilisateur non trouvé"
        }, status=404)
    
    # Empêcher de désactiver son propre compte
    if request.user.id == user.id:
        return Response({
            "status": "error",
            "code": "CANNOT_DISABLE_SELF",
            "message": "Vous ne pouvez pas désactiver votre propre compte"
        }, status=400)
    
    # Récupérer la nouvelle valeur
    is_active = request.data.get('is_active')
    
    if is_active is None:
        return Response({
            "status": "error",
            "code": "MISSING_FIELD",
            "message": "Le champ 'is_active' est requis (true/false)"
        }, status=400)
    
    # Convertir en booléen (au cas où ça arrive en string)
    if isinstance(is_active, str):
        is_active = is_active.lower() == 'true'
    
    old_status = user.is_active
    user.is_active = is_active
    user.save()
    
    status_message = "réactivé" if is_active else "désactivé"
    
    return Response({
        "status": "success",
        "code": "USER_STATUS_UPDATED",
        "message": f"Utilisateur {user.nom} {user.prenom} {status_message}",
        "data": {
            "user_id": user.id,
            "user_name": f"{user.prenom} {user.nom}",
            "old_status": old_status,
            "new_status": is_active,
            "modified_by": {
                "id": request.user.id,
                "name": f"{request.user.prenom} {request.user.nom}",
                "role": request.user.role
            }
        }
    })
@api_view(['POST'])
@permission_classes([AllowAny])
def api_reset_password_confirm(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not all([uid, token, new_password]):
        return Response({"status": "error", "message": "uid, token et new_password sont requis"}, status=400)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError):
        return Response({"status": "error", "message": "Lien invalide"}, status=400)

    if PasswordResetTokenGenerator().check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({"status": "success", "message": "Mot de passe réinitialisé avec succès"})
    else:
        return Response({"status": "error", "message": "Token invalide ou expiré"}, status=400)




# ==========================
# CREATE USER SIMPLE
# ==========================

from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_create_user(request):
    if request.user.role != 'admin':
        return Response(
            {"status": "error", "message": "Accès admin uniquement"},
            status=403
        )

    data = request.data

    required = ['email', 'nom', 'prenom']
    missing = [f for f in required if not data.get(f)]

    if missing:
        return Response(
            {"status": "error", "message": f"Champs manquants : {', '.join(missing)}"},
            status=400
        )

    email = data.get('email').strip().lower()

    if User.objects.filter(email=email).exists():
        return Response(
            {"status": "error", "message": "Email déjà utilisé"},
            status=400
        )

    # 🔐 password auto
    temp_password = get_random_string(10)

    user = User(
        email=email,
        nom=data.get('nom').strip(),
        prenom=data.get('prenom').strip(),
        role=data.get('role'),
        adresse=data.get('adresse'),
        telephone=data.get('telephone'),
        date_naissance=data.get('date_naissance'),
        sexe=data.get('sexe'),
        matricule=data.get('matricule'),

    )

    if 'photo_profil' in request.FILES:
        user.photo_profil = request.FILES['photo_profil']

    user.set_password(temp_password)
    user.save()

    # ✅ ENVOYER L'EMAIL DIRECTEMENT ICI
    try:
        send_mail(
            subject="Votre compte a été créé",
            message=(
                f"Bonjour {user.prenom} {user.nom},\n\n"
                f"Votre compte a été créé avec succès.\n\n"
                f"📧 Email: {user.email}\n"
                f"🔑 Mot de passe temporaire: {temp_password}\n\n"
                f"⚠️  Veuillez changer votre mot de passe lors de votre première connexion.\n\n"
                f"Cordialement,\nL'équipe administrative"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,  # Mettre False pour voir les erreurs en développement
        )
        print(f"✅ Email envoyé à {user.email}")
    except Exception as e:
        print(f"❌ ERREUR ENVOI EMAIL: {e}")
        # Vous pouvez logger l'erreur mais continuer quand même
        import traceback
        traceback.print_exc()

    # Reste de votre réponse...
    return Response({
        "status": "success",
        "message": "Utilisateur créé avec succès",
        "credentials": {
            "email": user.email,
            "generated_password": temp_password
        },
        "user": {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "role": user.role,
            "adresse": user.adresse,
            "telephone": user.telephone,
            "date_naissance": user.date_naissance,
            "sexe": user.sexe,
            "matricule": user.matricule,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "photo_profil": user.photo_profil.url if user.photo_profil else None,
            "groups": list(user.groups.values_list("name", flat=True)),
        }
    }, status=201)

from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_update_user(request, user_id):
    # Vérification admin
    # if request.user.role != 'admin':
    #     return Response({
    #         "status": "error",
    #         "code": "FORBIDDEN",
    #         "message": "Accès admin uniquement"
    #     }, status=403)

    # Récupération de l'utilisateur
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": "Utilisateur non trouvé"
        }, status=404)

    # Fonction pour formater les infos utilisateur
    def format_user_info(user_obj):
        return {
            "id": user_obj.id,
            "nom": user_obj.nom,
            "prenom": user_obj.prenom,
            "nom_complet": nom_complet(user_obj),
            "email": user_obj.email,
            "role": user_obj.role,
            "adresse": user_obj.adresse,
            "telephone": user_obj.telephone,
            "matricule": user_obj.matricule,
            "sexe": user_obj.sexe,
            "date_naissance": user_obj.date_naissance.isoformat() if user_obj.date_naissance else None,
            "activite_id": user_obj.activite_id,
            "direction_id": user_obj.direction_id,
            "departement_id": user_obj.departement_id,
            # "direction_division_id": user_obj.direction_division_id,
            # "departement_division_id":user_obj.departement_division_id,
            "direction_activite_id":user_obj.direction_activite_id,
            "structure_id":user_obj.structure_id,
            "division_activite_id":user_obj.division_activite_id,
            "direction_centrale_id":user_obj.direction_centrale_id,
            "is_active": user_obj.is_active,
            "photo_profil": user_obj.photo_profil.url if user_obj.photo_profil else None,
            "date_joined": user_obj.date_joined.isoformat() if hasattr(user_obj, 'date_joined') and user_obj.date_joined else None,
            "last_login": user_obj.last_login.isoformat() if user_obj.last_login else None
        }

    # 📊 AVANT MODIFICATION - Sauvegarder l'état original
    user_before = format_user_info(user)
    
    data = request.data
    
    # Liste des modifications effectuées
    modifications = []
    
    # 🔥 TRAITEMENT DU RÔLE - CORRECTION ICI
    if 'role' in data:
        role_value = data['role']
        
        # Liste des rôles valides depuis le modèle
        valid_roles = [role[0] for role in User.ROLE_CHOICES]
        
        # Autoriser null, None, ou chaîne vide
        if role_value is None or role_value == '' or (isinstance(role_value, str) and role_value.lower() == 'null'):
            user.role = None
            modifications.append(f"role: {user_before['role']} → null")
        elif role_value in valid_roles:
            user.role = role_value
            modifications.append(f"role: {user_before['role']} → {role_value}")
        else:
            return Response({
                "status": "error",
                "code": "INVALID_ROLE",
                "message": f"Rôle invalide: {role_value}",
                "valid_roles": valid_roles,
                "suggestion": f"Choisissez parmi: {', '.join(valid_roles)} ou null"
            }, status=400)

    # 🔥 TRAITEMENT DES AUTRES CHAMPS
    # fields = ['nom', 'prenom', 'email', 'adresse', 'telephone', 'matricule', 'sexe', 'activite_id', 'direction_id', 'departement_id']
    fields = [
    'nom',
    'prenom',
    'email',
    'adresse',
    'telephone',
    'matricule',
    'sexe',
    'activite_id',
    'direction_id',
    'departement_id',

    # ✅ AJOUTER CES CHAMPS
    'direction_centrale_id',
    # 'direction_division_id',
    # 'departement_division_id',
    'structure_id',
    'direction_activite_id',
    'division_activite_id'
]
    
    for field in fields:
        if field in data:
            old_value = getattr(user, field)
            new_value = data[field]
            
            # Nettoyer les valeurs vides
            if new_value == '' or new_value == 'null':
                new_value = None
            
            setattr(user, field, new_value)
            modifications.append(f"{field}: {old_value} → {new_value}")

    # 🔥 TRAITEMENT DE LA DATE DE NAISSANCE
    if 'date_naissance' in data:
        date_value = data['date_naissance']
        old_date = user.date_naissance
        
        if date_value is None or date_value == '' or date_value == 'null':
            user.date_naissance = None
            modifications.append(f"date_naissance: {old_date} → null")
        elif date_value:
            try:
                user.date_naissance = datetime.strptime(str(date_value).strip(), "%Y-%m-%d").date()
                modifications.append(f"date_naissance: {old_date} → {user.date_naissance}")
            except ValueError:
                return Response({
                    "status": "error",
                    "code": "INVALID_DATE_FORMAT",
                    "message": "Format date invalide. Utilisez YYYY-MM-DD"
                }, status=400)

    # 🔥 TRAITEMENT DE LA PHOTO
    photo_updated = False
    if 'photo_profil' in request.FILES:
        old_photo = user.photo_profil.url if user.photo_profil else None
        user.photo_profil = request.FILES['photo_profil']
        photo_updated = True
        modifications.append(f"photo_profil: {old_photo} → {user.photo_profil.url if user.photo_profil else 'nouvelle photo'}")

    # Sauvegarder l'utilisateur
    user.save()
    
    # 📊 APRÈS MODIFICATION - État après mise à jour
    user_after = format_user_info(user)

    # Réponse complète
    return Response({
        "status": "success",
        "code": "USER_UPDATED",
        "message": "Utilisateur mis à jour avec succès",
        "summary": {
            "modified_fields_count": len(modifications),
            "modifications": modifications,
            "photo_updated": photo_updated
        },
        "before": user_before,
        "after": user_after,
        "metadata": {
            "updated_by": {
                "id": request.user.id,
                "nom_complet": nom_complet(request.user),
                "role": request.user.role
            },
            "timestamp": datetime.now().isoformat(),
            "method": request.method
        }
    })
# ==========================
# LIST USERS
# ==========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_users(request):
    # if request.user.role != 'admin':
    #     return Response({"status": "error", "message": "Accès admin uniquement"}, status=403)

    # Exclure les admins de la liste
    users = User.objects.exclude(role='admin').order_by('nom')

    data = []
    for u in users:
        # Toutes les infos de l'utilisateur
        entry = {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "nom_complet": f"{u.prenom} {u.nom}",
            "role": u.role,
            "role_display": dict(User.ROLE_CHOICES).get(u.role, u.role),
            "matricule": u.matricule,
            "telephone": u.telephone,
            "adresse": u.adresse,
            "sexe": u.sexe,
            "sexe_display": dict(User.SEXE_CHOICES).get(u.sexe, u.sexe),
            "date_naissance": u.date_naissance,
            "activite_id": u.activite_id,
            "direction_id": u.direction_id,
            "departement_id": u.departement_id,
            "direction_centrale_id": u.direction_centrale_id,
            # "direction_division_id": u.direction_division_id,
            # "departement_division_id": u.departement_division_id,
            "structure_id":u.structure_id,
            "direction_activite_id": u.direction_activite_id,
            "division_activite_id": u.division_activite_id,
            "is_active": u.is_active,
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
            "photo_profil": u.photo_profil.url if u.photo_profil else None,
            "last_login": u.last_login,
        }

        

        

        data.append(entry)

    return Response({
        "status": "success",
        "count": len(data),
        "total_users": User.objects.exclude(role='admin').count(),
        "users": data
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_all_users(request):
    
    # 🔐 You can control access here
    if request.user.role != 'admin':
        return Response({
            "status": "error",
            "message": "Accès admin uniquement"
        }, status=403)

    users = User.objects.all().order_by('nom')  # ✅ includes admin

    data = []
    for u in users:
        entry = {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "nom_complet": f"{u.prenom} {u.nom}",
            "role": u.role,
            "role_display": dict(User.ROLE_CHOICES).get(u.role, u.role),
            "matricule": u.matricule,
            "telephone": u.telephone,
            "activite_id": u.activite_id,
            "direction_id":u.direction_id,
            "departement_id":u.departement_id,
            "direction_centrale_id": u.direction_centrale_id,
            # "direction_division_id": u.direction_division_id,
            # "departement_division_id": u.departement_division_id,
            "structure_id":u.structure_id,
            "direction_activite_id": u.direction_activite_id,
            "division_activite_id": u.division_activite_id,
            "is_active": u.is_active,
            "is_superuser": u.is_superuser,
            "photo_profil": u.photo_profil.url if u.photo_profil else None,
        }



        data.append(entry)

    return Response({
        "status": "success",
        "count": len(data),
        "users": data
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_all_users_public(request):
    
    # ✅ All authenticated users can access this endpoint
    # No admin restriction - just view-only access
    
    users = User.objects.all().order_by('nom')  # includes all users

    data = []
    for u in users:
        entry = {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "nom_complet": f"{u.prenom} {u.nom}",
            "role": u.role,
            "role_display": dict(User.ROLE_CHOICES).get(u.role, u.role),
            "matricule": u.matricule,
            "telephone": u.telephone,
            "activite_id": u.activite_id,
            "direction_id": u.direction_id,
            "departement_id": u.departement_id,
            "direction_centrale_id": u.direction_centrale_id,
            # "direction_division_id": u.direction_division_id,
            # "departement_division_id": u.departement_division_id,
            "structure_id":u.structure_id,
            "direction_activite_id": u.direction_activite_id,
            "division_activite_id": u.division_activite_id,
            "is_active": u.is_active,
            "is_superuser": u.is_superuser,
            "photo_profil": u.photo_profil.url if u.photo_profil else None,
        }

        data.append(entry)

    return Response({
        "status": "success",
        "count": len(data),
        "users": data
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_user_by_id(request, user_id):

    try:
        user = User.objects.get(id=user_id)

        return Response({
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "nom_complet": f"{user.prenom} {user.nom}",
            "role": user.role,
            "role_display": dict(User.ROLE_CHOICES).get(user.role, user.role),

            "activite_id": user.activite_id,
            "direction_id": user.direction_id,
            "departement_id": user.departement_id,
            "direction_centrale_id": user.direction_centrale_id,
            # "direction_division_id": user.direction_division_id,
            # "departement_division_id": user.departement_division_id,
            "structure_id":user.structure_id,
            "direction_activite_id": user.direction_activite_id,
            "division_activite_id": user.division_activite_id,

            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,

            "photo_profil": user.photo_profil.url if user.photo_profil else None,
        })

    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Utilisateur introuvable"
        }, status=404)
# ==========================
# GET USER
# ==========================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error", 
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur avec l'ID {user_id} non trouvé"
        }, status=404)

    # Vérification des droits (admin ou l'utilisateur lui-même)
    # if request.user.role != 'admin' and request.user.id != user.id:
    #     return Response({
    #         "status": "error",
    #         "code": "FORBIDDEN",
    #         "message": "Vous n'avez pas accès à ces informations",
    #         "details": "Seul l'admin ou l'utilisateur lui-même peut voir ce profil"
    #     }, status=403)

    # Fonction pour formater la date
    def format_date(date_obj):
        return date_obj.isoformat() if date_obj else None

    # Construction de la réponse complète
    user_data = {
        # === INFORMATIONS DE BASE ===
        "id": user.id,
        "email": user.email,
        "nom": user.nom,
        "prenom": user.prenom,
        "nom_complet": f"{user.prenom} {user.nom}",
        
        # === RÔLE ET PERMISSIONS ===
        "role": user.role,
        "role_display": dict(User.ROLE_CHOICES).get(user.role, "Non défini"),
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        
        # === INFORMATIONS PROFESSIONNELLES ===
        "matricule": user.matricule,
        "telephone": user.telephone,
        "adresse": user.adresse,
        
        # === INFORMATIONS PERSONNELLES ===
        "sexe": user.sexe,
        "sexe_display": dict(User.SEXE_CHOICES).get(user.sexe, "Non spécifié"),
        "date_naissance": format_date(user.date_naissance),
        "age": None,
        
        # === LOCALISATION ===
        
        "activite_id": user.activite_id,
        "direction_id": user.direction_id,
        "departement_id": user.departement_id,
        "direction_centrale_id": user.direction_centrale_id,
        # "direction_division_id": user.direction_division_id,
        # "departement_division_id": user.departement_division_id,
        "structure_id":user.structure_id,
        "direction_activite_id": user.direction_activite_id,
        "division_activite_id": user.division_activite_id,
        
        # === MÉDIAS ===
        "photo_profil": user.photo_profil.url if user.photo_profil else None,
        
        # === DATES SYSTÈME ===
        "last_login": format_date(user.last_login),
        "date_joined": format_date(getattr(user, 'date_joined', None)),
        
        # === GROUPES ET PERMISSIONS ===
        "groups": list(user.groups.values('id', 'name')),
        "user_permissions": list(user.user_permissions.values('id', 'codename', 'name')),
        
        # === STATISTIQUES DU COMPTE ===
        "account_stats": {
            "has_photo": user.photo_profil is not None,
            "has_matricule": user.matricule is not None,
            "has_telephone": user.telephone is not None,
            "has_adresse": user.adresse is not None,
            "profile_complete": all([
                user.nom, user.prenom, user.email,
                user.telephone, user.adresse, user.matricule
            ])
        }
    }
    
    # Calcul de l'âge
    if user.date_naissance:
        from datetime import date
        today = date.today()
        age = today.year - user.date_naissance.year
        if (today.month, today.day) < (user.date_naissance.month, user.date_naissance.day):
            age -= 1
        user_data["age"] = age
    
   
    
    # === SI L'UTILISATEUR EST UN ADMIN ===
    if user.role == 'admin':
        user_data["admin_info"] = {
            "is_admin": True,
            "has_full_access": user.is_superuser,
            "can_manage_users": True,
            "can_manage_roles": True
        }
    
    # === AUTRES RÔLES ===
    else:
        user_data["other_info"] = {
            "role_type": user.role or "Non assigné",
            "needs_role_assignment": user.role is None
        }

    return Response({
        "status": "success",
        "code": "USER_FOUND",
        "message": f"Profil de {user_data['nom_complet']} récupéré avec succès",
        "user": user_data,
        "request_metadata": {
            "requested_by": {
                "id": request.user.id,
                "nom_complet": f"{request.user.prenom} {request.user.nom}",
                "role": request.user.role
            },
            "timestamp": datetime.now().isoformat(),
            "user_id_requested": user_id
        }
    })
# ==========================
# DELETE USER
# ==========================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_delete_user(request, user_id):
    if request.user.role != 'admin':
        return Response({"status": "error", "message": "Accès admin uniquement"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"status": "error", "message": "Utilisateur non trouvé"}, status=404)

    name = nom_complet(user)
    user.delete()

    return Response({
        "status": "success",
        "message": f"{name} supprimé"
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'role': getattr(user, 'role', None),
        'nom_complet': f"{user.prenom} {user.nom}",
        'activite_id':    str(user.activite_id)    if user.activite_id    else None,
        'direction_id':    str(user.direction_id)    if user.direction_id    else None,
        'departement_id': str(user.departement_id) if user.departement_id else None,
        'is_active': user.is_active,
    })
# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def api_update_user_role(request, user_id):
#     """
#     Endpoint spécifique pour mettre à jour uniquement le rôle d'un utilisateur
#     """
#     # Vérification admin
#     if request.user.role != 'admin':
#         return Response({
#             "status": "error",
#             "code": "FORBIDDEN",
#             "message": "Accès admin uniquement"
#         }, status=403)

#     # Récupération de l'utilisateur
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur avec l'ID {user_id} non trouvé"
#         }, status=404)

#     # Récupération du nouveau rôle
#     new_role = request.data.get('role')
    
#     if new_role is None:
#         return Response({
#             "status": "error",
#             "code": "MISSING_ROLE",
#             "message": "Le champ 'role' est requis"
#         }, status=400)

#     # Liste des rôles valides
#     valid_roles = [role[0] for role in User.ROLE_CHOICES]
    
#     # Vérification si le rôle est valide
#     if new_role not in valid_roles:
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": f"Rôle invalide: {new_role}",
#             "valid_roles": valid_roles,
#             "suggestion": f"Choisissez parmi: {', '.join(valid_roles)}"
#         }, status=400)

#     # Sauvegarder l'ancien rôle
#     old_role = user.role
    
#     # Mettre à jour le rôle
#     user.role = new_role
#     user.save()

#     return Response({
#         "status": "success",
#         "code": "ROLE_UPDATED",
#         "message": f"Rôle de {user.prenom} {user.nom} mis à jour avec succès",
#         "data": {
#             "user_id": user.id,
#             "user_name": f"{user.prenom} {user.nom}",
#             "old_role": old_role,
#             "new_role": new_role,
#             "updated_by": {
#                 "id": request.user.id,
#                 "name": f"{request.user.prenom} {request.user.nom}",
#                 "role": request.user.role
#             }
#         }
#     }, status=200)
# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def api_update_user_role(request, user_id):
#     if request.user.role != 'admin':
#         return Response({
#             "status": "error",
#             "code": "FORBIDDEN",
#             "message": "Accès admin uniquement"
#         }, status=403)

#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur avec l'ID {user_id} non trouvé"
#         }, status=404)

#     new_role = request.data.get('role')
#     if new_role is None:
#         return Response({
#             "status": "error",
#             "code": "MISSING_ROLE",
#             "message": "Le champ 'role' est requis"
#         }, status=400)

#     valid_roles = [role[0] for role in User.ROLE_CHOICES]
#     if new_role not in valid_roles:
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": f"Rôle invalide: {new_role}",
#             "valid_roles": valid_roles,
#             "suggestion": f"Choisissez parmi: {', '.join(valid_roles)}"
#         }, status=400)

#     old_role = user.role

#     # ─── Reset tous les champs liés avant d'appliquer ────────────────────────
#     LINKED_FIELDS = [
#         'direction_centrale_id',
#         'direction_id',
#         'departement_id',
#         'activite_id',
#         'structure_id',
#         'division_activite_id',
#         'direction_activite_id',
#     ]
#     for field in LINKED_FIELDS:
#         setattr(user, field, None)

#     # ─── Mapping rôle → champ requis ─────────────────────────────────────────
#     ROLE_FIELD_MAP = {
#         'assistant_directeur_centrale':     'direction_centrale_id',
#         'responsable_departement':          'direction_id',
#         'responsable_departement_division': 'direction_id',
#         'directeur_direction_activite':     'activite_id',
#         'directeur_division_activite':      'structure_id',
#         'responsable_direction_division':   'structure_id',
#     }

#     if new_role in ROLE_FIELD_MAP:
#         field_name = ROLE_FIELD_MAP[new_role]
#         field_value = request.data.get(field_name)
#         if field_value:
#             setattr(user, field_name, field_value)
#         # pas de 400 ici : la validation est déjà faite dans affectation-service
#     # ──────────────────────────────────────────────────────────────────────────

#     user.role = new_role
#     user.save()

#     return Response({
#         "status": "success",
#         "code": "ROLE_UPDATED",
#         "message": f"Rôle de {user.prenom} {user.nom} mis à jour avec succès",
#         "data": {
#             "user_id":   user.id,
#             "user_name": f"{user.prenom} {user.nom}",
#             "old_role":  old_role,
#             "new_role":  new_role,
#             # retourner les champs liés pour que affectation-service puisse les lire
#             "linked_fields": {f: getattr(user, f) for f in LINKED_FIELDS},
#             "updated_by": {
#                 "id":   request.user.id,
#                 "name": f"{request.user.prenom} {request.user.nom}",
#                 "role": request.user.role
#             }
#         }
#     }, status=200)
# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def api_update_user_role(request, user_id):
#     """
#     PATCH /api/users/{user_id}/update-role/
    
#     Met à jour le rôle d'un utilisateur et ses champs liés.
#     """
    
#     # Vérification admin
#     if request.user.role != 'admin':
#         return Response({
#             "status": "error",
#             "code": "FORBIDDEN",
#             "message": "Accès admin uniquement"
#         }, status=403)
    
#     # Récupération utilisateur
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({
#             "status": "error",
#             "code": "USER_NOT_FOUND",
#             "message": f"Utilisateur avec l'ID {user_id} non trouvé"
#         }, status=404)
    
#     # Vérification rôle
#     new_role = request.data.get('role')
#     if new_role is None:
#         return Response({
#             "status": "error",
#             "code": "MISSING_ROLE",
#             "message": "Le champ 'role' est requis"
#         }, status=400)
    
#     valid_roles = [role[0] for role in User.ROLE_CHOICES]
#     if new_role not in valid_roles:
#         return Response({
#             "status": "error",
#             "code": "INVALID_ROLE",
#             "message": f"Rôle invalide: {new_role}",
#             "valid_roles": valid_roles
#         }, status=400)
    
#     old_role = user.role
    
#     # ──────────────────────────────────────────────────────────────
#     # 1. Réinitialiser TOUS les champs liés (peu importe le rôle)
#     # ──────────────────────────────────────────────────────────────
#     LINKED_FIELDS = [
#         'direction_centrale_id',
#         'direction_id',
#         'departement_id',
#         'activite_id',
#         'structure_id',
#         'division_activite_id',
#         'direction_activite_id',
#     ]
    
#     for field in LINKED_FIELDS:
#         setattr(user, field, None)
    
#     # ──────────────────────────────────────────────────────────────
#     # 2. Appliquer les nouveaux champs liés depuis la requête
#     # ──────────────────────────────────────────────────────────────
#     # Mapping rôle → champ requis (pour validation seulement)
#     ROLE_REQUIRED_FIELD = {
#         'assistant_directeur_centrale':     'direction_centrale_id',
#         'responsable_departement':          'direction_id',
#         'responsable_departement_division': 'direction_id',
#         'directeur_direction_activite':     'activite_id',
#         'directeur_division_activite':      'structure_id',
#         'responsable_direction_division':   'structure_id',
#     }
    
#     # Mettre à jour TOUS les champs liés présents dans la requête
#     # (pas seulement ceux du mapping - important !)
#     for field in LINKED_FIELDS:
#         if field in request.data:
#             field_value = request.data.get(field)
#             if field_value:
#                 setattr(user, field, field_value)
#                 print(f"DEBUG: Setting {field} = {field_value}")
    
#     # ──────────────────────────────────────────────────────────────
#     # 3. Validation optionnelle : champ requis présent ?
#     # ──────────────────────────────────────────────────────────────
#     if new_role in ROLE_REQUIRED_FIELD:
#         required_field = ROLE_REQUIRED_FIELD[new_role]
#         if not getattr(user, required_field, None):
#             # Ne pas bloquer si absent, car affectation-service gère déjà
#             # Mais on log pour debug
#             print(f"WARNING: Rôle {new_role} sans {required_field}")
    
#     # ──────────────────────────────────────────────────────────────
#     # 4. Appliquer le nouveau rôle
#     # ──────────────────────────────────────────────────────────────
#     user.role = new_role
#     user.save()
    
#     # ──────────────────────────────────────────────────────────────
#     # 5. Retourner toutes les données (pour affectation-service)
#     # ──────────────────────────────────────────────────────────────
#     return Response({
#         "status": "success",
#         "code": "ROLE_UPDATED",
#         "message": f"Rôle de {user.prenom} {user.nom} mis à jour avec succès",
#         "data": {
#             "user_id":   user.id,
#             "user_name": f"{user.prenom} {user.nom}",
#             "old_role":  old_role,
#             "new_role":  new_role,
#             # Retourner TOUS les champs liés pour que affectation-service puisse les lire
#             "linked_fields": {
#                 field: getattr(user, field, None) for field in LINKED_FIELDS
#             },
#             "updated_by": {
#                 "id":   request.user.id,
#                 "name": f"{request.user.prenom} {request.user.nom}",
#                 "role": request.user.role
#             }
#         }
#     }, status=200)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def api_update_user_role(request, user_id):
    """
    PATCH /auth/users/<user_id>/update-role/
    """

    # ── Permission admin ──────────────────────────────────────────────
    if request.user.role != 'admin':
        return Response({
            "status": "error",
            "code": "FORBIDDEN",
            "message": "Accès admin uniquement"
        }, status=403)

    # ── Récupération utilisateur ──────────────────────────────────────
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur avec l'ID {user_id} non trouvé"
        }, status=404)

    # ── Validation rôle ───────────────────────────────────────────────
    new_role = request.data.get('role')

    if new_role is None:
        return Response({
            "status": "error",
            "code": "MISSING_ROLE",
            "message": "Le champ 'role' est requis"
        }, status=400)

    valid_roles = [r[0] for r in User.ROLE_CHOICES]

    if new_role not in valid_roles:
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": f"Rôle invalide: {new_role}",
            "valid_roles": valid_roles
        }, status=400)

    old_role = user.role

    # ── 1. Reset tous les champs liés ────────────────────────────────
    LINKED_FIELDS = [
        'direction_centrale_id',
        'direction_id',
        'departement_id',
        'activite_id',
        'structure_id',
        'division_activite_id',
        'direction_activite_id',
    ]

    for field in LINKED_FIELDS:
        setattr(user, field, None)

    # ── 2. Appliquer les champs liés reçus ───────────────────────────
    # On itère sur LINKED_FIELDS et on accepte toute valeur présente
    # dans request.data, y compris None (reset explicite)
    print(f"[UPDATE-ROLE] request.data = {dict(request.data)}")

    for field in LINKED_FIELDS:
        if field in request.data:
            value = request.data.get(field)
            # Convertir "" en None, garder None tel quel, garder la vraie valeur
            setattr(user, field, value if value else None)
            print(f"[UPDATE-ROLE] {field} = {value!r}")

    # ── 3. Appliquer le nouveau rôle ─────────────────────────────────
    user.role = new_role
    user.save()

    print(f"[UPDATE-ROLE] Sauvegardé — role={user.role}, "
          f"direction_centrale_id={user.direction_centrale_id}, "
          f"direction_id={user.direction_id}, "
          f"activite_id={user.activite_id}, "
          f"structure_id={user.structure_id}")

    # ── 4. Réponse complète ───────────────────────────────────────────
    return Response({
        "status": "success",
        "code": "ROLE_UPDATED",
        "message": f"Rôle de {user.prenom} {user.nom} mis à jour avec succès",
        "data": {
            "user_id":   user.id,
            "user_name": f"{user.prenom} {user.nom}",
            "old_role":  old_role,
            "new_role":  new_role,
            "linked_fields": {
                field: getattr(user, field, None)
                for field in LINKED_FIELDS
            },
            "updated_by": {
                "id":   request.user.id,
                "name": f"{request.user.prenom} {request.user.nom}",
                "role": request.user.role
            }
        }
    }, status=200)
# authentification/views.py

# authentification/views.py - Modifier api_update_user_departement

# authentification/api/views.py

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def api_update_user_departement(request, user_id):
    """
    PATCH /auth/users/<user_id>/update-departement/
    Body: { "departement_id": null, "direction_id": null }
    
    Permet de mettre à jour ou supprimer (mettre à null) le département d'un responsable
    """
    # Vérifier que l'utilisateur est directeur_direction ou admin
    if request.user.role not in ['admin', 'directeur_direction']:
        return Response({
            "status": "error",
            "code": "FORBIDDEN",
            "message": "Seul un admin ou un directeur de direction peut utiliser cet endpoint"
        }, status=403)
    
    # Récupérer l'utilisateur cible
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": f"Utilisateur {user_id} non trouvé"
        }, status=404)
    
    # Vérifier que l'utilisateur cible est actif
    if not user.is_active:
        return Response({
            "status": "error",
            "code": "USER_INACTIVE",
            "message": "Cet utilisateur est inactif"
        }, status=400)
    
    # Vérifier que l'utilisateur cible a le bon rôle
    if user.role != 'responsable_departement':
        return Response({
            "status": "error",
            "code": "INVALID_ROLE",
            "message": f"L'utilisateur doit être 'responsable_departement' (actuel: {user.role})"
        }, status=400)
    
    # Si l'utilisateur a déjà une direction (et que ce n'est pas un admin), vérifier qu'il est dans la même direction
    if request.user.role == 'directeur_direction' and user.direction_id is not None:
        if str(user.direction_id) != str(request.user.direction_id):
            return Response({
                "status": "error",
                "code": "FORBIDDEN",
                "message": "Vous ne pouvez modifier que les utilisateurs de votre direction"
            }, status=403)
    
    # Récupérer les données (peuvent être null)
    departement_id = request.data.get('departement_id')
    direction_id = request.data.get('direction_id')
    
    # Sauvegarder les anciennes valeurs
    old_departement_id = user.departement_id
    old_direction_id = user.direction_id
    
    # ✅ Mettre à jour (accepter null)
    # departement_id peut être une string ou None/null
    if 'departement_id' in request.data:
        if departement_id is None or departement_id == '' or departement_id == 'null':
            user.departement_id = None
        else:
            user.departement_id = departement_id
    
    # direction_id peut être une string ou None/null
    if 'direction_id' in request.data:
        if direction_id is None or direction_id == '' or direction_id == 'null':
            user.direction_id = None
        else:
            user.direction_id = direction_id
    
    user.save()
    
    # Fonction pour le nom complet
    def get_nom_complet(u):
        return f"{u.prenom} {u.nom}".strip()
    
    return Response({
        "status": "success",
        "code": "DEPARTEMENT_UPDATED",
        "message": "Département mis à jour avec succès",
        "data": {
            "user_id": user.id,
            "user_name": get_nom_complet(user),
            "user_role": user.role,
            "old_departement_id": old_departement_id,
            "new_departement_id": user.departement_id,
            "old_direction_id": old_direction_id,
            "new_direction_id": user.direction_id,
            "updated_by": {
                "id": request.user.id,
                "name": get_nom_complet(request.user),
                "role": request.user.role
            },
            "timestamp": datetime.now().isoformat()
        }
    }, status=200)
# authentification/api/views.py

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_user_token(request):
    """
    POST /auth/refresh-token/
    Force la création d'un nouveau token avec les données à jour
    """
    user = request.user
    
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(user)
    
    # Ajouter les informations à jour dans le nouveau token
    refresh['role'] = user.role
    refresh['user_id'] = str(user.id)
    refresh['activite_id'] = str(user.activite_id) if user.activite_id else None
    refresh['direction_id'] = str(user.direction_id) if user.direction_id else None
    refresh['departement_id'] = str(user.departement_id) if user.departement_id else None
    
    return Response({
        "status": "success",
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user_id": str(user.id),
        "role": user.role,
        "direction_id": user.direction_id,
        "departement_id": user.departement_id,
        "message": "Token rafraîchi avec succès"
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])  # Pas besoin d'admin, juste authentifié
@parser_classes([MultiPartParser, FormParser, JSONParser])
def api_update_own_profile(request):
    """
    PUT/PATCH /auth/users/me/update/
    
    Permet à un utilisateur de modifier son propre profil
    (admin peut tout modifier, utilisateur normal seulement certains champs)
    """
    user = request.user  # L'utilisateur authentifié
    
    # Champs que tout le monde peut modifier
    public_fields = ['nom', 'prenom', 'adresse', 'telephone', 'sexe', 'date_naissance', 'photo_profil']
    
    # Champs réservés aux admins
    admin_only_fields = ['role', 'email', 'matricule', 'is_active', 
                         'activite_id', 'direction_id', 'departement_id',
                         'direction_centrale_id', 'division_activite_id',
                         'direction_activite_id', 'structure_id',
                        ]
    
    def format_user_info(user_obj):
        return {
            "id": user_obj.id,
            "nom": user_obj.nom,
            "prenom": user_obj.prenom,
            "nom_complet": f"{user_obj.prenom} {user_obj.nom}".strip(),
            "email": user_obj.email,
            "role": user_obj.role,
            "adresse": user_obj.adresse,
            "telephone": user_obj.telephone,
            "matricule": user_obj.matricule,
            "sexe": user_obj.sexe,
            "date_naissance": user_obj.date_naissance.isoformat() if user_obj.date_naissance else None,
            "activite_id": user_obj.activite_id,
            "direction_id": user_obj.direction_id,
            "departement_id": user_obj.departement_id,
            "direction_centrale_id": user_obj.direction_centrale_id,
            "is_active": user_obj.is_active,
            "photo_profil": user_obj.photo_profil.url if user_obj.photo_profil else None,
        }
    
    # Sauvegarder l'état avant modification
    user_before = format_user_info(user)
    modifications = []
    is_admin = user.role == 'admin'
    
    data = request.data
    
    # 🔥 TRAITEMENT DES CHAMPS PUBLICS (tout le monde peut modifier)
    for field in public_fields:
        if field in data:
            old_value = getattr(user, field)
            new_value = data[field]
            
            # Nettoyer les valeurs vides
            if new_value == '' or new_value == 'null':
                new_value = None
            
            setattr(user, field, new_value)
            modifications.append(f"{field}: {old_value} → {new_value}")
    
    # 🔥 TRAITEMENT DES CHAMPS ADMIN (seulement si l'utilisateur est admin)
    if is_admin:
        for field in admin_only_fields:
            if field in data:
                old_value = getattr(user, field)
                new_value = data[field]
                
                # Nettoyer les valeurs vides
                if new_value == '' or new_value == 'null':
                    new_value = None
                
                # Vérification spéciale pour le rôle
                if field == 'role' and new_value is not None:
                    valid_roles = [role[0] for role in User.ROLE_CHOICES]
                    if new_value not in valid_roles:
                        return Response({
                            "status": "error",
                            "code": "INVALID_ROLE",
                            "message": f"Rôle invalide: {new_value}",
                            "valid_roles": valid_roles
                        }, status=400)
                
                setattr(user, field, new_value)
                modifications.append(f"{field}: {old_value} → {new_value}")
    else:
        # Si non-admin essaie de modifier un champ admin, on ignore silencieusement
        for field in admin_only_fields:
            if field in data:
                modifications.append(f"{field}: ignoré (non autorisé)")
    
    # 🔥 TRAITEMENT SPÉCIAL DE LA DATE DE NAISSANCE
    if 'date_naissance' in data:
        date_value = data['date_naissance']
        if date_value is None or date_value == '' or date_value == 'null':
            user.date_naissance = None
        elif date_value:
            try:
                user.date_naissance = datetime.strptime(str(date_value).strip(), "%Y-%m-%d").date()
            except ValueError:
                return Response({
                    "status": "error",
                    "code": "INVALID_DATE_FORMAT",
                    "message": "Format date invalide. Utilisez YYYY-MM-DD"
                }, status=400)
    
    # 🔥 TRAITEMENT DE LA PHOTO
    photo_updated = False
    if 'photo_profil' in request.FILES:
        user.photo_profil = request.FILES['photo_profil']
        photo_updated = True
        modifications.append("photo_profil: mise à jour")
    
    # Sauvegarder
    user.save()
    
    # État après modification
    user_after = format_user_info(user)
    
    return Response({
        "status": "success",
        "code": "PROFILE_UPDATED",
        "message": "Profil mis à jour avec succès",
        "summary": {
            "modified_fields_count": len([m for m in modifications if "ignoré" not in m]),
            "modifications": modifications,
            "photo_updated": photo_updated,
            "is_admin": is_admin
        },
        "before": user_before,
        "after": user_after,
        "metadata": {
            "updated_by": user.id,
            "timestamp": datetime.now().isoformat(),
            "method": request.method
        }
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_own_profile(request):
    """
    GET /auth/users/me/
    
    Récupère le profil de l'utilisateur authentifié
    """
    user = request.user
    
    return Response({
        "status": "success",
        "data": {
            "id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "nom_complet": f"{user.prenom} {user.nom}".strip(),
            "email": user.email,
            "role": user.role,
            "adresse": user.adresse,
            "telephone": user.telephone,
            "matricule": user.matricule,
            "sexe": user.sexe,
            "date_naissance": user.date_naissance.isoformat() if user.date_naissance else None,
            "activite_id": user.activite_id,
            "direction_id": user.direction_id,
            "departement_id": user.departement_id,
            "direction_centrale_id": user.direction_centrale_id,
            "division_activite_id": user.division_activite_id,
            "direction_activite_id": user.direction_activite_id,
            # "departement_division_id": user.departement_division_id,
            # "direction_division_id": user.direction_division_id,
            "structure_id":user.structure_id,
            "is_active": user.is_active,
            "photo_profil": user.photo_profil.url if user.photo_profil else None,
            "date_joined": user.date_joined.isoformat() if hasattr(user, 'date_joined') and user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        },
        "metadata": {
            "timestamp": datetime.now().isoformat()
        }
    }, status=200)