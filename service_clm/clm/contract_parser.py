# # clm/contract_parser.py
# """
# Parser qui cherche dans le texte extrait les informations du contrat
# en utilisant des expressions régulières (regex).

# Les patterns sont adaptés aux contrats algériens (SONATRACH),
# mais facilement extensibles.
# """

# import re
# from dateutil import parser as date_parser
# from datetime import date
# import logging

# logger = logging.getLogger(__name__)


# def parse_contract_data(text: str) -> dict:
#     """
#     Analyse le texte extrait et retourne un dict avec les champs trouvés.
    
#     Tous les champs sont optionnels (None si non trouvé).
#     Le frontend / l'utilisateur devra compléter les champs manquants.
#     """
#     result = {
#         'numero_contrat':     _extract_numero_contrat(text),
#         'titre':              _extract_titre(text),
#         'type_contrat':       _extract_type_contrat(text),
#         'partie_b_nom':       _extract_partie_b(text),
#         'pays_partie_b':      _extract_pays(text),
#         'objet':              _extract_objet(text),
#         'date_signature':     _extract_date(text, ['signé', 'signature', 'signed']),
#         'date_debut':         _extract_date(text, ['début', 'commencement', 'entrée en vigueur', 'start']),
#         'date_fin':           _extract_date(text, ['fin', 'expiration', 'échéance', 'end']),
#         'montant':            _extract_montant(text),
#         'devise':             _extract_devise(text),
#         'conditions_paiement':_extract_paiement(text),
#     }
    
#     # Log ce qui a été trouvé
#     found = [k for k, v in result.items() if v is not None]
#     logger.info(f'[PARSER] Champs trouvés : {found}')
    
#     return result


# # ─────────────────────────────────────────────────────────
# # Fonctions internes (privées)
# # ─────────────────────────────────────────────────────────

# # def _extract_numero_contrat(text: str):
# #     """
# #     Cherche des patterns comme :
# #     - N° 2024/DRH/001
# #     - Contrat n° CLM-2024-042
# #     - Contract No. SONA-2024-007
# #     """
# #     patterns = [
# #         r'[Nn][°º]\s*([A-Z0-9\-/]{5,30})',
# #         r'[Nn]um[eé]ro\s*[:\s]\s*([A-Z0-9\-/]{5,30})',
# #         r'[Cc]ontract\s+[Nn]o\.?\s*([A-Z0-9\-/]{5,30})',
# #         r'[Rr][eé]f[eé]rence\s*[:\s]\s*([A-Z0-9\-/]{5,30})',
# #     ]
# #     return _first_match(text, patterns)
# def _extract_numero_contrat(text: str):

#     patterns = [
#         r'(CTR[-/]?\d{4}[-/]?\d+)',
#         r'(CLM[-/]?\d{4}[-/]?\d+)',
#         r'[Nn][°º]?\s*[:\-]?\s*([A-Z0-9\-/]{5,30})',
#         r'[Nn]um[eé]ro\s*(?:de)?\s*(?:contrat)?\s*[:\-]?\s*([A-Z0-9\-/]{5,30})',
#         r'[Rr][eé]f[eé]rence\s*[:\-]?\s*([A-Z0-9\-/]{5,30})',
#     ]

#     return _first_match(text, patterns)

# def _extract_titre(text: str):
#     """Cherche la ligne après 'CONTRAT DE' ou 'ACCORD' """
#     patterns = [
#         r'CONTRAT\s+(?:DE\s+)?(.{10,80}?)(?:\n|$)',
#         r'ACCORD\s+(?:DE\s+)?(.{10,80}?)(?:\n|$)',
#         r'CONVENTION\s+(?:DE\s+)?(.{10,80}?)(?:\n|$)',
#         r'[Oo]bjet\s*[:\s]\s*(.{10,120}?)(?:\n|$)',
#     ]
#     return _first_match(text, patterns)


# def _extract_type_contrat(text: str):
#     """
#     Retourne un code parmi les choices Django :
#     prestation, fourniture, travaux, consultation, partenariat, autre
#     """
#     text_lower = text.lower()
#     mapping = {
#         'prestation':   ['prestation', 'service', 'services'],
#         'fourniture':   ['fourniture', 'livraison', 'supply'],
#         'travaux':      ['travaux', 'construction', 'works', 'engineering'],
#         'consultation': ['consultation', 'conseil', 'advisory', 'consulting'],
#         'partenariat':  ['partenariat', 'partnership', 'joint venture', 'coopération'],
#     }
#     for code, keywords in mapping.items():
#         if any(kw in text_lower for kw in keywords):
#             return code
#     return 'autre'


# # def _extract_partie_b(text: str):
# #     """Cherche la seconde partie contractante"""
# #     patterns = [
# #         r'[Pp]artie\s+[Bb]\s*[:\-]\s*(.{3,80}?)(?:\n|,)',
# #         r'[Ee]ntre\s+.*?et\s+la?\s+[Ss]oci[eé]t[eé]\s+(.{3,80}?)(?:\n|,)',
# #         r'[Cc]ontractor\s*[:\-]\s*(.{3,80}?)(?:\n|$)',
# #         r'[Pp]restataire\s*[:\-]\s*(.{3,80}?)(?:\n|$)',
# #         r'[Ff]ournisseur\s*[:\-]\s*(.{3,80}?)(?:\n|$)',
# #     ]
# #     return _first_match(text, patterns)
# def _extract_partie_b(text: str):

#     patterns = [
#         r'la société\s+([A-Z][A-Z\s&\-]{3,60})',
#         r'Partie\s*B\s*[:\-]?\s*([A-Z][A-Z\s&\-]{3,60})',
#         r'Fournisseur\s*[:\-]?\s*([A-Z][A-Z\s&\-]{3,60})',
#         r'Prestataire\s*[:\-]?\s*([A-Z][A-Z\s&\-]{3,60})',
#         r'et\s+la\s+société\s+([A-Z][A-Z\s&\-]{3,60})',
#     ]

#     value = _first_match(text, patterns)

#     if value:
#         value = re.sub(r'\s+', ' ', value)
#         return value.strip()

#     return None

# def _extract_partie_a(text: str):

#     patterns = [
#         r'Partie\s*A\s*[:\-]?\s*([A-Z][A-Z\s&\-.]{3,80})',
#         r'Client\s*[:\-]?\s*([A-Z][A-Z\s&\-.]{3,80})',
#         r'Entreprise\s*[:\-]?\s*([A-Z][A-Z\s&\-.]{3,80})',
#         r'Entre\s+la\s+société\s+([A-Z][A-Z\s&\-.]{3,80})',
#     ]

#     value = _first_match(text, patterns)

#     if value:
#         value = re.sub(r'\s+', ' ', value)
#         return value.strip()

#     return None
# def _extract_pays(text: str):
#     """Cherche le pays de la partie B"""
#     pays_connus = [
#         'Algérie', 'Algeria', 'France', 'Italie', 'Italy', 'Espagne', 'Spain',
#         'Allemagne', 'Germany', 'États-Unis', 'USA', 'United States',
#         'Chine', 'China', 'Russie', 'Russia', 'Royaume-Uni', 'UK', 'Maroc',
#         'Tunisie', 'Libye', 'Egypte', 'Egypt', 'Turquie', 'Turkey',
#         'Japon', 'Japan', 'Brésil', 'Brazil', 'Canada', 'Inde', 'India',
#     ]
#     for pays in pays_connus:
#         if re.search(r'\b' + re.escape(pays) + r'\b', text, re.IGNORECASE):
#             return pays
#     return None


# # def _extract_objet(text: str):
# #     """Extrait l'objet du contrat"""
# #     patterns = [
# #         r'[Oo]bjet\s+du\s+[Cc]ontrat\s*[:\-]\s*(.{20,300}?)(?:\n\n|\Z)',
# #         r'[Oo]bjet\s*[:\-]\s*(.{20,300}?)(?:\n\n|\Z)',
# #         r'[Ss]ujet\s*[:\-]\s*(.{20,300}?)(?:\n\n|\Z)',
# #         r'[Pp]ortée\s*[:\-]\s*(.{20,300}?)(?:\n\n|\Z)',
# #     ]
# #     return _first_match(text, patterns)
# def _extract_objet(text: str):

#     patterns = [
#         r'[Oo]bjet\s*[:\-]\s*(.{10,120}?)(?:Date|Montant|Conditions|\n|$)',
#     ]

#     value = _first_match(text, patterns)

#     if value:
#         return value.strip()

#     return None

# # def _extract_date(text: str, keywords: list):
# #     """
# #     Cherche une date proche d'un mot-clé.
# #     Retourne une string 'YYYY-MM-DD' ou None.
# #     """
# #     # Pattern de date : JJ/MM/AAAA, JJ-MM-AAAA, AAAA-MM-JJ, "15 janvier 2024"
# #     date_patterns = [
# #         r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}',
# #         r'\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}',
# #         r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|'
# #         r'septembre|octobre|novembre|décembre|january|february|march|april|'
# #         r'may|june|july|august|september|october|november|december)\s+\d{4}',
# #     ]
    
# #     # Chercher dans une fenêtre de 150 caractères autour du mot-clé
# #     for keyword in keywords:
# #         pattern = re.compile(
# #             re.escape(keyword) + r'.{0,150}?(' + '|'.join(date_patterns) + r')',
# #             re.IGNORECASE | re.DOTALL
# #         )
# #         match = pattern.search(text)
# #         if match:
# #             date_str = match.group(1)
# #             try:
# #                 parsed = date_parser.parse(date_str, dayfirst=True)
# #                 return parsed.strftime('%Y-%m-%d')
# #             except Exception:
# #                 pass
# #     return None
# def _extract_date(text: str, keywords: list):

#     date_patterns = [
#         r'\d{4}-\d{2}-\d{2}',
#         r'\d{2}/\d{2}/\d{4}',
#         r'\d{2}-\d{2}-\d{4}',
#     ]

#     for keyword in keywords:

#         pattern = re.compile(
#             re.escape(keyword) + r'.{0,120}?(' + '|'.join(date_patterns) + r')',
#             re.IGNORECASE | re.DOTALL
#         )

#         match = pattern.search(text)

#         if match:

#             date_str = match.group(1)

#             try:

#                 if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
#                     parsed = date_parser.parse(date_str)

#                 else:
#                     parsed = date_parser.parse(date_str, dayfirst=True)

#                 return parsed.strftime('%Y-%m-%d')

#             except Exception:
#                 pass

#     return None

# def _extract_montant(text: str):
#     """
#     Cherche des montants comme :
#     - 1 500 000,00 DZD
#     - USD 250,000.00
#     - € 50.000
#     """
#     patterns = [
#         r'[Mm]ontant\s*[:\-]?\s*([\d\s.,]+)',
#         r'[Pp]rix\s+(?:global|total|forfaitaire)?\s*[:\-]?\s*([\d\s.,]+)',
#         r'[Vv]aleur\s*[:\-]?\s*([\d\s.,]+)',
#         r'([\d\s.,]+)\s*(?:DZD|USD|EUR|€|\$)',
#     ]
#     raw = _first_match(text, patterns)
#     if raw:
#         # Nettoyer : enlever espaces, garder chiffres et séparateur décimal
#         cleaned = re.sub(r'[^\d.,]', '', raw)
#         # Convertir virgule décimale en point
#         if ',' in cleaned and '.' in cleaned:
#             cleaned = cleaned.replace(',', '')
#         elif ',' in cleaned:
#             cleaned = cleaned.replace(',', '.')
#         try:
#             return float(cleaned)
#         except ValueError:
#             pass
#     return None


# def _extract_devise(text: str):
#     """Cherche la devise utilisée"""
#     devises = {
#         'DZD': ['DZD', 'DA ', 'dinars algériens', 'dinar algérien'],
#         'USD': ['USD', 'US$', 'dollars américains', 'dollar américain'],
#         'EUR': ['EUR', '€', 'euros'],
#         'GBP': ['GBP', '£', 'livres sterling'],
#     }
#     for code, patterns in devises.items():
#         if any(p in text for p in patterns):
#             return code
#     return 'DZD'  # défaut


# def _extract_paiement(text: str):
#     """Extrait les conditions de paiement"""
#     patterns = [
#         r'[Cc]onditions?\s+de\s+paiement\s*[:\-]\s*(.{10,200}?)(?:\n\n|\Z)',
#         r'[Mm]odalit[eé]s?\s+de\s+paiement\s*[:\-]\s*(.{10,200}?)(?:\n\n|\Z)',
#         r'[Pp]ayment\s+[Tt]erms?\s*[:\-]\s*(.{10,200}?)(?:\n\n|\Z)',
#     ]
#     return _first_match(text, patterns)


# def _first_match(text: str, patterns: list):
#     """Essaie chaque pattern et retourne le premier groupe trouvé, nettoyé."""
#     for pattern in patterns:
#         match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
#         if match:
#             value = match.group(1).strip()
#             # Enlever les sauts de ligne internes
#             value = re.sub(r'\s+', ' ', value)
#             if len(value) > 2:
#                 return value
#     return None
# clm/contract_parser.py
# """
# Parser regex pour contrats Sonatrach (type fourniture, services, travaux).
# Extrait les champs standards + métadonnées spécifiques.
# """

# import re
# from dateutil import parser as date_parser
# import logging

# logger = logging.getLogger(__name__)


# # ══════════════════════════════════════════════════════════════
# # POINT D'ENTRÉE PRINCIPAL
# # ══════════════════════════════════════════════════════════════

# def parse_contract_data(text: str) -> dict:
#     """
#     Analyse le texte extrait et retourne un dict avec :
#       - champs standards du modèle Contrat
#       - metadonnees : champs spécifiques fourniture (Art. 4-22)
#       - risques_detectes : liste de risques calculés
#     """
#     result = {
#         'numero_contrat':      _extract_numero_contrat(text),
#         'titre':               _extract_titre(text),
#         'type_contrat':        _extract_type_contrat(text),
#         'partie_a_nom':        _extract_partie_a(text),
#         'partie_b_nom':        _extract_partie_b(text),
#         'pays_partie_b':       _extract_pays(text),
#         'objet':               _extract_objet(text),
#         'date_signature':      _extract_date(text, ['signé', 'signature', 'signed']),
#         'date_debut':          _extract_date(text, ['entrée en vigueur', 'mise en vigueur', 'début']),
#         'date_fin':            _extract_date(text, ['fin', 'expiration', 'échéance']),
#         'montant':             _extract_montant(text),
#         'devise':              _extract_devise(text),
#         'conditions_paiement': _extract_paiement(text),
#         'metadonnees':         _extract_metadonnees_fourniture(text),
#         'risques_detectes':    [],   # rempli après, voir risk_engine.py
#     }

#     found = [k for k, v in result.items() if v not in [None, {}, []]]
#     logger.info(f'[PARSER] Champs trouvés : {found}')
#     return result


# # ══════════════════════════════════════════════════════════════
# # CHAMPS STANDARDS
# # ══════════════════════════════════════════════════════════════

# def _extract_numero_contrat(text: str):
#     patterns = [
#         r'(CTR[-/]?\d{4}[-/]?\d+)',
#         r'(CLM[-/]?\d{4}[-/]?\d+)',
#         r'[Pp]rojet\s+de\s+contrat\s+[Nn][°º]?\s*[-–]?\s*([A-Z0-9\-/]{3,30})',
#         r'[Nn][°º]\s*[-–]?\s*([A-Z0-9\-/]{4,30})',
#         r'[Nn]um[eé]ro\s*(?:de)?\s*(?:contrat)?\s*[:\-]?\s*([A-Z0-9\-/]{4,30})',
#         r'[Rr][eé]f[eé]rence\s*[:\-]?\s*([A-Z0-9\-/]{4,30})',
#     ]
#     return _first_match(text, patterns)


# def _extract_titre(text: str):
#     patterns = [
#         r'[«"]\s*(Fourniture\s+[^»"]{5,100})\s*[»"]',
#         r'CONTRAT\s+(?:DE\s+)?(.{10,80}?)(?:\n|$)',
#         r'La\s+Fourniture\s+de\s*[:\-]?\s*(.{5,100}?)(?:\n|$)',
#         r'[Oo]bjet\s*[:\-]\s*(.{10,120}?)(?:\n|$)',
#     ]
#     return _first_match(text, patterns)


# def _extract_type_contrat(text: str):
#     text_lower = text.lower()
#     mapping = {
#         'fourniture':  ['fourniture', 'livraison', 'supply', 'équipements', 'matériels'],
#         'service':     ['prestation', 'service', 'services'],
#         'travaux':     ['travaux', 'construction', 'works', 'engineering', 'réalisation'],
#         'partenariat': ['partenariat', 'partnership', 'joint venture', 'coopération'],
#         'vente':       ['vente', 'cession', 'sale'],
#         'transfert':   ['transfert', 'transfer', 'cession de droits'],
#     }
#     for code, keywords in mapping.items():
#         if any(kw in text_lower for kw in keywords):
#             return code
#     return 'service'


# def _extract_partie_a(text: str):
#     # Sonatrach est toujours la partie A dans ce contexte
#     if re.search(r'sonatrach', text, re.IGNORECASE):
#         return 'SONATRACH'
#     patterns = [
#         r'Partie\s*A\s*[:\-]?\s*([A-Z][A-Z\s&\-.]{3,80})',
#         r'[Cc]lient\s*[:\-]\s*([A-Z][A-Z\s&\-.]{3,80})',
#         r'[Ee]ntre\s+la\s+soci[eé]t[eé]\s+([A-Z][A-Z\s&\-.]{3,60})',
#     ]
#     return _first_match(text, patterns) or 'SONATRACH'


# def _extract_partie_b(text: str):
#     patterns = [
#         r'[Ll]a\s+soci[eé]t[eé]\s*:\s*_{5,}',    # champ vide → None
#         r'[Ff]ournisseur\s*:\s*([A-Z][A-Z\s&\-\.]{3,80})',
#         r'[Pp]restataire\s*[:\-]\s*([A-Z][A-Z\s&\-\.]{3,80})',
#         r'[Pp]artie\s*[Bb]\s*[:\-]\s*([A-Z][A-Z\s&\-\.]{3,80})',
#         r'[Dd]ésigne\s+la\s+soci[eé]t[eé]\s+([A-Z][A-Z\s&\-\.]{3,80})',
#     ]
#     value = _first_match(text, patterns)
#     if value and len(value.replace('_', '').strip()) < 3:
#         return None   # champ vide dans le template
#     return value.strip() if value else None


# def _extract_pays(text: str):
#     pays_connus = [
#         'Algérie', 'Algeria', 'France', 'Italie', 'Italy', 'Espagne', 'Spain',
#         'Allemagne', 'Germany', 'États-Unis', 'USA', 'United States',
#         'Chine', 'China', 'Russie', 'Russia', 'Royaume-Uni', 'UK',
#         'Maroc', 'Tunisie', 'Libye', 'Egypte', 'Egypt',
#         'Turquie', 'Turkey', 'Japon', 'Japan', 'Canada', 'Inde', 'India',
#     ]
#     # Chercher dans le contexte "Siège Social" pour la partie B
#     siege_match = re.search(
#         r'[Ss]i[èe]ge\s+[Ss]ocial\s+(?:est\s+au|:\s*)(.{5,80})',
#         text, re.IGNORECASE
#     )
#     if siege_match:
#         ctx = siege_match.group(1)
#         for pays in pays_connus:
#             if re.search(r'\b' + re.escape(pays) + r'\b', ctx, re.IGNORECASE):
#                 return pays

#     for pays in pays_connus:
#         if re.search(r'\b' + re.escape(pays) + r'\b', text, re.IGNORECASE):
#             return pays
#     return None


# def _extract_objet(text: str):
#     patterns = [
#         r'[Ll]ot\s+(?:n[°º]?\s*)?0?1\s*[:\-]\s*(.{5,120}?)(?:Lot|Article|\n)',
#         r'[Oo]bjet\s+du\s+[Cc]ontrat\s*[:\-]\s*(.{10,300}?)(?:\n\n|\Z)',
#         r'[Oo]bjet\s*[:\-]\s*(.{10,200}?)(?:\n\n|\Z)',
#         r's\'engage\s+[àa]\s+fournir\s+au\s+[Cc]lient\s+(.{10,200}?)(?:,|\n)',
#     ]
#     value = _first_match(text, patterns)
#     if value and '____' in value:
#         return None   # champ vide
#     return value.strip() if value else None


# def _extract_date(text: str, keywords: list):
#     date_patterns = [
#         r'\d{4}-\d{2}-\d{2}',
#         r'\d{2}/\d{2}/\d{4}',
#         r'\d{2}-\d{2}-\d{4}',
#         r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|'
#         r'septembre|octobre|novembre|décembre)\s+\d{4}',
#     ]
#     for keyword in keywords:
#         pattern = re.compile(
#             re.escape(keyword) + r'.{0,150}?(' + '|'.join(date_patterns) + r')',
#             re.IGNORECASE | re.DOTALL
#         )
#         match = pattern.search(text)
#         if match:
#             date_str = match.group(1)
#             try:
#                 parsed = date_parser.parse(date_str, dayfirst=True)
#                 return parsed.strftime('%Y-%m-%d')
#             except Exception:
#                 pass
#     return None


# def _extract_montant(text: str):
#     patterns = [
#         r'[Mm]ontant\s+global.*?s\'[eé]l[eè]ve\s+[àa]\s+la\s+somme\s+de\s*[:\-]?\s*([\d\s.,]+)',
#         r'[Mm]ontant\s+[Cc]ontractuel\s*[:\-]?\s*([\d\s.,]+)',
#         r'[Mm]ontant\s*[:\-]?\s*([\d\s.,]+)',
#         r'[Pp]rix\s+(?:global|total|forfaitaire)\s*[:\-]?\s*([\d\s.,]+)',
#         r'([\d\s.,]+)\s*(?:DZD|DA\b|Dinars)',
#     ]
#     raw = _first_match(text, patterns)
#     if raw:
#         cleaned = re.sub(r'[^\d.,]', '', raw)
#         if ',' in cleaned and '.' in cleaned:
#             cleaned = cleaned.replace(' ', '').replace(',', '')
#         elif ',' in cleaned:
#             cleaned = cleaned.replace(',', '.')
#         try:
#             val = float(cleaned)
#             return val if val > 0 else None
#         except ValueError:
#             pass
#     return None


# def _extract_devise(text: str):
#     devises = {
#         'DZD': ['DZD', r'\bDA\b', 'dinars algériens', 'dinar algérien', 'Dinars'],
#         'USD': ['USD', r'US\$', 'dollars américains'],
#         'EUR': ['EUR', '€', 'euros'],
#         'GBP': ['GBP', '£', 'livres sterling'],
#     }
#     for code, patterns in devises.items():
#         for p in patterns:
#             if re.search(p, text):
#                 return code
#     return 'DZD'


# def _extract_paiement(text: str):
#     patterns = [
#         r'[Cc]onditions?\s+de\s+paiement\s*[:\-]\s*(.{10,300}?)(?:\n\n|\Z)',
#         r'[Mm]odalit[eé]s?\s+de\s+paiement\s*[:\-]\s*(.{10,300}?)(?:\n\n|\Z)',
#         r'[Pp]aiement.{0,30}?(?:virement|chèque|espèces).{0,200}?(?:\n\n|\Z)',
#     ]
#     return _first_match(text, patterns)


# # ══════════════════════════════════════════════════════════════
# # MÉTADONNÉES SPÉCIFIQUES FOURNITURE (Art. 4 → Art. 22)
# # ══════════════════════════════════════════════════════════════

# def _extract_metadonnees_fourniture(text: str) -> dict:
#     """
#     Extrait les 10 champs métier spécifiques au contrat type fourniture Sonatrach.
#     Les valeurs absentes restent None → déclenchent les risques IMPRÉCISION.
#     """
#     meta = {}

#     # ── Art. 4 : Délai de livraison ───────────────────────────────────
#     # "dans un délai de … Mois à compter de la mise en vigueur"
#     m = re.search(
#         r'[Ll]ivraison\s+(?:compl[eè]te\s+)?(?:de\s+la\s+fourniture\s+)?'
#         r'interviendra\s+au\s+plus\s+tard\s+dans\s+un\s+d[eé]lai\s+de\s+'
#         r'([.\w]+)\s*[Mm]ois',
#         text
#     )
#     if not m:
#         m = re.search(r'd[eé]lai\s+de\s+(\d+)\s*[Mm]ois', text)
#     if m:
#         val = m.group(1).strip()
#         # Le template contient "………" → ignorer
#         if re.match(r'^\d+$', val):
#             meta['delai_livraison_mois'] = int(val)
#     # Si non trouvé → None → risque IMPRÉCISION

#     # ── Art. 5 : Pénalité de retard ───────────────────────────────────
#     # "pénalité de retard de un pourcent (1%)"
#     m = re.search(
#         r'p[eé]nalit[eé]\s+de\s+retard\s+de\s+\w+\s+pourcent\s*\((\d+)%?\)',
#         text, re.IGNORECASE
#     )
#     if not m:
#         m = re.search(
#             r'p[eé]nalit[eé].*?(\d+(?:[.,]\d+)?)\s*(?:pourcent|%)\s*(?:du\s+montant)?\s*par\s+semaine',
#             text, re.IGNORECASE
#         )
#     if m:
#         meta['penalite_retard_pct'] = float(m.group(1).replace(',', '.'))

#     # ── Art. 5 : Plafond des pénalités ───────────────────────────────
#     # "ne pourra excéder dix pourcent (10%)"
#     m = re.search(
#         r'ne\s+pourra\s+exc[eé]der\s+\w+\s+pourcent\s*\((\d+)%?\)',
#         text, re.IGNORECASE
#     )
#     if not m:
#         m = re.search(
#             r'(?:maximum|plafonn[eé]|ne\s+pourra\s+exc[eé]der).*?(\d+)\s*(?:pourcent|%)',
#             text, re.IGNORECASE
#         )
#     if m:
#         meta['penalite_plafond_pct'] = float(m.group(1))

#     # ── Art. 7 : Durée de garantie ───────────────────────────────────
#     # "garantit … pendant une durée de ……. (….) mois"
#     m = re.search(
#         r'[Gg]arantit?\s+.{0,100}?pendant\s+une\s+dur[eé]e\s+de\s+'
#         r'([.\w]+)\s*\(?[.\w]*\)?\s*[Mm]ois',
#         text, re.DOTALL
#     )
#     if m:
#         val = m.group(1).strip()
#         if re.match(r'^\d+$', val):
#             meta['duree_garantie_mois'] = int(val)

#     # ── Art. 9 : Délai de paiement ────────────────────────────────────
#     # "dans les trente (30) jours"
#     m = re.search(
#         r'(?:trente|30)\s*\(?\s*30\s*\)?\s*jours',
#         text, re.IGNORECASE
#     )
#     if m:
#         meta['delai_paiement_jours'] = 30
#     else:
#         m = re.search(r'dans\s+les\s+(\d+)\s*jours', text, re.IGNORECASE)
#         if m:
#             meta['delai_paiement_jours'] = int(m.group(1))

#     # ── Art. 10 : Caution bonne fin (%) ──────────────────────────────
#     # "caution bancaire de bonne fin … de dix pourcent (10%)"
#     m = re.search(
#         r'[Cc]aution\s+bancaire\s+de\s+bonne\s+fin\s+.{0,50}?'
#         r'\w+\s+pourcent\s*\((\d+)%?\)',
#         text, re.DOTALL
#     )
#     if not m:
#         m = re.search(
#             r'[Cc]aution.*?(\d+)\s*(?:pourcent|%)\s*du\s+montant',
#             text, re.IGNORECASE | re.DOTALL
#         )
#     if m:
#         meta['caution_bonne_fin_pct'] = int(m.group(1))

#     # ── Art. 10 : Caution bonne fin (DZD) ───────────────────────────
#     # "soit : ……………………………… (……………..DZD)"
#     m = re.search(
#         r'[Cc]aution.*?soit\s*[:\-]?\s*([\d\s.,]+)\s*\((.{3,30}?DZD)\)',
#         text, re.DOTALL
#     )
#     if m:
#         raw = m.group(1).strip()
#         if re.search(r'\d', raw):
#             meta['caution_bonne_fin_dzd'] = re.sub(r'\s+', '', raw)

#     # ── Art. 19 : Tribunal compétent ─────────────────────────────────
#     # "tribunal territorialement compétent de Laghouat"
#     m = re.search(
#         r'tribunal\s+territorialement\s+comp[eé]tent\s+de\s+([A-ZÀ-Ü][a-zà-ü\-]+)',
#         text, re.IGNORECASE
#     )
#     if m:
#         meta['tribunal_competent'] = m.group(1).strip()

#     # ── Art. 20 : Langue ─────────────────────────────────────────────
#     m = re.search(r'r[eé]dig[eé]\s+en\s+langue\s+(fran[cç]aise|anglaise|arabe)', text, re.IGNORECASE)
#     if m:
#         meta['langue_contrat'] = m.group(1).lower()
#     elif re.search(r'langue\s+fran[cç]aise', text, re.IGNORECASE):
#         meta['langue_contrat'] = 'français'

#     # ── Art. 20 : Nombre d'originaux ─────────────────────────────────
#     # "rédigé en langue française en dix (10) originaux"
#     m = re.search(r'en\s+\w+\s+\((\d+)\)\s+originaux', text, re.IGNORECASE)
#     if not m:
#         m = re.search(r'(\d+)\s+originaux', text, re.IGNORECASE)
#     if m:
#         meta['nb_originaux'] = int(m.group(1))

#     return meta

# clm/contract_parser.py
"""
Parser regex — Contrats Sonatrach type fourniture.
v2 : societe_a_nom / societe_b_nom + 18 nouveaux champs extraits du PDF.
"""

import re
from dateutil import parser as date_parser
import logging

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ══════════════════════════════════════════════════════════════════

def parse_contract_data(text: str) -> dict:
    """
    Analyse le texte extrait et retourne un dict complet avec :
      - champs standards (modèle Contrat)
      - metadonnees : champs spécifiques fourniture
      - contacts    : représentants, fax, téléphone, email
      - signatures  : nom/prénom/fonction × 2 parties (Art. 22)
      - risques_detectes : liste calculée (voir risk_engine.py)
    """
    contacts   = _extract_contacts(text)
    signatures = _extract_signatures(text)

    result = {
        # ── Champs standards ──────────────────────────────────────
        'numero_contrat':      _extract_numero_contrat(text),
        'titre':               _extract_titre(text),
        'type_contrat':        _extract_type_contrat(text),

        # ── Parties — RENOMMÉS v2 ─────────────────────────────────
        'societe_a_nom':  _extract_societe_a(text),   # ancien: partie_a_nom
        'societe_b_nom':  _extract_societe_b(text),   # ancien: partie_b_nom

        'pays_partie_b':       _extract_pays(text),
        'objet':               _extract_objet(text),
        'date_signature':      _extract_date(text, ['signé', 'signature']),
        'date_debut':          _extract_date(text, ['entrée en vigueur', 'mise en vigueur']),
        'date_fin':            _extract_date(text, ['fin', 'expiration', 'échéance']),
        'montant':             _extract_montant(text),
        'devise':              _extract_devise(text),
        'conditions_paiement': _extract_paiement(text),

        # ── Représentants ─────────────────────────────────────────
        'societe_a_representant_nom':      contacts.get('representant_a_nom'),
        'societe_a_representant_prenom':   signatures.get('nom_client'),   # Art.22
        'societe_a_representant_fonction': contacts.get('representant_a_fonction'),
        'societe_b_siege_social':          _extract_siege_social(text),
        'societe_b_representant_nom':      contacts.get('representant_b_nom'),
        'societe_b_representant_prenom':   signatures.get('prenom_fournisseur'),
        'societe_b_representant_fonction': contacts.get('representant_b_fonction'),
        

        # ── Contacts Art. 21 ──────────────────────────────────────
        'notification_adresse_ligne1': contacts.get('adresse_ligne1'),
        'notification_adresse_ligne2': contacts.get('adresse_ligne2'),
        'fax_fournisseur':             contacts.get('fax'),
        'telephone_fournisseur':       contacts.get('telephone'),
        'email_fournisseur':           contacts.get('email'),

        # ── Signatures Art. 22 ────────────────────────────────────
        'nom_client':           signatures.get('nom_client'),
        'prenom_client':        signatures.get('prenom_client'),
        'fonction_client':      signatures.get('fonction_client'),
        'nom_fournisseur':      signatures.get('nom_fournisseur'),
        'prenom_fournisseur':   signatures.get('prenom_fournisseur'),
        'fonction_fournisseur': signatures.get('fonction_fournisseur'),

        # ── Métadonnées + risques ─────────────────────────────────
        'metadonnees':      _extract_metadonnees_fourniture(text),
        'risques_detectes': [],
    }

    found   = [k for k, v in result.items() if v not in [None, {}, [], '']]
    missing = [k for k, v in result.items() if v in [None, {}, [], '']]
    logger.info(f'[PARSER] Trouvés: {len(found)} | Manquants: {len(missing)}')
    logger.debug(f'[PARSER] Manquants: {missing}')
    return result


# ══════════════════════════════════════════════════════════════════
# CHAMPS STANDARDS
# ══════════════════════════════════════════════════════════════════

def _extract_numero_contrat(text: str):
    patterns = [
        r'[Pp]rojet\s+de\s+contrat\s+[Nn][°º]?\s*[-–]?\s*([A-Z0-9\-/]{3,30})',
        r'(CTR[-/]?\d{4}[-/]?\d+)',
        r'(CLM[-/]?\d{4}[-/]?\d+)',
        r'[Nn][°º]\s*[-–]?\s*([A-Z0-9\-/]{4,30})',
        r'[Nn]um[eé]ro\s*(?:de)?\s*(?:contrat)?\s*[:\-]?\s*([A-Z0-9\-/]{4,30})',
    ]
    return _first_match(text, patterns)


def _extract_titre(text: str):
    patterns = [
        r'[«"]\s*(Fourniture\s+[^»"]{5,100})\s*[»"]',
        r'La\s+Fourniture\s+de\s*[:\-]?\s*(.{5,100}?)(?:\n|$)',
        r'CONTRAT\s+(?:DE\s+)?(.{10,80}?)(?:\n|$)',
    ]
    return _first_match(text, patterns)


def _extract_type_contrat(text: str):
    text_lower = text.lower()
    mapping = {
        'fourniture':  ['fourniture', 'livraison', 'équipements', 'matériels'],
        'service':     ['prestation', 'service', 'services'],
        'travaux':     ['travaux', 'construction', 'réalisation'],
        'partenariat': ['partenariat', 'joint venture', 'coopération'],
        'vente':       ['vente', 'cession', 'sale'],
        'transfert':   ['transfert', 'cession de droits'],
    }
    for code, keywords in mapping.items():
        if any(kw in text_lower for kw in keywords):
            return code
    return 'service'


# ── Parties — RENOMMÉS v2 ─────────────────────────────────────────

def _extract_societe_a(text: str):
    """Extrait la dénomination de la Partie A (Client). Ancien nom: _extract_partie_a."""
    # Art. 1.1 : "Client : Désigne …………………………………………………….
    m = re.search(r'[Cc]lient\s*:\s*[Dd][eé]signe\s+(.{5,120}?)(?:\.|$|\n)', text)
    if m:
        val = m.group(1).strip()
        if '…' not in val and '____' not in val and len(val) > 3:
            return val

    if re.search(r'sonatrach', text, re.IGNORECASE):
        return 'SONATRACH'

    patterns = [
        r'[Ee]ntre\s*:\s*La\s+[Ss]oci[eé]t[eé]\s+([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\.]{3,80})',
        r'[Cc]lient\s*[:\-]\s*([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\.]{3,80})',
        r'[Pp]artie\s*A\s*[:\-]?\s*([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\.]{3,80})',
    ]
    return _first_match(text, patterns) or 'SONATRACH'


def _extract_societe_b(text: str):
    """Extrait la dénomination de la Partie B (Fournisseur). Ancien nom: _extract_partie_b."""
    # Art. 1.1 : "Fournisseur : Désigne la société …………………………………………...
    m = re.search(
        r'[Ff]ournisseur\s*:\s*[Dd][eé]signe\s+la\s+soci[eé]t[eé]\s+(.{5,120}?)(?:\.|$|\n)',
        text
    )
    if m:
        val = m.group(1).strip()
        if '…' not in val and '____' not in val and len(val) > 3:
            return val

    patterns = [
        r'[Ll]a\s+soci[eé]t[eé]\s*:\s*([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\.]{3,80})',
        r'[Ff]ournisseur\s*:\s*([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\.]{3,80})',
        r'[Pp]artie\s*[Bb]\s*[:\-]\s*([A-ZÀ-Ü][A-Za-zÀ-ÿ\s&\-\.]{3,80})',
    ]
    value = _first_match(text, patterns)
    if value and len(value.replace('_', '').strip()) < 3:
        return None
    return value.strip() if value else None


def _extract_siege_social(text: str):
    m = re.search(
        r'[Ss]i[èe]ge\s+[Ss]ocial\s+est\s+au\s*:\s*([^\n_]{5,200})',
        text
    )
    if m:
        val = m.group(1).strip()
        if '____' not in val and '…' not in val:
            return val
    return None


# ── Autres champs standards ──────────────────────────────────────

def _extract_pays(text: str):
    pays_connus = [
        'Algérie', 'Algeria', 'France', 'Italie', 'Espagne', 'Allemagne',
        'États-Unis', 'USA', 'Chine', 'Russie', 'Royaume-Uni', 'UK',
        'Maroc', 'Tunisie', 'Libye', 'Egypte', 'Turquie', 'Japon',
        'Canada', 'Inde', 'Belgique', 'Pays-Bas', 'Suisse', 'Autriche',
    ]
    siege_match = re.search(
        r'[Ss]i[èe]ge\s+[Ss]ocial\s+(?:est\s+au|:\s*)(.{5,80})',
        text, re.IGNORECASE
    )
    if siege_match:
        ctx = siege_match.group(1)
        for pays in pays_connus:
            if re.search(r'\b' + re.escape(pays) + r'\b', ctx, re.IGNORECASE):
                return pays
    for pays in pays_connus:
        if re.search(r'\b' + re.escape(pays) + r'\b', text, re.IGNORECASE):
            return pays
    return None


def _extract_objet(text: str):
    # Essayer d'extraire les deux lots
    lot1 = None
    lot2 = None
    m1 = re.search(r'[Ll]ot\s+(?:n[°º]?\s*)?0?1\s*[:\-]\s*([^;\n_\.]{5,120})', text)
    m2 = re.search(r'[Ll]ot\s+(?:n[°º]?\s*)?0?2\s*[:\-]\s*([^;\n_\.]{5,120})', text)
    if m1 and '____' not in m1.group(1):
        lot1 = m1.group(1).strip()
    if m2 and '____' not in m2.group(1):
        lot2 = m2.group(1).strip()

    if lot1 or lot2:
        parts = []
        if lot1: parts.append(f"Lot 01 : {lot1}")
        if lot2: parts.append(f"Lot 02 : {lot2}")
        return " | ".join(parts)

    patterns = [
        r'[Oo]bjet\s+du\s+[Cc]ontrat\s*[:\-]\s*(.{10,300}?)(?:\n\n|\Z)',
        r's\'engage\s+[àa]\s+fournir\s+au\s+[Cc]lient\s+(.{10,200}?)(?:,|\n)',
    ]
    return _first_match(text, patterns)


def _extract_date(text: str, keywords: list):
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}/\d{2}/\d{4}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|'
        r'septembre|octobre|novembre|décembre)\s+\d{4}',
    ]
    for keyword in keywords:
        pattern = re.compile(
            re.escape(keyword) + r'.{0,150}?(' + '|'.join(date_patterns) + r')',
            re.IGNORECASE | re.DOTALL
        )
        match = pattern.search(text)
        if match:
            try:
                return date_parser.parse(match.group(1), dayfirst=True).strftime('%Y-%m-%d')
            except Exception:
                pass
    return None


def _extract_montant(text: str):
    patterns = [
        r'[Mm]ontant\s+global.*?s\'[eé]l[eè]ve\s+[àa]\s+la\s+somme\s+de\s*[:\-]?\s*([\d\s.,]+)',
        r'[Mm]ontant\s+[Cc]ontractuel\s*[:\-]?\s*([\d\s.,]+)',
        r'[Mm]ontant\s*[:\-]?\s*([\d\s.,]+)',
        r'[Pp]rix\s+(?:global|total|forfaitaire)\s*[:\-]?\s*([\d\s.,]+)',
        r'([\d\s.,]+)\s*(?:DZD|DA\b|Dinars)',
    ]
    raw = _first_match(text, patterns)
    if raw:
        cleaned = re.sub(r'[^\d.,]', '', raw)
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
        try:
            val = float(cleaned)
            return val if val > 0 else None
        except ValueError:
            pass
    return None


def _extract_devise(text: str):
    devises = {
        'DZD': ['DZD', r'\bDA\b', 'dinars algériens', 'Dinars'],
        'USD': ['USD', r'US\$', 'dollars américains'],
        'EUR': ['EUR', '€', 'euros'],
        'GBP': ['GBP', '£', 'livres sterling'],
    }
    for code, patterns in devises.items():
        for p in patterns:
            if re.search(p, text):
                return code
    return 'DZD'


def _extract_paiement(text: str):
    patterns = [
        r'[Cc]onditions?\s+de\s+paiement\s*[:\-]\s*(.{10,300}?)(?:\n\n|\Z)',
        r'[Mm]odalit[eé]s?\s+de\s+paiement\s*[:\-]\s*(.{10,300}?)(?:\n\n|\Z)',
        r'paiement.{0,30}?virement\s+bancaire.{0,200}?(?:\n\n|\Z)',
    ]
    return _first_match(text, patterns)


# ══════════════════════════════════════════════════════════════════
# CONTACTS ART. 21 — NOUVEAUX
# ══════════════════════════════════════════════════════════════════

def _extract_contacts(text: str) -> dict:
    """
    Extrait tous les contacts de l'Art. 21 :
    adresse, fax, téléphone, email + représentants des deux parties (pages 1 & 2).
    """
    contacts = {}

    # ── Fax (Art. 21) ─────────────────────────────────────────────
    m = re.search(r'[Ff]ax\s*:\s*([+\d\s\-\./()]{4,30}?)(?:\n|Télé|Email)', text)
    if m:
        val = m.group(1).strip()
        if '…' not in val and val:
            contacts['fax'] = val

    # ── Téléphone (Art. 21) ───────────────────────────────────────
    m = re.search(r'[Tt][eé]l[eé]phone\s*:\s*([+\d\s\-\./()]{4,30}?)(?:\n|Email)', text)
    if m:
        val = m.group(1).strip()
        if '…' not in val and val:
            contacts['telephone'] = val

    # ── Email (Art. 21) ───────────────────────────────────────────
    m = re.search(r'[Ee]mail\s*:\s*([\w.\-+]+@[\w.\-]+\.[a-z]{2,6})', text)
    if m:
        contacts['email'] = m.group(1).strip()

    # ── Adresses notifications (Art. 21) ─────────────────────────
    art21_block = re.search(
        r'[Nn]otifications?\s*\n(.{10,500}?)[Aa]rticle\s+22',
        text, re.DOTALL
    )
    if art21_block:
        lines = [l.strip() for l in art21_block.group(1).splitlines()
                 if l.strip() and '…' not in l and '____' not in l
                 and not re.match(r'^(Fax|Télé|Email|Pour)', l)]
        if len(lines) >= 1: contacts['adresse_ligne1'] = lines[0]
        if len(lines) >= 2: contacts['adresse_ligne2'] = lines[1]

    # ── Représentant Partie A / Client (page 1) ───────────────────
    # Pattern: "Monsieur : ___, Fonction : ___" dans le bloc Client
    client_bloc = re.search(
        r'[Dd][eé]sign[eé]e?\s+ci\s+apr[eè]s\s+par\s+l\'expression\s+"?\s*le\s+Client\s*"?'
        r'.{0,300}?[Mm]onsieur\s*:\s*([^,\n_]{3,60}?),\s*[Ff]onction\s*:\s*([^,\n_]{3,80})',
        text, re.DOTALL
    )
    if client_bloc:
        nom = client_bloc.group(1).strip()
        fct = client_bloc.group(2).strip()
        if '____' not in nom:  contacts['representant_a_nom']      = nom
        if '____' not in fct:  contacts['representant_a_fonction']  = fct

    # ── Représentant Partie B / Fournisseur (page 2) ──────────────
    fourn_bloc = re.search(
        r'[Dd][eé]sign[eé]e?\s+ci\s+apr[eè]s\s+par\s+l\'expression\s+"?\s*le\s+Fournisseur\s*"?'
        r'.{0,300}?[Mm]onsieur\s*:\s*([^,\n_]{3,60}?),\s*[Ff]onction\s*:\s*([^,\n_]{3,80})',
        text, re.DOTALL
    )
    if fourn_bloc:
        nom = fourn_bloc.group(1).strip()
        fct = fourn_bloc.group(2).strip()
        if '____' not in nom:  contacts['representant_b_nom']      = nom
        if '____' not in fct:  contacts['representant_b_fonction']  = fct

    return contacts


# ══════════════════════════════════════════════════════════════════
# SIGNATURES ART. 22 — NOUVEAUX
# ══════════════════════════════════════════════════════════════════

def _extract_signatures(text: str) -> dict:
    """
    Extrait le tableau de signatures Art. 22 :
      Pour le Client  : Nom / Prénom / Fonction
      Pour le Fournisseur : Nom / Prénom / Fonction
    """
    sigs = {}

    # Isoler le bloc Art. 22
    art22 = re.search(
        r'[Aa]rticle\s+22\s*[:\-]?\s*Entr[eé]e\s+en\s+[Vv]igueur(.+?)$',
        text, re.DOTALL
    )
    bloc = art22.group(1) if art22 else text

    # ── Bloc "Pour le Client" ──────────────────────────────────────
    client_bloc = re.search(
        r'[Pp]our\s+le\s+[Cc]lient\s*:(.*?)(?:[Pp]our\s+le\s+[Ff]ournisseur|$)',
        bloc, re.DOTALL
    )
    if client_bloc:
        b = client_bloc.group(1)
        for field, label in [('nom_client', 'Nom'), ('prenom_client', 'Pr[eé]nom'),
                              ('fonction_client', 'Fonction')]:
            m = re.search(rf'{label}\s*:\s*([A-Za-zÀ-ÿ\s\-\.\']+?)(?:\n|$)', b)
            if m and '____' not in m.group(1) and len(m.group(1).strip()) > 1:
                sigs[field] = m.group(1).strip()

    # ── Bloc "Pour le Fournisseur" ────────────────────────────────
    fourn_bloc = re.search(
        r'[Pp]our\s+le\s+[Ff]ournisseur\s*:(.*?)$',
        bloc, re.DOTALL
    )
    if fourn_bloc:
        b = fourn_bloc.group(1)
        for field, label in [('nom_fournisseur', 'Nom'), ('prenom_fournisseur', 'Pr[eé]nom'),
                              ('fonction_fournisseur', 'Fonction')]:
            m = re.search(rf'{label}\s*:\s*([A-Za-zÀ-ÿ\s\-\.\']+?)(?:\n|$)', b)
            if m and '____' not in m.group(1) and len(m.group(1).strip()) > 1:
                sigs[field] = m.group(1).strip()

    return sigs


# ══════════════════════════════════════════════════════════════════
# MÉTADONNÉES SPÉCIFIQUES FOURNITURE
# ══════════════════════════════════════════════════════════════════

def _extract_metadonnees_fourniture(text: str) -> dict:
    meta = {}

    # ── Lots (Art. 1.2) ───────────────────────────────────────────
    for n in ['01', '02', '1', '2']:
        m = re.search(rf'[Ll]ot\s+(?:n[°º]?\s*)?0?{n.lstrip("0") or "0"}\s*[:\-]\s*([^;\n_\.{{}}]{{5,120}})', text)
        key = f'lot_0{n.lstrip("0") or "1"}'
        if m and '____' not in m.group(1):
            meta[key] = m.group(1).strip()

    # ── Art. 4 : Délai de livraison ───────────────────────────────
    m = re.search(
        r'livraison\s+.*?dans\s+un\s+d[eé]lai\s+de\s+([.\w]+)\s*[Mm]ois',
        text, re.IGNORECASE
    )
    if not m:
        m = re.search(r'd[eé]lai\s+de\s+(\d+)\s*[Mm]ois', text)
    if m and re.match(r'^\d+$', m.group(1).strip()):
        meta['delai_livraison_mois'] = int(m.group(1))

    # ── Art. 5 : Pénalités ────────────────────────────────────────
    m = re.search(r'p[eé]nalit[eé].*?un\s+pourcent\s*\((\d+)%?\)', text, re.IGNORECASE)
    if m: meta['penalite_retard_pct'] = float(m.group(1))

    m = re.search(r'ne\s+pourra\s+exc[eé]der\s+\w+\s+pourcent\s*\((\d+)%?\)', text, re.IGNORECASE)
    if m: meta['penalite_plafond_pct'] = float(m.group(1))

    m = re.search(r'p[eé]nalit[eé].*?dans\s+un\s+d[eé]lai\s+de\s+quinze\s*\((\d+)\)\s*jours', text, re.IGNORECASE | re.DOTALL)
    if m: meta['penalite_delai_paiement_jours'] = int(m.group(1))
    else: meta['penalite_delai_paiement_jours'] = 15  # valeur fixe Art. 5

    # ── Art. 6 : Réception définitive ────────────────────────────
    m = re.search(
        r'r[eé]ception\s+d[eé]finitive\s+.*?d[eé]lai\s+de\s+\.+\s*\(\.+\)\s*[Mm]ois',
        text, re.IGNORECASE | re.DOTALL
    )
    if not m:
        m = re.search(r'r[eé]ception\s+d[eé]finitive.*?(\d+)\s*\(.*?\)\s*[Mm]ois', text, re.IGNORECASE | re.DOTALL)
    if m:
        g = m.group(1) if m.lastindex else None
        if g and re.match(r'^\d+$', g):
            meta['delai_reception_definitive_mois'] = int(g)

    # ── Art. 7 : Garantie ─────────────────────────────────────────
    m = re.search(r'[Gg]arantit?\s+.*?pendant\s+une\s+dur[eé]e\s+de\s+([.\w]+)\s*\(?.*?\)?\s*[Mm]ois',
                  text, re.DOTALL)
    if m and re.match(r'^\d+$', m.group(1).strip()):
        meta['duree_garantie_mois'] = int(m.group(1))

    # ── Art. 9 : Paiement ─────────────────────────────────────────
    m = re.search(r'trente\s*\(?\s*30\s*\)?\s*jours', text, re.IGNORECASE)
    meta['delai_paiement_jours'] = 30 if m else None

    m = re.search(r'six\s*\(?\s*06\s*\)?\s*exemplaires', text, re.IGNORECASE)
    if m: meta['nb_exemplaires_facture'] = 6

    # ── Art. 10 : Caution ─────────────────────────────────────────
    m = re.search(r'[Cc]aution.*?dix\s+pourcent\s*\((\d+)%?\)', text, re.IGNORECASE | re.DOTALL)
    if m: meta['caution_bonne_fin_pct'] = int(m.group(1))

    m = re.search(r'[Cc]aution.*?soit\s*[:\-]?\s*([\d\s.,]+)\s*\((.{3,30}?DZD)\)',
                  text, re.DOTALL)
    if m:
        raw = m.group(1).strip()
        if re.search(r'\d', raw):
            meta['caution_bonne_fin_dzd'] = re.sub(r'\s+', '', raw)

    m = re.search(r'[Cc]aution.*?trente\s*\(?\s*30\s*\)?\s*jours', text, re.IGNORECASE | re.DOTALL)
    if m: meta['caution_delai_mise_en_place_jours'] = 30

    m = re.search(r'[Cc]aution.*?lib[eé]r[eé]e\s+.*?un\s*\(?\s*01?\s*\)?\s*mois', text, re.IGNORECASE | re.DOTALL)
    if m: meta['caution_liberation_delai_mois'] = 1

    # ── Art. 11 : Banque Fournisseur ──────────────────────────────
    m = re.search(r'[Bb]anque\s*:\s*([^\n…_]{3,100})', text)
    if m and '…' not in m.group(1):
        meta['banque_fournisseur_nom'] = m.group(1).strip()

    m = re.search(r'[Aa]dresse\s*[:\-]?\s*([^\n…_]{5,200})', text)
    if m and '…' not in m.group(1):
        meta['banque_fournisseur_adresse'] = m.group(1).strip()

    m = re.search(r'[Cc]ompte\s+[Bb]ancaire\s+[Nn][°º]?\s*[:\-]?\s*([\d\s\-]{5,40})', text)
    if m and '…' not in m.group(1):
        meta['banque_fournisseur_compte'] = m.group(1).strip()

    # ── Art. 12 : Régime TVA ──────────────────────────────────────
    if re.search(r'exon[eé]r[eé]', text, re.IGNORECASE):
        meta['regime_tva'] = 'exonéré'

    # ── Art. 14 : Langue documentation ───────────────────────────
    m = re.search(r'documentation\s+technique.*?en\s+langue\s+(fran[cç]aise|anglaise|arabe)', text, re.IGNORECASE)
    if m: meta['langue_documentation'] = m.group(1).lower()
    else: meta['langue_documentation'] = 'français'

    # ── Art. 17 : Force majeure ───────────────────────────────────
    m = re.search(r'force\s+majeure.*?quinze\s*\((\d+)\)\s*jours', text, re.IGNORECASE | re.DOTALL)
    if m: meta['force_majeure_notif_jours'] = int(m.group(1))
    else:
        m = re.search(r'force\s+majeure.*?(\d+)\s*jours', text, re.IGNORECASE | re.DOTALL)
        if m: meta['force_majeure_notif_jours'] = int(m.group(1))

    # ── Art. 18 : Résiliation ─────────────────────────────────────
    m = re.search(r'r[eé]siliation.*?dix\s*\((\d+)\)\s*jours.*?mise\s+en\s+demeure', text, re.IGNORECASE | re.DOTALL)
    if m: meta['resiliation_demeure_jours'] = int(m.group(1))
    else: meta['resiliation_demeure_jours'] = 10  # valeur fixe Art. 18

    m = re.search(r'r[eé]siliation.*?trente\s*\((\d+)\)\s*jours.*?r[eé]ception', text, re.IGNORECASE | re.DOTALL)
    if m: meta['resiliation_expedition_jours'] = int(m.group(1))
    else: meta['resiliation_expedition_jours'] = 30  # valeur fixe Art. 18

    # ── Art. 19 : Tribunal ────────────────────────────────────────
    m = re.search(r'tribunal\s+territorialement\s+comp[eé]tent\s+de\s+([A-ZÀ-Ü][a-zà-ü\-]+)', text, re.IGNORECASE)
    if m: meta['tribunal_competent'] = m.group(1).strip()

    # ── Art. 20 : Langue & originaux ─────────────────────────────
    m = re.search(r'r[eé]dig[eé]\s+en\s+langue\s+(fran[cç]aise|anglaise|arabe)', text, re.IGNORECASE)
    if m: meta['langue_contrat'] = m.group(1).lower()
    elif re.search(r'langue\s+fran[cç]aise', text, re.IGNORECASE):
        meta['langue_contrat'] = 'français'

    m = re.search(r'en\s+\w+\s+\((\d+)\)\s+originaux', text, re.IGNORECASE)
    if m: meta['nb_originaux'] = int(m.group(1))

    m = re.search(r'(\d+)\s*\(0?\d+\)\s*conserv[eé]s\s+par\s+le\s+[Ff]ournisseur', text, re.IGNORECASE)
    if m: meta['nb_originaux_fournisseur'] = int(m.group(1))
    else: meta['nb_originaux_fournisseur'] = 2

    m = re.search(r'(\d+)\s*\(0?\d+\)\s*(?:conserv[eé]s\s+)?par\s+le\s+[Cc]lient', text, re.IGNORECASE)
    if m: meta['nb_originaux_client'] = int(m.group(1))
    else: meta['nb_originaux_client'] = 8

    return meta


# ══════════════════════════════════════════════════════════════════
# UTILITAIRE
# ══════════════════════════════════════════════════════════════════

def _first_match(text: str, patterns: list):
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            val = m.group(1).strip() if m.lastindex else m.group(0).strip()
            if val and '____' not in val and len(val.replace('…', '').strip()) > 2:
                return val
    return None