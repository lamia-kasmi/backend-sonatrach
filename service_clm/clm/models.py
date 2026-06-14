# # clm_service/models.py
# from django.db import models

# class Contrat(models.Model):

#     TYPES_CONTRAT = (
#         ('service',     'Services / خدمات'),
#         ('fourniture',  'Fournitures / توريد'),
#         ('travaux',     'Travaux / أشغال'),
#         ('partenariat', 'Partenariat / شراكة'),
#         ('vente',       'Vente / بيع'),
#         ('transfert',   'Transfert / نقل'),
#     )

#     STATUTS_CONTRAT = (
#         ('brouillon', 'Brouillon'),
#         ('actif',     'Actif'),
#         ('expire',    'Expiré'),
#         ('resilie',   'Résilié'),
#     )

#     # ── Identification ──────────────────────────────────────
#     numero_contrat = models.CharField(max_length=100, unique=True)
#     titre          = models.CharField(max_length=500)
#     type_contrat   = models.CharField(max_length=20, choices=TYPES_CONTRAT)

#     # ── Organisation interne (IDs cross-service, pas de FK Django) ──
#     # Stockés comme CharField car ils viennent de MongoDB (ObjectId 24 chars)
#     # et sont gérés par le service Juridique / Auth, pas par CLM
#     cree_par_id            = models.IntegerField()          # User.id (PostgreSQL Auth)
#     cree_par_role          = models.CharField(max_length=30)
#     departement_id         = models.CharField(max_length=24)
#     direction_id           = models.CharField(max_length=24)
#     direction_centrale_id  = models.CharField(max_length=24, blank=True, null=True)

#     # ── Parties ─────────────────────────────────────────────
#     partie_a_nom   = models.CharField(max_length=255, default="SONATRACH")
#     partie_b_nom   = models.CharField(max_length=255)
#     pays_partie_b  = models.CharField(max_length=100)
#     is_international = models.BooleanField(default=False)  # auto-calculé
#     type_partie      = models.CharField(
#         max_length=10,
#         choices=[('nationale','Nationale'),('etrangere','Étrangère')],
#         default='nationale'
#     )

#     # ── Détails contrat ──────────────────────────────────────
#     objet               = models.TextField()
#     date_signature      = models.DateField()
#     date_debut          = models.DateField()
#     date_fin            = models.DateField()
#     montant             = models.DecimalField(max_digits=18, decimal_places=2)
#     devise              = models.CharField(max_length=10, default='DZD')
#     conditions_paiement = models.TextField(blank=True, null=True)
#     pdf_url = models.URLField(max_length=500, null=True,blank=True,verbose_name='URL du document PDF'
# )

#     # ── Document ─────────────────────────────────────────────
#     # Mode 1 : Upload PDF/DOCX/Image (OCR + IA)
#     fichier_original = models.FileField(
#         upload_to='contrats/originaux/', blank=True, null=True
#     )
#     fichier_format   = models.CharField(max_length=10, blank=True)  # pdf, docx, jpg...
#     texte_extrait    = models.TextField(blank=True)
#     moteur_ocr       = models.CharField(
#         max_length=20, blank=True,
#         choices=[('tesseract','Tesseract'),
#                  ('easyocr','EasyOCR'),
#                  ('azure','Azure Document Intelligence')]
#     )
#     ocr_effectue = models.BooleanField(default=False)
#     ocr_date     = models.DateTimeField(null=True, blank=True)

#     # Mode 2 : Contrat généré depuis formulaire
#     contrat_genere = models.FileField(
#         upload_to='contrats/generes/', blank=True, null=True
#     )

#     # ── Statut & dates ───────────────────────────────────────
#     statut            = models.CharField(max_length=20, choices=STATUTS_CONTRAT, default='brouillon')
#     date_creation     = models.DateTimeField(auto_now_add=True)
#     date_modification = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         # Calcul automatique type_partie + is_international
#         pays_algerien = self.pays_partie_b.strip().lower() in [
#             'algérie', 'algerie', 'algeria', 'dz'
#         ]
#         self.type_partie     = 'nationale' if pays_algerien else 'etrangere'
#         self.is_international = not pays_algerien
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.numero_contrat} - {self.titre}"
    
# # clm/models.py — ajout des deux modèles

# class MetadonneeContrat(models.Model):
#     """Champs spécifiques extraits selon le type de contrat (clé-valeur)."""
#     contrat  = models.ForeignKey('Contrat', on_delete=models.CASCADE,
#                                   related_name='metadonnees')
#     cle      = models.CharField(max_length=100)
#     valeur   = models.TextField()

#     class Meta:
#         unique_together = ('contrat', 'cle')
#         verbose_name = 'Métadonnée contrat'

#     def __str__(self):
#         return f"{self.contrat.numero_contrat} | {self.cle} = {self.valeur}"


# class RisqueContrat(models.Model):
#     """Risques détectés par le moteur d'analyse sur un contrat."""

#     TYPE_CHOICES = [
#         ('retard',      'Retard'),
#         ('imprecision', 'Imprécision'),
#         ('different',   'Différend'),
#     ]
#     SEVERITE_CHOICES = [
#         ('faible',   'Faible'),
#         ('moyen',    'Moyen'),
#         ('eleve',    'Élevé'),
#         ('critique', 'Critique'),
#     ]
#     NIVEAU_CHOICES = [
#         ('warning',  'Avertissement'),
#         ('alert',    'Alerte'),
#         ('escalade', 'Escalade'),
#     ]

#     contrat          = models.ForeignKey('Contrat', on_delete=models.CASCADE,
#                                           related_name='risques')
#     code             = models.CharField(max_length=10)     # ex: 'R-01', 'I-06', 'D-02'
#     type_risque      = models.CharField(max_length=15, choices=TYPE_CHOICES)
#     description      = models.TextField()
#     severite         = models.CharField(max_length=10, choices=SEVERITE_CHOICES)
#     article_ref      = models.CharField(max_length=50, blank=True)
#     suggestion       = models.TextField(blank=True)
#     occurrence_count = models.PositiveIntegerField(default=1)
#     niveau_alerte    = models.CharField(max_length=10, choices=NIVEAU_CHOICES,
#                                          default='warning')
#     resolu           = models.BooleanField(default=False)
#     date_detection   = models.DateTimeField(auto_now_add=True)
#     date_resolution  = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         unique_together = ('contrat', 'code')
#         ordering        = ['-severite', 'code']
#         verbose_name    = 'Risque contrat'

#     def __str__(self):
#         return f"[{self.code}] {self.contrat.numero_contrat} — {self.type_risque} ({self.severite})"
# clm_service/models.py

# from django.db import models
# from decimal import Decimal

# class Contrat(models.Model):

#     TYPES_CONTRAT = (
#         ('service',     'Services / خدمات'),
#         ('fourniture',  'Fournitures / توريد'),
#         ('travaux',     'Travaux / أشغال'),
#         ('partenariat', 'Partenariat / شراكة'),
#         ('vente',       'Vente / بيع'),
#         ('transfert',   'Transfert / نقل'),
#     )

#     STATUTS_CONTRAT = (
#         ('brouillon', 'Brouillon'),
#         ('actif',     'Actif'),
#         ('expire',    'Expiré'),
#         ('resilie',   'Résilié'),
#     )

#     # ── Identification ────────────────────────────────────────────
#     numero_contrat = models.CharField(max_length=100, unique=True)
#     titre          = models.CharField(max_length=500)
#     type_contrat   = models.CharField(max_length=20, choices=TYPES_CONTRAT)

#     # ── Organisation interne ──────────────────────────────────────
#     cree_par_id           = models.IntegerField()
#     cree_par_role         = models.CharField(max_length=30)
#     departement_id        = models.CharField(max_length=24)
#     direction_id          = models.CharField(max_length=24)
#     direction_centrale_id = models.CharField(max_length=24, blank=True, null=True)

#     # ── Parties — RENOMMÉS v2 ─────────────────────────────────────
#     # AVANT : partie_a_nom / partie_b_nom
#     # APRÈS : societe_a_nom / societe_b_nom
#     societe_a_nom  = models.CharField(
#         max_length=255,
#         default="SONATRACH",
#         verbose_name="Dénomination sociale Partie A (Client)"
#     )
#     societe_b_nom  = models.CharField(
#         max_length=255,
#         verbose_name="Dénomination sociale Partie B (Fournisseur)"
#     )
#     pays_partie_b    = models.CharField(max_length=100)
#     is_international = models.BooleanField(default=False)
#     type_partie      = models.CharField(
#         max_length=10,
#         choices=[('nationale', 'Nationale'), ('etrangere', 'Étrangère')],
#         default='nationale'
#     )

#     # ── Représentants Partie A (Client) — NOUVEAUX ────────────────
#     societe_a_representant_nom      = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Nom représentant Client")
#     societe_a_representant_prenom   = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Prénom représentant Client")
#     societe_a_representant_fonction = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Fonction représentant Client")

#     # ── Représentants Partie B (Fournisseur) — NOUVEAUX ──────────
#     societe_b_siege_social          = models.CharField(max_length=500, blank=True, null=True,
#         verbose_name="Siège social Fournisseur")
#     societe_b_representant_nom      = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Nom représentant Fournisseur")
#     societe_b_representant_prenom   = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Prénom représentant Fournisseur")
#     societe_b_representant_fonction = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Fonction représentant Fournisseur")

#     # ── Contacts Art. 21 — NOUVEAUX ──────────────────────────────
#     notification_adresse_ligne1 = models.CharField(max_length=500, blank=True, null=True)
#     notification_adresse_ligne2 = models.CharField(max_length=500, blank=True, null=True)
#     fax_fournisseur             = models.CharField(max_length=50, blank=True, null=True)
#     telephone_fournisseur       = models.CharField(max_length=50, blank=True, null=True)
#     email_fournisseur           = models.EmailField(blank=True, null=True)

#     # ── Signatures Art. 22 — NOUVEAUX ────────────────────────────
#     nom_client         = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Nom signataire Client (Art. 22)")
#     prenom_client      = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Prénom signataire Client (Art. 22)")
#     fonction_client    = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Fonction signataire Client (Art. 22)")
#     nom_fournisseur    = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Nom signataire Fournisseur (Art. 22)")
#     prenom_fournisseur = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Prénom signataire Fournisseur (Art. 22)")
#     fonction_fournisseur = models.CharField(max_length=255, blank=True, null=True,
#         verbose_name="Fonction signataire Fournisseur (Art. 22)")

#     # ── Détails contrat ───────────────────────────────────────────
#     objet               = models.TextField()
#     date_signature      = models.DateField(null=True, blank=True)
#     date_debut          = models.DateField(null=True, blank=True)
#     date_fin            = models.DateField(null=True, blank=True)
#     montant             = models.DecimalField(max_digits=18, decimal_places=2, default=0)
#     devise              = models.CharField(max_length=10, default='DZD')
#     conditions_paiement = models.TextField(blank=True, null=True)
#     pdf_url             = models.URLField(max_length=500, null=True, blank=True,
#                             verbose_name='URL du document PDF')

#     # ── Document ──────────────────────────────────────────────────
#     fichier_original = models.FileField(upload_to='contrats/originaux/', blank=True, null=True)
#     fichier_format   = models.CharField(max_length=10, blank=True)
#     texte_extrait    = models.TextField(blank=True)
#     moteur_ocr       = models.CharField(
#         max_length=20, blank=True,
#         choices=[('tesseract', 'Tesseract'),
#                  ('easyocr', 'EasyOCR'),
#                  ('azure', 'Azure Document Intelligence')]
#     )
#     ocr_effectue   = models.BooleanField(default=False)
#     ocr_date       = models.DateTimeField(null=True, blank=True)
#     contrat_genere = models.FileField(upload_to='contrats/generes/', blank=True, null=True)

#     # ── Statut & dates ────────────────────────────────────────────
#     statut            = models.CharField(max_length=20, choices=STATUTS_CONTRAT, default='brouillon')
#     date_creation     = models.DateTimeField(auto_now_add=True)
#     date_modification = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         pays_algerien = self.pays_partie_b.strip().lower() in [
#             'algérie', 'algerie', 'algeria', 'dz'
#         ]
#         self.type_partie      = 'nationale' if pays_algerien else 'etrangere'
#         self.is_international = not pays_algerien
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.numero_contrat} - {self.titre}"


# class MetadonneeContrat(models.Model):
#     """Champs spécifiques extraits selon le type de contrat (clé-valeur)."""
#     contrat = models.ForeignKey('Contrat', on_delete=models.CASCADE,
#                                 related_name='metadonnees')
#     cle     = models.CharField(max_length=100)
#     valeur  = models.TextField()

#     class Meta:
#         unique_together = ('contrat', 'cle')
#         verbose_name    = 'Métadonnée contrat'

#     def __str__(self):
#         return f"{self.contrat.numero_contrat} | {self.cle} = {self.valeur}"


# class RisqueContrat(models.Model):
#     """Risques détectés par le moteur d'analyse sur un contrat."""

#     TYPE_CHOICES = [
#         ('retard',      'Retard'),
#         ('imprecision', 'Imprécision'),
#         ('different',   'Différend'),
#     ]
#     SEVERITE_CHOICES = [
#         ('faible',   'Faible'),
#         ('moyen',    'Moyen'),
#         ('eleve',    'Élevé'),
#         ('critique', 'Critique'),
#     ]
#     NIVEAU_CHOICES = [
#         ('warning',  'Avertissement'),
#         ('alert',    'Alerte'),
#         ('escalade', 'Escalade'),
#     ]

#     contrat          = models.ForeignKey('Contrat', on_delete=models.CASCADE,
#                                          related_name='risques')
#     code             = models.CharField(max_length=10)
#     type_risque      = models.CharField(max_length=15, choices=TYPE_CHOICES)
#     description      = models.TextField()
#     severite         = models.CharField(max_length=10, choices=SEVERITE_CHOICES)
#     article_ref      = models.CharField(max_length=50, blank=True)
#     suggestion       = models.TextField(blank=True)
#     occurrence_count = models.PositiveIntegerField(default=1)
#     niveau_alerte    = models.CharField(max_length=10, choices=NIVEAU_CHOICES, default='warning')
#     resolu           = models.BooleanField(default=False)
#     date_detection   = models.DateTimeField(auto_now_add=True)
#     date_resolution  = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         unique_together = ('contrat', 'code')
#         ordering        = ['-severite', 'code']
#         verbose_name    = 'Risque contrat'

#     def __str__(self):
#         return f"[{self.code}] {self.contrat.numero_contrat} — {self.type_risque} ({self.severite})"


import calendar
from datetime import date

from django.db import models
from decimal import Decimal


import calendar
from datetime import date, datetime


def ajouter_mois(d, mois):
    """
    Ajoute `mois` mois à la date `d`.
    `d` peut être un objet date/datetime OU une chaîne ('YYYY-MM-DD', 'DD/MM/YYYY', 'DD-MM-YYYY').
    Retourne None si `d` ou `mois` est vide/invalide.
    """
    if d is None or mois in (None, ''):
        return None

    # ── Normalisation de d en objet date ───────────────────────────
    if isinstance(d, datetime):
        d = d.date()
    elif isinstance(d, str):
        d_str = d.strip()
        parsed = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                parsed = datetime.strptime(d_str, fmt).date()
                break
            except ValueError:
                continue
        if parsed is None:
            return None
        d = parsed
    elif not isinstance(d, date):
        return None

    try:
        mois = int(mois)
    except (TypeError, ValueError):
        return None

    mois_total = d.month - 1 + mois
    annee = d.year + mois_total // 12
    mois_resultat = mois_total % 12 + 1
    dernier_jour_du_mois = calendar.monthrange(annee, mois_resultat)[1]
    jour = min(d.day, dernier_jour_du_mois)

    return date(annee, mois_resultat, jour)
class Contrat(models.Model):

    TYPES_CONTRAT = (
        ('service',     'Services / خدمات'),
        ('fourniture',  'Fournitures / توريد'),
        ('travaux',     'Travaux / أشغال'),
        ('partenariat', 'Partenariat / شراكة'),
        ('vente',       'Vente / بيع'),
        ('transfert',   'Transfert / نقل'),
    )

    STATUTS_CONTRAT = (
        ('brouillon', 'Brouillon'),
        ('actif',     'Actif'),
        ('expire',    'Expiré'),
        ('resilie',   'Résilié'),
    )

    # ── Identification ────────────────────────────────────────────
    numero_contrat = models.CharField(max_length=100, unique=True)
    titre          = models.CharField(max_length=500)
    type_contrat   = models.CharField(max_length=20, choices=TYPES_CONTRAT)

    # ── Organisation interne ──────────────────────────────────────
    cree_par_id           = models.IntegerField()
    cree_par_role         = models.CharField(max_length=30)
    departement_id        = models.CharField(max_length=24)
    direction_id          = models.CharField(max_length=24)
    direction_centrale_id = models.CharField(max_length=24, blank=True, null=True)

    # ── Parties — RENOMMÉS v2 ─────────────────────────────────────
    societe_a_nom  = models.CharField(
        max_length=255,
        default="SONATRACH",
        verbose_name="Dénomination sociale Partie A (Client)"
    )
    societe_b_nom  = models.CharField(
        max_length=255,
        verbose_name="Dénomination sociale Partie B (Fournisseur)"
    )
    pays_partie_b    = models.CharField(max_length=100)
    is_international = models.BooleanField(default=False)
    type_partie      = models.CharField(
        max_length=10,
        choices=[('nationale', 'Nationale'), ('etrangere', 'Étrangère')],
        default='nationale'
    )

    # ── Représentants Partie A (Client) ────────────────────────────
    societe_a_representant_nom      = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Nom représentant Client")
    societe_a_representant_prenom   = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Prénom représentant Client")
    societe_a_representant_fonction = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Fonction représentant Client")

    # ── Représentants Partie B (Fournisseur) ──────────────────────
    societe_b_siege_social          = models.CharField(max_length=500, blank=True, null=True,
        verbose_name="Siège social Fournisseur")
    societe_b_representant_nom      = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Nom représentant Fournisseur")
    societe_b_representant_prenom   = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Prénom représentant Fournisseur")
    societe_b_representant_fonction = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Fonction représentant Fournisseur")

    # ── Contacts Art. 21 ───────────────────────────────────────────
    notification_adresse_ligne1 = models.CharField(max_length=500, blank=True, null=True)
    notification_adresse_ligne2 = models.CharField(max_length=500, blank=True, null=True)
    fax_fournisseur             = models.CharField(max_length=50, blank=True, null=True)
    telephone_fournisseur       = models.CharField(max_length=50, blank=True, null=True)
    email_fournisseur           = models.EmailField(blank=True, null=True)

    # ── Signatures Art. 22 ─────────────────────────────────────────
    nom_client         = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Nom signataire Client (Art. 22)")
    prenom_client      = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Prénom signataire Client (Art. 22)")
    fonction_client    = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Fonction signataire Client (Art. 22)")
    nom_fournisseur    = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Nom signataire Fournisseur (Art. 22)")
    prenom_fournisseur = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Prénom signataire Fournisseur (Art. 22)")
    fonction_fournisseur = models.CharField(max_length=255, blank=True, null=True,
        verbose_name="Fonction signataire Fournisseur (Art. 22)")

    # ── Détails contrat ───────────────────────────────────────────
    objet               = models.TextField()
    date_signature      = models.DateField(null=True, blank=True)
    date_debut          = models.DateField(null=True, blank=True)
    date_fin            = models.DateField(null=True, blank=True)
    montant             = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    devise              = models.CharField(max_length=10, default='DZD')
    conditions_paiement = models.TextField(blank=True, null=True)
    pdf_url             = models.URLField(max_length=500, null=True, blank=True,
                            verbose_name='URL du document PDF')

    # ── Délai de livraison & date limite — NOUVEAUX ────────────────
    delai_livraison_mois = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Délai de livraison (mois)",
        help_text="Nombre de mois accordés pour la livraison, "
                   "à compter de la date de début (date_debut)."
    )
    date_limite_livraison = models.DateField(
        null=True, blank=True, editable=False,
        verbose_name="Date limite de livraison (calculée automatiquement)",
        help_text="Calculé automatiquement = date_debut + delai_livraison_mois"
    )

    # ── Document ──────────────────────────────────────────────────
    fichier_original = models.FileField(upload_to='contrats/originaux/', blank=True, null=True)
    fichier_format   = models.CharField(max_length=10, blank=True)
    texte_extrait    = models.TextField(blank=True)
    moteur_ocr       = models.CharField(
        max_length=20, blank=True,
        choices=[('tesseract', 'Tesseract'),
                 ('easyocr', 'EasyOCR'),
                 ('azure', 'Azure Document Intelligence')]
    )
    ocr_effectue   = models.BooleanField(default=False)
    ocr_date       = models.DateTimeField(null=True, blank=True)
    contrat_genere = models.FileField(upload_to='contrats/generes/', blank=True, null=True)

    # ── Statut & dates ────────────────────────────────────────────
    statut            = models.CharField(max_length=20, choices=STATUTS_CONTRAT, default='brouillon')
    date_creation     = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    # ── Calcul / save ────────────────────────────────────────────
    def calculer_date_limite_livraison(self):
        """Retourne la date limite de livraison calculée, sans la persister."""
        return ajouter_mois(self.date_debut, self.delai_livraison_mois)

    def save(self, *args, **kwargs):
        pays_algerien = self.pays_partie_b.strip().lower() in [
            'algérie', 'algerie', 'algeria', 'dz'
        ]
        self.type_partie      = 'nationale' if pays_algerien else 'etrangere'
        self.is_international = not pays_algerien

        # ── Calcul automatique de la date limite de livraison ──────
        self.date_limite_livraison = self.calculer_date_limite_livraison()

        super().save(*args, **kwargs)

    # ── Propriétés utilitaires ──────────────────────────────────────
    @property
    def jours_restants_livraison(self):
        """Nombre de jours restants avant la date limite (peut être négatif si dépassée)."""
        if not self.date_limite_livraison:
            return None
        from django.utils import timezone
        delta = self.date_limite_livraison - timezone.now().date()
        return delta.days

    @property
    def est_en_retard(self):
        """
        True si la date limite de livraison est dépassée et que le contrat
        n'a pas encore de date_fin (livraison non encore actée),
        et que le contrat n'est pas expiré/résilié.
        """
        if not self.date_limite_livraison:
            return False
        if self.statut in ('resilie', 'expire'):
            return False
        if self.date_fin:
            # Livraison déjà actée : on compare la date de fin réelle à la date limite
            return self.date_fin > self.date_limite_livraison
        from django.utils import timezone
        return timezone.now().date() > self.date_limite_livraison

    def __str__(self):
        return f"{self.numero_contrat} - {self.titre}"


class MetadonneeContrat(models.Model):
    """Champs spécifiques extraits selon le type de contrat (clé-valeur)."""
    contrat = models.ForeignKey('Contrat', on_delete=models.CASCADE,
                                related_name='metadonnees')
    cle     = models.CharField(max_length=100)
    valeur  = models.TextField()

    class Meta:
        unique_together = ('contrat', 'cle')
        verbose_name    = 'Métadonnée contrat'

    def __str__(self):
        return f"{self.contrat.numero_contrat} | {self.cle} = {self.valeur}"


class RisqueContrat(models.Model):
    """Risques détectés par le moteur d'analyse sur un contrat."""

    TYPE_CHOICES = [
        ('retard',      'Retard'),
        ('imprecision', 'Imprécision'),
        ('different',   'Différend'),
    ]
    SEVERITE_CHOICES = [
        ('faible',   'Faible'),
        ('moyen',    'Moyen'),
        ('eleve',    'Élevé'),
        ('critique', 'Critique'),
    ]
    NIVEAU_CHOICES = [
        ('warning',  'Avertissement'),
        ('alert',    'Alerte'),
        ('escalade', 'Escalade'),
    ]

    contrat          = models.ForeignKey('Contrat', on_delete=models.CASCADE,
                                         related_name='risques')
    code             = models.CharField(max_length=10)
    type_risque      = models.CharField(max_length=15, choices=TYPE_CHOICES)
    description      = models.TextField()
    severite         = models.CharField(max_length=10, choices=SEVERITE_CHOICES)
    article_ref      = models.CharField(max_length=50, blank=True)
    suggestion       = models.TextField(blank=True)
    occurrence_count = models.PositiveIntegerField(default=1)
    niveau_alerte    = models.CharField(max_length=10, choices=NIVEAU_CHOICES, default='warning')
    resolu           = models.BooleanField(default=False)
    date_detection   = models.DateTimeField(auto_now_add=True)
    date_resolution  = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('contrat', 'code')
        ordering        = ['-severite', 'code']
        verbose_name    = 'Risque contrat'

    def __str__(self):
        return f"[{self.code}] {self.contrat.numero_contrat} — {self.type_risque} ({self.severite})"