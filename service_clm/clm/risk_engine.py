# clm/risk_engine.py
"""
Moteur d'analyse de risques pour les contrats Sonatrach.

3 types de risques :
  - RETARD      : délais anormaux, absence de pénalités
  - IMPRECISION : champs manquants, clauses vagues, template non rempli
  - DIFFERENT   : notions fiscales/impôts imprécises, résiliation floue,
                  juridiction absente

Logique de récurrence :
  - 1ère occurrence → WARNING
  - 2ème occurrence → ALERT (notifier le chef de département)
  - 3ème+ occurrence → ESCALADE (notifier la direction)
"""

import re
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from .models import ajouter_mois
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════

SEUIL_RETARD_MOIS = 7          # Art. 4 : au-delà → risque retard
SEUIL_CAUTION_PCT = 10         # Art. 10 : en dessous → risque différend
SEUIL_ECHEANCE_JOURS = 30      # alerte si expiration dans moins de 30j

TYPE_RETARD     = 'retard'
TYPE_IMPRECISION = 'imprecision'
TYPE_DIFFERENT  = 'different'

SEV_FAIBLE   = 'faible'
SEV_MOYEN    = 'moyen'
SEV_ELEVE    = 'eleve'
SEV_CRITIQUE = 'critique'


# ══════════════════════════════════════════════════════════════
# STRUCTURES
# ══════════════════════════════════════════════════════════════

def _risque(code: str, type_risque: str, description: str,
            severite: str, article_ref: str = '', suggestion: str = '') -> dict:
    return {
        'code':        code,
        'type':        type_risque,
        'description': description,
        'severite':    severite,
        'article_ref': article_ref,
        'suggestion':  suggestion,
    }

# ══════════════════════════════════════════════════════════════
# ANALYSE PRINCIPALE
# ══════════════════════════════════════════════════════════════

def analyser_risques(parsed: dict, texte: str) -> List[dict]:
    """
    Prend en entrée :
      - parsed    : dict retourné par parse_contract_data()
      - texte     : texte brut extrait du PDF

    Retourne une liste de risques détectés.
    Chaque risque est un dict avec : code, type, description, severite,
    article_ref, suggestion.
    """
    risques = []
    meta    = parsed.get('metadonnees', {})

    # ── 1. RISQUES DE RETARD ──────────────────────────────────────────
    risques += _analyser_retard(parsed, meta)

    # ── 2. RISQUES D'IMPRÉCISION ─────────────────────────────────────
    risques += _analyser_imprecision(parsed, meta, texte)

    # ── 3. RISQUES DE DIFFÉREND ───────────────────────────────────────
    risques += _analyser_different(parsed, meta, texte)

    logger.info(f'[RISK] {len(risques)} risques détectés : '
                f'{[r["code"] for r in risques]}')
    return risques


# ══════════════════════════════════════════════════════════════
# 1. RISQUES DE RETARD
# ══════════════════════════════════════════════════════════════



# def _analyser_retard(parsed: dict, meta: dict) -> list:
#     risques = []
#     delai   = meta.get('delai_livraison_mois')

#     # R-01 : Délai de livraison excessif (> 7 mois)
#     if delai is not None and delai > SEUIL_RETARD_MOIS:
#         risques.append(_risque(
#             code        = 'R-01',
#             type_risque = TYPE_RETARD,
#             description = (
#                 f"Délai de livraison de {delai} mois dépasse le seuil autorisé "
#                 f"de {SEUIL_RETARD_MOIS} mois. / "
#                 f"مدة التسليم المحددة بـ {delai} شهرًا تتجاوز الحد المسموح به "
#                 f"البالغ {SEUIL_RETARD_MOIS} شهرًا."
#             ),
#             severite    = SEV_CRITIQUE if delai > 12 else SEV_ELEVE,
#             article_ref = 'Article 4',
#             suggestion  = (
#                 "Réduire le délai ou obtenir une dérogation de la direction. "
#                 "Prévoir un plan de livraison par tranches. / "
#                 "تقليص المدة أو الحصول على ترخيص استثنائي من الإدارة، "
#                 "ووضع خطة تسليم على دفعات."
#             ),
#         ))

#     # R-02 : Délai non défini
#     if delai is None:
#         risques.append(_risque(
#             code        = 'R-02',
#             type_risque = TYPE_RETARD,
#             description = (
#                 "Délai de livraison non renseigné dans le contrat. / "
#                 "مدة التسليم غير محددة في العقد."
#             ),
#             severite    = SEV_ELEVE,
#             article_ref = 'Article 4',
#             suggestion  = (
#                 "Définir un délai de livraison précis en mois. / "
#                 "تحديد مدة تسليم دقيقة بالأشهر."
#             ),
#         ))

#     # R-03 : Absence de pénalités de retard
#     if meta.get('penalite_retard_pct') is None:
#         risques.append(_risque(
#             code        = 'R-03',
#             type_risque = TYPE_RETARD,
#             description = (
#                 "Aucune pénalité de retard définie dans le contrat. / "
#                 "لم يتم تحديد أي غرامة تأخير في العقد."
#             ),
#             severite    = SEV_ELEVE,
#             article_ref = 'Article 5',
#             suggestion  = (
#                 "Intégrer une clause de pénalité (minimum 1% par semaine, "
#                 "plafonnée à 10% du montant total). / "
#                 "إدراج بند غرامة تأخير (بحد أدنى 1% أسبوعيًا، وبحد أقصى "
#                 "10% من القيمة الإجمالية للعقد)."
#             ),
#         ))

#     # R-04 : Absence de plafond pénalités
#     if meta.get('penalite_plafond_pct') is None:
#         risques.append(_risque(
#             code        = 'R-04',
#             type_risque = TYPE_RETARD,
#             description = (
#                 "Plafond des pénalités de retard non défini. / "
#                 "لم يتم تحديد سقف غرامات التأخير."
#             ),
#             severite    = SEV_MOYEN,
#             article_ref = 'Article 5',
#             suggestion  = (
#                 "Définir un plafond de pénalités (standard Sonatrach : 10%). / "
#                 "تحديد سقف للغرامات (المعيار المعتمد لدى سوناطراك: 10%)."
#             ),
#         ))

#     # R-05 / R-06 : Échéance proche ou contrat expiré
#     date_fin = parsed.get('date_fin')
#     if date_fin:
#         try:
#             from datetime import datetime, date
#             fin = datetime.strptime(str(date_fin), '%Y-%m-%d').date()
#             jours_restants = (fin - date.today()).days

#             if 0 < jours_restants <= SEUIL_ECHEANCE_JOURS:
#                 risques.append(_risque(
#                     code        = 'R-05',
#                     type_risque = TYPE_RETARD,
#                     description = (
#                         f"Contrat expire dans {jours_restants} jour(s) "
#                         f"(le {fin.strftime('%d/%m/%Y')}). / "
#                         f"ينتهي العقد في غضون {jours_restants} يومًا "
#                         f"(بتاريخ {fin.strftime('%d/%m/%Y')})."
#                     ),
#                     severite    = SEV_CRITIQUE if jours_restants <= 7 else SEV_ELEVE,
#                     article_ref = 'Article 4 / Article 22',
#                     suggestion  = (
#                         "Lancer immédiatement la procédure de renouvellement "
#                         "ou de résiliation formelle. / "
#                         "الشروع فورًا في إجراءات التجديد أو الفسخ الرسمي للعقد."
#                     ),
#                 ))
#             elif jours_restants <= 0:
#                 risques.append(_risque(
#                     code        = 'R-06',
#                     type_risque = TYPE_RETARD,
#                     description = (
#                         f"Contrat expiré depuis le {fin.strftime('%d/%m/%Y')}. / "
#                         f"انتهت صلاحية العقد منذ تاريخ {fin.strftime('%d/%m/%Y')}."
#                     ),
#                     severite    = SEV_CRITIQUE,
#                     article_ref = 'Article 22',
#                     suggestion  = (
#                         "Régulariser immédiatement la situation contractuelle. / "
#                         "تسوية الوضعية التعاقدية فورًا."
#                     ),
#                 ))
#         except Exception:
#             pass

#     return risques
def _analyser_retard(parsed: dict, meta: dict) -> list:
    risques = []
    # delai   = meta.get('delai_livraison_mois')
    try:
        delai = int(meta.get('delai_livraison_mois') or parsed.get('delai_livraison_mois'))
    except (TypeError, ValueError):
        delai = None

    # R-01 : Délai de livraison excessif (> 7 mois)
    if delai is not None and delai > SEUIL_RETARD_MOIS:
        risques.append(_risque(
            code        = 'R-01',
            type_risque = TYPE_RETARD,
            description = (
                f"Délai de livraison de {delai} mois dépasse le seuil autorisé "
                f"de {SEUIL_RETARD_MOIS} mois. / "
                f"مدة التسليم المحددة بـ {delai} شهرًا تتجاوز الحد المسموح به "
                f"البالغ {SEUIL_RETARD_MOIS} شهرًا."
            ),
            severite    = SEV_CRITIQUE if delai > 12 else SEV_ELEVE,
            article_ref = 'Article 4',
            suggestion  = (
                "Réduire le délai ou obtenir une dérogation de la direction. "
                "Prévoir un plan de livraison par tranches. / "
                "تقليص المدة أو الحصول على ترخيص استثنائي من الإدارة، "
                "ووضع خطة تسليم على دفعات."
            ),
        ))

    # ═══════════════════════════════════════════════════════════════
    # R-07 / R-08 : Échéance de LIVRAISON (date_limite_livraison)
    # date_limite_livraison = date_debut + delai_livraison_mois
    # ═══════════════════════════════════════════════════════════════
    # date_debut = parsed.get('date_debut')
    date_debut = parsed.get('date_debut') or meta.get('date_debut')
    date_limite_livraison = ajouter_mois(date_debut, delai)

    if date_limite_livraison:
        jours_restants_livraison = (date_limite_livraison - date.today()).days

        # R-07 : Date limite de livraison proche (< 30 jours)
        if 0 < jours_restants_livraison <= SEUIL_ECHEANCE_JOURS:
            risques.append(_risque(
                code        = 'R-07',
                type_risque = TYPE_RETARD,
                description = (
                    f"La date limite de livraison approche : "
                    f"{jours_restants_livraison} jour(s) restant(s) "
                    f"(échéance le {date_limite_livraison.strftime('%d/%m/%Y')}). / "
                    f"اقترب الموعد النهائي للتسليم: "
                    f"باقي {jours_restants_livraison} يومًا "
                    f"(الموعد النهائي بتاريخ {date_limite_livraison.strftime('%d/%m/%Y')})."
                ),
                severite    = SEV_CRITIQUE if jours_restants_livraison <= 7 else SEV_ELEVE,
                article_ref = 'Article 4',
                suggestion  = (
                    "Vérifier l'état d'avancement de la livraison auprès du Fournisseur "
                    "et anticiper les pénalités de retard si nécessaire (Art. 5). / "
                    "التحقق من سير عملية التسليم لدى المورد والاستعداد لتطبيق "
                    "غرامات التأخير عند الحاجة (المادة 5)."
                ),
            ))

        # R-08 : Date limite de livraison dépassée
        elif jours_restants_livraison <= 0:
            jours_retard = abs(jours_restants_livraison)
            risques.append(_risque(
                code        = 'R-08',
                type_risque = TYPE_RETARD,
                description = (
                    f"La date limite de livraison est dépassée depuis "
                    f"{jours_retard} jour(s) (échéance prévue le "
                    f"{date_limite_livraison.strftime('%d/%m/%Y')}). / "
                    f"تجاوز الموعد النهائي للتسليم بـ {jours_retard} يومًا "
                    f"(كان الموعد المحدد بتاريخ "
                    f"{date_limite_livraison.strftime('%d/%m/%Y')})."
                ),
                severite    = SEV_CRITIQUE,
                article_ref = 'Article 4 / Article 5',
                suggestion  = (
                    "Appliquer les pénalités de retard prévues à l'Article 5 et "
                    "mettre en demeure le Fournisseur de livrer dans les plus brefs délais. / "
                    "تطبيق غرامات التأخير المنصوص عليها في المادة 5 وإعذار المورد "
                    "بالتسليم في أقرب الآجال."
                ),
            ))

    # # R-05 / R-06 : Échéance proche ou contrat expiré (basé sur date_fin)
    # date_fin = parsed.get('date_fin')
    # if date_fin:
    #     try:
    #         fin = datetime.strptime(str(date_fin), '%Y-%m-%d').date()
    #         jours_restants = (fin - date.today()).days

    #         if 0 < jours_restants <= SEUIL_ECHEANCE_JOURS:
    #             risques.append(_risque(
    #                 code        = 'R-05',
    #                 type_risque = TYPE_RETARD,
    #                 description = (
    #                     f"Contrat expire dans {jours_restants} jour(s) "
    #                     f"(le {fin.strftime('%d/%m/%Y')}). / "
    #                     f"ينتهي العقد في غضون {jours_restants} يومًا "
    #                     f"(بتاريخ {fin.strftime('%d/%m/%Y')})."
    #                 ),
    #                 severite    = SEV_CRITIQUE if jours_restants <= 7 else SEV_ELEVE,
    #                 article_ref = 'Article 4 / Article 22',
    #                 suggestion  = (
    #                     "Lancer immédiatement la procédure de renouvellement "
    #                     "ou de résiliation formelle. / "
    #                     "الشروع فورًا في إجراءات التجديد أو الفسخ الرسمي للعقد."
    #                 ),
    #             ))
    #         elif jours_restants <= 0:
    #             risques.append(_risque(
    #                 code        = 'R-06',
    #                 type_risque = TYPE_RETARD,
    #                 description = (
    #                     f"Contrat expiré depuis le {fin.strftime('%d/%m/%Y')}. / "
    #                     f"انتهت صلاحية العقد منذ تاريخ {fin.strftime('%d/%m/%Y')}."
    #                 ),
    #                 severite    = SEV_CRITIQUE,
    #                 article_ref = 'Article 22',
    #                 suggestion  = (
    #                     "Régulariser immédiatement la situation contractuelle. / "
    #                     "تسوية الوضعية التعاقدية فورًا."
    #                 ),
    #             ))
    #     except Exception:
    #         pass

    return risques
# ══════════════════════════════════════════════════════════════
# 2. RISQUES D'IMPRÉCISION
# ══════════════════════════════════════════════════════════════



def _analyser_imprecision(parsed: dict, meta: dict, texte: str) -> list:
    risques = []

    # I-01 : Montant manquant ou nul
    montant = parsed.get('montant')
    if not montant or float(montant) == 0:
        risques.append(_risque(
            code        = 'I-01',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Montant contractuel non renseigné ou égal à zéro. / "
                "المبلغ التعاقدي غير محدد أو يساوي صفرًا."
            ),
            severite    = SEV_ELEVE,
            article_ref = 'Article 8',
            suggestion  = (
                "Renseigner le montant global du contrat en DZD. / "
                "تحديد المبلغ الإجمالي للعقد بالدينار الجزائري."
            ),
        ))

    # # I-02 / I-03 / I-04 : Dates manquantes
    # labels_dates = {
    #     'date_debut':     ('début',     'تاريخ البداية',   'Article 4 / Article 22'),
    #     'date_fin':       ('fin',       'تاريخ النهاية',   'Article 4'),
    #     'date_signature': ('signature', 'تاريخ التوقيع',   'Article 22'),
    # }
    # for champ, (label_fr, label_ar, art) in labels_dates.items():
    #     if not parsed.get(champ):
    #         risques.append(_risque(
    #             code        = f'I-0{2 + ["date_debut","date_fin","date_signature"].index(champ)}',
    #             type_risque = TYPE_IMPRECISION,
    #             description = (
    #                 f"Date de {label_fr} non renseignée. / "
    #                 f"{label_ar} غير محدد."
    #             ),
    #             severite    = SEV_ELEVE,
    #             article_ref = art,
    #             suggestion  = (
    #                 f"Renseigner la date de {label_fr} au format YYYY-MM-DD. / "
    #                 f"تحديد {label_ar} بصيغة YYYY-MM-DD."
    #             ),
    #         ))

    # ═══════════════════════════════════════════════════════════════
    # I-05 / I-10 : Représentant Fournisseur (Partie B) complet
    # ═══════════════════════════════════════════════════════════════

    rep_b_nom = (
        parsed.get('societe_b_representant_nom') or
        parsed.get('representant_b_nom') or
        parsed.get('nom_fournisseur')
    )

    rep_b_fonction = (
        parsed.get('societe_b_representant_fonction') or
        parsed.get('representant_b_fonction') or
        parsed.get('fonction_fournisseur')
    )

    # Vérification du NOM
    if not rep_b_nom or not str(rep_b_nom).strip():
        risques.append(_risque(
            code        = 'I-5',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Nom du représentant du Fournisseur (Partie B) non renseigné. / "
                "اسم ممثل المورد (الطرف الثاني) غير محدد."
            ),
            severite    = SEV_MOYEN,
            article_ref = 'Article 22',
            suggestion  = (
                "Renseigner le nom du signataire pour le Fournisseur. / "
                "تحديد اسم الموقّع باسم المورد."
            ),
        ))

    # Vérification de la FONCTION (seulement si le nom existe)
    if rep_b_nom and str(rep_b_nom).strip():
        if not rep_b_fonction or not str(rep_b_fonction).strip():
            risques.append(_risque(
                code        = 'I-10',
                type_risque = TYPE_IMPRECISION,
                description = (
                    f"Fonction du représentant du Fournisseur ('{rep_b_nom}') non renseignée. / "
                    f"وظيفة ممثل المورد ('{rep_b_nom}') غير محددة."
                ),
                severite    = SEV_FAIBLE,
                article_ref = 'Article 22',
                suggestion  = (
                    "Renseigner la fonction du signataire (ex: Gérant, DG, Président). / "
                    "تحديد وظيفة الموقّع (مثل: مدير، مدير عام، رئيس)."
                ),
            ))

    # I-06 : Objet du contrat vide ou contient des blancs
    objet = parsed.get('objet') or ''
    if not objet or '____' in objet or len(objet.strip()) < 10:
        risques.append(_risque(
            code        = 'I-06',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Objet du contrat (Lot 01 / Lot 02) non défini. / "
                "موضوع العقد (الحصة 01 / الحصة 02) غير محدد."
            ),
            severite    = SEV_MOYEN,
            article_ref = 'Article 1.2',
            suggestion  = (
                "Décrire précisément la fourniture objet du contrat (lots, quantités, spécifications). / "
                "وصف موضوع التوريد بدقة (الحصص، الكميات، المواصفات)."
            ),
        ))

    # I-07 : Durée de garantie non renseignée
    if meta.get('duree_garantie_mois') is None:
        risques.append(_risque(
            code        = 'I-07',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Durée de garantie non définie dans le contrat. / "
                "مدة الضمان غير محددة في العقد."
            ),
            severite    = SEV_ELEVE,
            article_ref = 'Article 7',
            suggestion  = (
                "Définir la durée de garantie en mois à compter de la réception provisoire. / "
                "تحديد مدة الضمان بالأشهر ابتداءً من تاريخ الاستلام المؤقت."
            ),
        ))

    # I-08 : Caution bonne fin (DZD) non calculée
    if meta.get('caution_bonne_fin_pct') and not meta.get('caution_bonne_fin_dzd'):
        montant_val = float(parsed.get('montant') or 0)
        pct         = meta['caution_bonne_fin_pct']
        if montant_val > 0:
            calcule = montant_val * pct / 100
            risques.append(_risque(
                code        = 'I-08',
                type_risque = TYPE_IMPRECISION,
                description = (
                    f"Montant de la caution de bonne fin non renseigné. "
                    f"Valeur calculée : {calcule:,.2f} DZD ({pct}% de {montant_val:,.2f}). / "
                    f"مبلغ ضمان حسن التنفيذ غير محدد. "
                    f"القيمة المحسوبة: {calcule:,.2f} دج ({pct}% من {montant_val:,.2f})."
                ),
                severite    = SEV_MOYEN,
                article_ref = 'Article 10',
                suggestion  = (
                    f"Indiquer le montant exact de la caution : {calcule:,.2f} DZD. / "
                    f"تحديد المبلغ الدقيق للضمان: {calcule:,.2f} دج."
                ),
            ))
        else:
            risques.append(_risque(
                code        = 'I-08',
                type_risque = TYPE_IMPRECISION,
                description = (
                    "Montant de la caution de bonne fin non calculable (montant contrat manquant). / "
                    "تعذر حساب مبلغ ضمان حسن التنفيذ (مبلغ العقد غير محدد)."
                ),
                severite    = SEV_MOYEN,
                article_ref = 'Article 10',
                suggestion  = (
                    "Renseigner d'abord le montant du contrat, puis calculer la caution. / "
                    "تحديد مبلغ العقد أولاً، ثم حساب الضمان."
                ),
            ))

    delai = meta.get('delai_livraison_mois')

    # I-11 : Délai de livraison non défini
    if delai is None:
        risques.append(_risque(
            code        = 'I-11',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Délai de livraison non renseigné dans le contrat. / "
                "مدة التسليم غير محددة في العقد."
            ),
            severite    = SEV_ELEVE,
            article_ref = 'Article 4',
            suggestion  = (
                "Définir un délai de livraison précis en mois. / "
                "تحديد مدة تسليم دقيقة بالأشهر."
            ),
        ))

    # I-12 : Absence de pénalités de retard
    if meta.get('penalite_retard_pct') is None:
        risques.append(_risque(
            code        = 'I-12',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Aucune pénalité de retard définie dans le contrat. / "
                "لم يتم تحديد أي غرامة تأخير في العقد."
            ),
            severite    = SEV_ELEVE,
            article_ref = 'Article 5',
            suggestion  = (
                "Intégrer une clause de pénalité (minimum 1% par semaine, "
                "plafonnée à 10% du montant total). / "
                "إدراج بند غرامة تأخير (بحد أدنى 1% أسبوعيًا، وبحد أقصى "
                "10% من القيمة الإجمالية للعقد)."
            ),
        ))

    # I-13 : Absence de plafond pénalités
    if meta.get('penalite_plafond_pct') is None:
        risques.append(_risque(
            code        = 'I-13',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Plafond des pénalités de retard non défini. / "
                "لم يتم تحديد سقف غرامات التأخير."
            ),
            severite    = SEV_MOYEN,
            article_ref = 'Article 5',
            suggestion  = (
                "Définir un plafond de pénalités (standard Sonatrach : 10%). / "
                "تحديد سقف للغرامات (المعيار المعتمد لدى سوناطراك: 10%)."
            ),
        ))

    # ═══════════════════════════════════════════════════════════════
    # I-01 : Montant manquant ou nul (inchangé)
    # ═══════════════════════════════════════════════════════════════
    montant = parsed.get('montant')
    if not montant or float(montant) == 0:
        risques.append(_risque(
            code        = 'I-01',
            type_risque = TYPE_IMPRECISION,
            description = (
                "Montant contractuel non renseigné ou égal à zéro. / "
                "المبلغ التعاقدي غير محدد أو يساوي صفرًا."
            ),
            severite    = SEV_ELEVE,
            article_ref = 'Article 8',
            suggestion  = (
                "Renseigner le montant global du contrat en DZD. / "
                "تحديد المبلغ الإجمالي للعقد بالدينار الجزائري."
            ),
        ))

    

    # # I-09 : Champs template vides détectés dans le texte
    # blancs_detectes = len(re.findall(r'_{4,}', texte))
    # points_detectes = len(re.findall(r'[…\.]{5,}', texte))
    # total_blancs = blancs_detectes + points_detectes
    # if total_blancs > 5:
    #     risques.append(_risque(
    #         code        = 'I-09',
    #         type_risque = TYPE_IMPRECISION,
    #         description = (
    #             f"{total_blancs} champ(s) non renseigné(s) détecté(s) dans le document "
    #             f"({blancs_detectes} zones '____' + {points_detectes} zones '………'). / "
    #             f"تم اكتشاف {total_blancs} حقل/حقول غير معبأة في الوثيقة "
    #             f"({blancs_detectes} منطقة '____' + {points_detectes} منطقة '………')."
    #         ),
    #         severite    = SEV_MOYEN if total_blancs < 15 else SEV_ELEVE,
    #         article_ref = 'Global',
    #         suggestion  = (
    #             "Compléter tous les champs du template avant signature. "
    #             "Utiliser le formulaire de complétion CLM. / "
    #             "إكمال جميع حقول النموذج قبل التوقيع. "
    #             "استخدام استمارة الإتمام في نظام CLM."
    #         ),
    #     ))

    return risques


# ══════════════════════════════════════════════════════════════
# 3. RISQUES DE DIFFÉREND
# ══════════════════════════════════════════════════════════════

# def _analyser_different(parsed: dict, meta: dict, texte: str) -> list:
#     risques = []

#     # D-01 : Régime TVA ambigu
#     # Art. 12 mentionne TVA + exonération mais sans taux précis
#     tva_mention  = bool(re.search(r'\bTVA\b', texte))
#     taux_tva     = bool(re.search(r'TVA\s+de\s+\d+\s*%', texte))
#     exo_mention  = bool(re.search(r'exon[eé]r[eé]', texte, re.IGNORECASE))
#     if tva_mention and not taux_tva:
#         desc = (
#             "La TVA est mentionnée (Art. 12) mais son taux n'est pas précisé. "
#             "Mention d'exonération présente." if exo_mention else
#             "La TVA est mentionnée (Art. 12) mais son taux n'est pas précisé."
#         )
#         risques.append(_risque(
#             code        = 'D-01',
#             type_risque = TYPE_DIFFERENT,
#             description = desc,
#             severite    = SEV_ELEVE,
#             article_ref = 'Article 12',
#             suggestion  = (
#                 "Préciser le taux de TVA applicable ou confirmer l'exonération "
#                 "avec référence à l'arrêté interministériel du 07/12/1991."
#             ),
#         ))

#     # D-02 : Impôts / droits / taxes sans montant chiffré
#     impot_match = re.search(
#         r'[Ii]mp[ôo]ts?\s*,?\s*[Dd]roits?\s*(?:et\s*[Tt]axes?)?',
#         texte
#     )
#     montant_fiscal = re.search(
#         r'[Ii]mp[ôo]ts?.*?\d[\d\s.,]+\s*(?:DZD|DA|%)',
#         texte, re.DOTALL
#     )
#     if impot_match and not montant_fiscal:
#         risques.append(_risque(
#             code        = 'D-02',
#             type_risque = TYPE_DIFFERENT,
#             description = (
#                 "Clause fiscale présente (Art. 12 : impôts, droits et taxes) "
#                 "sans montant chiffré ni taux précis."
#             ),
#             severite    = SEV_ELEVE,
#             article_ref = 'Article 12',
#             suggestion  = (
#                 "Quantifier la charge fiscale applicable ou préciser que "
#                 "l'ensemble des impôts est à la charge du fournisseur (clause standard Sonatrach)."
#             ),
#         ))

#     # D-03 : Tribunal compétent absent
#     if not meta.get('tribunal_competent'):
#         # Vérifier aussi dans le texte
#         tribunal_dans_texte = bool(re.search(
#             r'tribunal\s+(?:territorialement\s+)?comp[eé]tent', texte, re.IGNORECASE
#         ))
#         if not tribunal_dans_texte:
#             risques.append(_risque(
#                 code        = 'D-03',
#                 type_risque = TYPE_DIFFERENT,
#                 description = "Juridiction compétente en cas de litige non définie.",
#                 severite    = SEV_ELEVE,
#                 article_ref = 'Article 19',
#                 suggestion  = (
#                     "Préciser le tribunal territorialement compétent "
#                     "(standard Sonatrach : Tribunal de Laghouat)."
#                 ),
#             ))

#     # D-04 : Clause de résiliation incomplète
#     resil_match = re.search(r'[Rr][eé]siliation', texte)
#     resil_preavis = re.search(r'r[eé]siliation.*?\d+\s*jours', texte, re.DOTALL)
#     if resil_match and not resil_preavis:
#         risques.append(_risque(
#             code        = 'D-04',
#             type_risque = TYPE_DIFFERENT,
#             description = (
#                 "Clause de résiliation présente (Art. 18) mais délai de préavis "
#                 "ou conditions de mise en demeure non précisés numériquement."
#             ),
#             severite    = SEV_MOYEN,
#             article_ref = 'Article 18',
#             suggestion  = (
#                 "Préciser le délai de mise en demeure avant résiliation "
#                 "(standard : 10 jours, Art. 18 §2)."
#             ),
#         ))

#     # D-05 : Clause de cession sans restriction explicite
#     cession_match  = re.search(r'[Cc]ession', texte)
#     cession_accord = re.search(r'accord\s+(?:écrit\s+)?(?:préalable\s+)?(?:et\s+)?express', texte, re.IGNORECASE)
#     if cession_match and not cession_accord:
#         risques.append(_risque(
#             code        = 'D-05',
#             type_risque = TYPE_DIFFERENT,
#             description = "Clause de cession présente (Art. 16) sans restriction explicite par écrit.",
#             severite    = SEV_MOYEN,
#             article_ref = 'Article 16',
#             suggestion  = (
#                 "Ajouter l'obligation d'accord écrit préalable et express du Client "
#                 "pour toute cession du contrat."
#             ),
#         ))

#     # D-06 : Force majeure sans délai de notification précis
#     fm_match  = re.search(r'[Ff]orce\s+[Mm]ajeure', texte)
#     fm_delai  = re.search(r'force\s+majeure.*?\d+\s*jours', texte, re.DOTALL | re.IGNORECASE)
#     if fm_match and not fm_delai:
#         risques.append(_risque(
#             code        = 'D-06',
#             type_risque = TYPE_DIFFERENT,
#             description = "Clause de force majeure (Art. 17) sans délai de notification chiffré.",
#             severite    = SEV_FAIBLE,
#             article_ref = 'Article 17',
#             suggestion  = (
#                 "Préciser le délai maximum de notification d'un cas de force majeure "
#                 "(standard : 15 jours après survenance)."
#             ),
#         ))

#     # D-07 : Caution bancaire insuffisante (< 10% standard Sonatrach)
#     caution_pct = meta.get('caution_bonne_fin_pct')
#     if caution_pct is not None and caution_pct < SEUIL_CAUTION_PCT:
#         risques.append(_risque(
#             code        = 'D-07',
#             type_risque = TYPE_DIFFERENT,
#             description = (
#                 f"Caution de bonne fin de {caution_pct}% inférieure au standard "
#                 f"Sonatrach de {SEUIL_CAUTION_PCT}%."
#             ),
#             severite    = SEV_ELEVE,
#             article_ref = 'Article 10',
#             suggestion  = f"Porter la caution de bonne fin à {SEUIL_CAUTION_PCT}% du montant contractuel.",
#         ))

#     return risques
def _analyser_different(parsed: dict, meta: dict, texte: str) -> list:
    risques = []

    # D-01 : Régime TVA ambigu
    tva_mention  = bool(re.search(r'\bTVA\b', texte))
    taux_tva     = bool(re.search(r'TVA\s+de\s+\d+\s*%', texte))
    exo_mention  = bool(re.search(r'exon[eé]r[eé]', texte, re.IGNORECASE))
    if tva_mention and not taux_tva:
        if exo_mention:
            desc = (
                "La TVA est mentionnée (Art. 12) mais son taux n'est pas précisé. "
                "Mention d'exonération présente. / "
                "الرسم على القيمة المضافة مذكور (المادة 12) دون تحديد نسبته. "
                "مع الإشارة إلى وجود إعفاء."
            )
        else:
            desc = (
                "La TVA est mentionnée (Art. 12) mais son taux n'est pas précisé. / "
                "الرسم على القيمة المضافة مذكور (المادة 12) دون تحديد نسبته."
            )
        risques.append(_risque(
            code        = 'D-01',
            type_risque = TYPE_DIFFERENT,
            description = desc,
            severite    = SEV_ELEVE,
            article_ref = 'Article 12',
            suggestion  = (
                "Préciser le taux de TVA applicable ou confirmer l'exonération "
                "avec référence à l'arrêté interministériel du 07/12/1991. / "
                "تحديد نسبة الرسم على القيمة المضافة المطبقة أو تأكيد الإعفاء "
                "بالإشارة إلى القرار الوزاري المشترك الصادر في 07/12/1991."
            ),
        ))

    # D-02 : Impôts / droits / taxes sans montant chiffré
    impot_match = re.search(
        r'[Ii]mp[ôo]ts?\s*,?\s*[Dd]roits?\s*(?:et\s*[Tt]axes?)?',
        texte
    )
    montant_fiscal = re.search(
        r'[Ii]mp[ôo]ts?.*?\d[\d\s.,]+\s*(?:DZD|DA|%)',
        texte, re.DOTALL
    )
    if impot_match and not montant_fiscal:
        risques.append(_risque(
            code        = 'D-02',
            type_risque = TYPE_DIFFERENT,
            description = (
                "Clause fiscale présente (Art. 12 : impôts, droits et taxes) "
                "sans montant chiffré ni taux précis. / "
                "يوجد بند ضريبي (المادة 12: الضرائب والرسوم) دون تحديد "
                "مبلغ أو نسبة دقيقة."
            ),
            severite    = SEV_ELEVE,
            article_ref = 'Article 12',
            suggestion  = (
                "Quantifier la charge fiscale applicable ou préciser que "
                "l'ensemble des impôts est à la charge du fournisseur "
                "(clause standard Sonatrach). / "
                "تحديد قيمة العبء الضريبي المطبق أو الإشارة إلى أن جميع "
                "الضرائب على عاتق المورد (البند المعتاد لدى سوناطراك)."
            ),
        ))

    # D-03 : Tribunal compétent absent
    if not meta.get('tribunal_competent'):
        tribunal_dans_texte = bool(re.search(
            r'tribunal\s+(?:territorialement\s+)?comp[eé]tent', texte, re.IGNORECASE
        ))
        if not tribunal_dans_texte:
            risques.append(_risque(
                code        = 'D-03',
                type_risque = TYPE_DIFFERENT,
                description = (
                    "Juridiction compétente en cas de litige non définie. / "
                    "الجهة القضائية المختصة في حال النزاع غير محددة."
                ),
                severite    = SEV_ELEVE,
                article_ref = 'Article 19',
                suggestion  = (
                    "Préciser le tribunal territorialement compétent "
                    "(standard Sonatrach : Tribunal de Laghouat). / "
                    "تحديد المحكمة المختصة إقليميًا "
                    "(المعيار المعتمد لدى سوناطراك: محكمة الأغواط)."
                ),
            ))

    # D-04 : Clause de résiliation incomplète
    resil_match = re.search(r'[Rr][eé]siliation', texte)
    resil_preavis = re.search(r'r[eé]siliation.*?\d+\s*jours', texte, re.DOTALL)
    if resil_match and not resil_preavis:
        risques.append(_risque(
            code        = 'D-04',
            type_risque = TYPE_DIFFERENT,
            description = (
                "Clause de résiliation présente (Art. 18) mais délai de préavis "
                "ou conditions de mise en demeure non précisés numériquement. / "
                "يوجد بند فسخ (المادة 18) دون تحديد رقمي لمدة الإشعار المسبق "
                "أو شروط الإعذار."
            ),
            severite    = SEV_MOYEN,
            article_ref = 'Article 18',
            suggestion  = (
                "Préciser le délai de mise en demeure avant résiliation "
                "(standard : 10 jours, Art. 18 §2). / "
                "تحديد مدة الإعذار قبل الفسخ (المعيار: 10 أيام، المادة 18 الفقرة 2)."
            ),
        ))

    # D-05 : Clause de cession sans restriction explicite
    cession_match  = re.search(r'[Cc]ession', texte)
    cession_accord = re.search(r'accord\s+(?:écrit\s+)?(?:préalable\s+)?(?:et\s+)?express', texte, re.IGNORECASE)
    if cession_match and not cession_accord:
        risques.append(_risque(
            code        = 'D-05',
            type_risque = TYPE_DIFFERENT,
            description = (
                "Clause de cession présente (Art. 16) sans restriction explicite par écrit. / "
                "يوجد بند تنازل (المادة 16) دون قيد صريح كتابي."
            ),
            severite    = SEV_MOYEN,
            article_ref = 'Article 16',
            suggestion  = (
                "Ajouter l'obligation d'accord écrit préalable et express du Client "
                "pour toute cession du contrat. / "
                "إضافة شرط الموافقة الكتابية المسبقة والصريحة من الزبون "
                "لأي تنازل عن العقد."
            ),
        ))

    # D-06 : Force majeure sans délai de notification précis
    fm_match  = re.search(r'[Ff]orce\s+[Mm]ajeure', texte)
    fm_delai  = re.search(r'force\s+majeure.*?\d+\s*jours', texte, re.DOTALL | re.IGNORECASE)
    if fm_match and not fm_delai:
        risques.append(_risque(
            code        = 'D-06',
            type_risque = TYPE_DIFFERENT,
            description = (
                "Clause de force majeure (Art. 17) sans délai de notification chiffré. / "
                "يوجد بند القوة القاهرة (المادة 17) دون تحديد رقمي لمدة الإشعار."
            ),
            severite    = SEV_FAIBLE,
            article_ref = 'Article 17',
            suggestion  = (
                "Préciser le délai maximum de notification d'un cas de force majeure "
                "(standard : 15 jours après survenance). / "
                "تحديد المدة القصوى للإشعار بحالة القوة القاهرة "
                "(المعيار: 15 يومًا بعد وقوعها)."
            ),
        ))

    # D-07 : Caution bancaire insuffisante (< 10% standard Sonatrach)
    caution_pct = meta.get('caution_bonne_fin_pct')
    if caution_pct is not None and caution_pct < SEUIL_CAUTION_PCT:
        risques.append(_risque(
            code        = 'D-07',
            type_risque = TYPE_DIFFERENT,
            description = (
                f"Caution de bonne fin de {caution_pct}% inférieure au standard "
                f"Sonatrach de {SEUIL_CAUTION_PCT}%. / "
                f"ضمان حسن التنفيذ بنسبة {caution_pct}% أقل من المعيار المعتمد "
                f"لدى سوناطراك البالغ {SEUIL_CAUTION_PCT}%."
            ),
            severite    = SEV_ELEVE,
            article_ref = 'Article 10',
            suggestion  = (
                f"Porter la caution de bonne fin à {SEUIL_CAUTION_PCT}% du montant contractuel. / "
                f"رفع ضمان حسن التنفيذ إلى {SEUIL_CAUTION_PCT}% من المبلغ التعاقدي."
            ),
        ))

    return risques
def get_niveau_escalade(occurrence_count: int) -> dict:
    """
    Retourne le niveau d'alerte selon le nombre d'occurrences du même risque.
    """
    if occurrence_count == 1:
        return {
            'niveau':    'warning',
            'label':     'Avertissement / تنبيه',
            'escalader': False,
            'notifier':  'chef_departement',
        }
    elif occurrence_count == 2:
        return {
            'niveau':    'alert',
            'label':     'Alerte / إنذار',
            'escalader': False,
            'notifier':  'directeur_direction',
        }
    else:
        return {
            'niveau':    'escalade',
            'label':     f'Escalade (occurrence #{occurrence_count}) / تصعيد (التكرار رقم {occurrence_count})',
            'escalader': True,
            'notifier':  'directeur_activite',
        }



"""
À AJOUTER à la fin de clm/risk_engine.py
(après get_niveau_escalade)

Fonction d'orchestration : analyse + notification en une seule étape.
"""

from .notification_client import envoyer_alertes_risque


def analyser_et_notifier(parsed: dict, texte: str, contrat_id: int, jwt_token: str) -> dict:
    """
    Orchestrateur principal :
      1. Analyse les risques du contrat
      2. Détermine le niveau d'escalade pour chaque risque RETARD
      3. Envoie les alertes au service Notification

    Args:
        parsed      : dict retourné par parse_contract_data()
        texte       : texte brut du PDF
        contrat_id  : ID Django du contrat
        jwt_token   : JWT de l'utilisateur courant (propagé vers Node)

    Returns:
        {
            'risques':      [...],   # tous les risques détectés
            'notification': {...},   # résultat envoi
        }
    """
    # 1. Analyse complète
    risques = analyser_risques(parsed, texte)

    # 2. Enrichir chaque risque retard avec le niveau d'escalade
    #    (basé sur occurrence_count stocké en base — voir view ci-dessous)
    for r in risques:
        if r.get('type') == 'retard':
            # occurrence_count sera rempli par la view avant d'appeler cette fn
            occ = r.get('occurrence_count', 1)
            r['escalade'] = get_niveau_escalade(occ)

    # 3. Notifier le service Notification (non bloquant : erreur loguée seulement)
    notif_result = envoyer_alertes_risque(contrat_id, risques, jwt_token)

    return {
        'risques':      risques,
        'notification': notif_result,
    }
# # ══════════════════════════════════════════════════════════════
# RÉCURRENCE DES RISQUES
# ══════════════════════════════════════════════════════════════

def get_niveau_escalade(occurrence_count: int) -> dict:
    """
    Retourne le niveau d'alerte selon le nombre d'occurrences du même risque.

    - 1 occurrence  → WARNING  (information chef de département)
    - 2 occurrences → ALERT    (notification direction)
    - 3+            → ESCALADE (escalade automatique niveau supérieur)
    """
    if occurrence_count == 1:
        return {
            'niveau':    'warning',
            'label':     'Avertissement',
            'escalader': False,
            'notifier':  'chef_departement',
        }
    elif occurrence_count == 2:
        return {
            'niveau':    'alert',
            'label':     'Alerte',
            'escalader': False,
            'notifier':  'directeur_direction',
        }
    else:
        return {
            'niveau':    'escalade',
            'label':     f'Escalade (occurrence #{occurrence_count})',
            'escalader': True,
            'notifier':  'directeur_activite',
        }