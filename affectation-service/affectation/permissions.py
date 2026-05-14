from rest_framework.permissions import BasePermission


def get_role(user):
    return str(getattr(user, 'role', '')).lower().strip()





class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return get_role(request.user) == 'admin'



class IsAgent(BasePermission):
    """Tous les rôles authentifiés"""
    def has_permission(self, request, view):
        return get_role(request.user) == 'agent'


    


class IsResponsableDepartement(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'responsable_departement'
        )
     

# permissions.py — ajouter ce qui manque
class IsDirecteurActivite(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'directeur_activite'
        )
class IsDirecteurDirection(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'directeur_direction'
        )