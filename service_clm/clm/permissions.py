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
class IsVicePresedent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'vice_presedent'
        )
class IsDirecteurDirection(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'directeur_direction'
        )
class IsDirecteurCentrale(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_role(request.user) == 'directeur_centrale'
        )


class IsAssistantDirecteurCentrale(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_role(request.user) == 'assistant_directeur_centrale'
        )


class IsDirecteurDirectionActivite(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_role(request.user) == 'directeur_direction_activite'
        )


class IsDirecteurDivisionActivite(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_role(request.user) == 'directeur_division_activite'
        )


class IsResponsableDirectionDivision(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_role(request.user) == 'responsable_direction_division'
        )


class IsResponsableDepartementDivision(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and get_role(request.user) == 'responsable_departement_division'
        )