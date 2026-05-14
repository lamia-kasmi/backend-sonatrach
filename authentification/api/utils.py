# authentification/api/utils.py

def nom_complet(user):
    """Retourne le nom complet d'un utilisateur"""
    if not user:
        return ""
    prenom = getattr(user, 'prenom', '') or ''
    nom = getattr(user, 'nom', '') or ''
    return f"{prenom} {nom}".strip()