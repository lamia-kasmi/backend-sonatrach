
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from cloudinary.models import CloudinaryField


# ===============================
# CUSTOM USER MANAGER
# ===============================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, nom, prenom, role, password=None, **extra_fields):
        if not email:
            raise ValueError("Email obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            temp = get_random_string(8)
            user.set_password(temp)
            user._temp_password = temp  # pour l'email
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(
            email=email, nom=nom, prenom=prenom,
            role='admin', password=password, **extra_fields
        )


# ===============================
# USER MODEL
# ===============================
class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('admin',                 'Admin'),
        ('agent',                  'Agent'),
        ('vice_presedent',      'Vice Presedent'),#
        ('directeur_direction',   'Directeur de Direction'),#
        ('responsable_departement','Responsable de Département'),
        ('directeur_centrale',             'Directeur Centrale'),#
        ('assistant_directeur_centrale',   'Assistant Directeur Centrale'),
        ('directeur_direction_activite',   'Directeur Direction Activité'),
        ('directeur_division_activite',    'Directeur Division Activité'),
        ('responsable_direction_division', 'Responsable Direction Division'),
        ('responsable_departement_division','Responsable Département Division'),
        
    ]

    SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

    # --- Champs de base ---
    email        = models.EmailField(unique=True)
    nom          = models.CharField(max_length=50)
    prenom       = models.CharField(max_length=50)
    role         = models.CharField(max_length=50, choices=ROLE_CHOICES,blank=True, null=True)
    photo_profil = CloudinaryField('image', blank=True, null=True)

    # --- Champs communs employé ---
    adresse        = models.TextField(blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    sexe           = models.CharField(max_length=1, choices=SEXE_CHOICES, blank=True, null=True)
    telephone      = models.CharField(max_length=20, blank=True, null=True)
    matricule      = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # --- Références externes MongoDB ---
    activite_id    = models.CharField(max_length=24, blank=True, null=True)
    direction_id   = models.CharField(max_length=24, blank=True, null=True)
    departement_id = models.CharField(max_length=24, blank=True, null=True)

    direction_centrale_id   = models.CharField(max_length=24, blank=True, null=True)
    # activite(division/direction)
    division_activite_id   = models.CharField(max_length=24, blank=True, null=True)
    direction_activite_id   = models.CharField(max_length=24, blank=True, null=True)
    #dividion ( departement/direction)
    structure_id   = models.CharField(max_length=24, blank=True, null=True)
    
    

    
    

    # --- Flags Django ---
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)

    groups           = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.role})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    def save(self, *args, **kwargs):
        is_new = self._state.adding  

        # générer mot de passe si nouveau user
        if is_new and not self.password:
            temp_password = get_random_string(8)
            self.set_password(temp_password)
            self._temp_password = temp_password  # pour email

        super().save(*args, **kwargs)

        # envoyer email APRES save
        if is_new and hasattr(self, "_send_welcome_email") and self._send_welcome_email:
            try:
                send_mail(
                    subject="Votre compte a été créé",
                    message=(
                        f"Bonjour {self.prenom},\n\n"
                        f"Email: {self.email}\n"
                        f"Mot de passe: {self._temp_password}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.email],
                    fail_silently=False,
                )
            except Exception:
                pass
