
from rest_framework import serializers
from .models import  User
import cloudinary.uploader
from django.contrib.auth.hashers import make_password
import secrets



# ==================================================
# USER SERIALIZER
# ==================================================
class UserSerializer(serializers.ModelSerializer):
    photo_profil = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "nom", "prenom", "password",
            "role", "activite_id",
            "direction_id", "departement_id",
            "is_staff", "is_superuser", "photo_profil"
        ]
        extra_kwargs = {
            "password":     {"write_only": True, "required": False},
            "role":         {"required": True},
            "activite_id":    {"required": False, "allow_null": True},
            "direction_id":    {"required": False, "allow_null": True},
            "departement_id":  {"required": False, "allow_null": True},

        }

    # ==================================================
    # VALIDATION GLOBALE
    # ==================================================
    def validate(self, data):
        role         = data.get('role', getattr(self.instance, 'role', None))
        activite_id    = data.get('activite_id')
        direction_id   = data.get('direction_id')
        departement_id = data.get('departement_id')
        

        if role == 'directeur_activite':
            if activite_id:
                # Fourni → on vérifie
                self._verify_activite(activite_id)
            data['direction_id']   = None
            data['departement_id'] = None
        
        elif role == 'directeur_direction':
            if not direction_id:
                raise serializers.ValidationError({
                    "direction_id": "Obligatoire pour directeur_direction"
                })

            
            data['departement_id'] = None
        
        elif role == 'responsable_departement':
            if not departement_id:
                raise serializers.ValidationError({
                    "departement_id": "Obligatoire pour responsable_departement"
                })

            if not direction_id:
                raise serializers.ValidationError({
                    "direction_id": "Un département doit appartenir à une direction"
                })


            if activite_id:
                self._verify_activite(activite_id)


        else:
            data['activite_id']    = None
            data['direction_id']   = None
            data['departement_id'] = None


        return data
    
    # ==================================================
    # CREATE
    # ==================================================
    def create(self, validated_data):
        photo = validated_data.pop("photo_profil", None)

        if not validated_data.get("password"):
            generated_password         = secrets.token_urlsafe(8)
            validated_data["password"] = make_password(generated_password)
            self.generated_password    = generated_password

        if photo:
            result = cloudinary.uploader.upload(photo)
            validated_data["photo_profil"] = result["secure_url"]

        user = super().create(validated_data)
        user.generated_password = getattr(self, "generated_password", None)
        return user

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self, instance, validated_data):
        photo = validated_data.pop("photo_profil", None)

        if photo:
            result = cloudinary.uploader.upload(photo)
            validated_data["photo_profil"] = result["secure_url"]

        password = validated_data.pop("password", None)
        if password:
            validated_data["password"] = make_password(password)

        return super().update(instance, validated_data)


