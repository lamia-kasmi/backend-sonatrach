
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # POST /affectation/assign/
    path('assign-role/', views.assign_role, name='affectation-assign'),

    #Activite
    path('assign-activite/', views.assign_activite_to_user, name='assign_activite'),
    path('reassign-activite/', views.reassign_activite_to_user, name='reassign_activite'),
    path('users/<int:user_id>/remove-activite/', views.remove_activite_from_user, name='remove_activite'),
    path('users/directeurs-activite/non-affectes/', views.api_list_directeurs_activite, name='list-directeurs-activite'),
    path('users/directeurs-activite/affectes/', views.api_list_directeurs_activite_affectes, name='list-directeurs-activite-affectes'),
    path('users/directeurs-activite/all/', views.api_list_all_directeurs_activite, name='list-all-directeurs-activite'),
    
    # Direction
    path('assign-direction/', views.assign_direction_to_user, name='assign_direction'),
    path('reassign-direction/', views.reassign_direction_to_user, name='reassign_direction'),
    path('users/<int:user_id>/remove-direction/', views.remove_direction_from_user, name='remove_direction'),
    path('users/directeurs-direction/', views.api_list_directeurs_direction, name='list-directeurs-direction'),
    path('users/directeurs-direction/affectes/', views.api_list_directeurs_direction_affectes, name='list-directeurs-direction-affectes'),
    path('users/directeurs-direction/all/', views.api_list_all_directeurs_direction, name='list-all-directeurs-direction'),


    #Departement
    path('assign-departement/', views.assign_departement_to_user, name='assign_departement'),
    path('reassign-departement/', views.reassign_departement_to_user, name='reassign_departement'),
    path('users/<int:user_id>/remove-departement/', views.remove_departement_from_user, name='remove_departement'),
    path('users/responsables-departement/', views.api_list_responsables_departement, name='list-responsables-departement'),
    path('users/responsables-departement/affectes/', views.api_list_responsables_departement_affectes, name='list-responsables-departement-affectes'),
    path('users/responsables-departement/all/', views.api_list_all_responsables_departement, name='list-all-responsables-departement'),
    

    # Direction Centrale
    path('assign-direction-centrale/', views.assign_direction_centrale_to_user, name='assign-direction-centrale'),
    path('reassign-direction-centrale/', views.reassign_direction_centrale_to_user, name='reassign-direction-centrale'),
    path('users/<int:user_id>/remove-direction-centrale/', views.remove_direction_centrale_from_user, name='remove-direction-centrale'),
    path('users/directeurs-centrale/', views.api_list_directeurs_centrale, name='list-directeurs-centrale'),
    path('users/directeurs-centrale/affectes/', views.api_list_directeurs_centrale_affectes, name='list-directeurs-centrale-affectes'),
    path('users/directeurs-centrale/all/', views.api_list_all_directeurs_centrale, name='list-all-directeurs-centrale'),

    # =========================================================
    # DIRECTION ACTIVITE
    # =========================================================

    path('assign-direction-activite/',views.assign_direction_activite_to_user,name='assign_direction_activite'),

    path('reassign-direction-activite/',views.reassign_direction_activite_to_user,name='reassign_direction_activite'),

    path('users/<int:user_id>/remove-direction-activite/',views.remove_direction_activite_from_user,name='remove_direction_activite'),

    path('users/directeurs-direction-activite/',views.api_list_directeurs_direction_activite,name='list-directeurs-direction-activite'),

    path('users/directeurs-direction-activite/affectes/',views.api_list_directeurs_direction_activite_affectes,name='list-directeurs-direction-activite-affectes'),

    path('users/directeurs-direction-activite/all/',views.api_list_all_directeurs_direction_activite,name='list-all-directeurs-direction-activite'),


    # =========================================================
    # DIVISION ACTIVITE
    # =========================================================

    path('assign-division-activite/',views.assign_division_activite_to_user,name='assign_division_activite'),

    path('reassign-division-activite/',views.reassign_division_activite_to_user,name='reassign_division_activite'),
    path('users/<int:user_id>/remove-division-activite/',views.remove_division_activite_from_user,name='remove_division_activite'),
    path('users/directeurs-division-activite/',views.api_list_directeurs_division_activite,name='list-directeurs-division-activite'),
    path('users/directeurs-division-activite/affectes/',views.api_list_directeurs_division_activite_affectes,name='list-directeurs-division-activite-affectes'),
    path('users/directeurs-division-activite/all/',views.api_list_all_directeurs_division_activite,name='list-all-directeurs-division-activite'),

    # ── STRUCTURE DIRECTION (responsable_direction_division) ──
    path('assign-structure-direction/',   views.assign_structure_direction_to_user,   name='assign-structure-direction'),
    path('reassign-structure-direction/', views.reassign_structure_direction_to_user, name='reassign-structure-direction'),
    path('users/<int:user_id>/remove-structure-direction/', views.remove_structure_direction_from_user, name='remove-structure-direction'),
    path('users/responsables-direction-division/',          views.api_list_responsables_direction_division,          name='list-responsables-direction-division'),
    path('users/responsables-direction-division/affectes/', views.api_list_responsables_direction_division_affectes, name='list-responsables-direction-division-affectes'),
    path('users/responsables-direction-division/all/',      views.api_list_all_responsables_direction_division,      name='list-all-responsables-direction-division'),

    # ── STRUCTURE DEPARTEMENT (responsable_departement_division) ──
    path('assign-structure-departement/',   views.assign_structure_departement_to_user,   name='assign-structure-departement'),
    path('reassign-structure-departement/', views.reassign_structure_departement_to_user, name='reassign-structure-departement'),
    path('users/<int:user_id>/remove-structure-departement/', views.remove_structure_departement_from_user, name='remove-structure-departement'),
    path('users/responsables-departement-division/',          views.api_list_responsables_departement_division,          name='list-responsables-departement-division'),
    path('users/responsables-departement-division/affectes/', views.api_list_responsables_departement_division_affectes, name='list-responsables-departement-division-affectes'),
    path('users/responsables-departement-division/all/',      views.api_list_all_responsables_departement_division,      name='list-all-responsables-departement-division'),

    # ── GET par champ organisationnel ─────────────────────────────────────────────
    path('directions/<str:direction_id>/responsables-departement/',
        views.api_list_responsables_by_direction,
        name='responsables-by-direction'),

    path('departements/<str:departement_id>/responsables-departement/',
        views.api_list_responsables_by_departement,
        name='responsables-by-departement'),

    path('activites/<str:activite_id>/directeurs-direction/',
        views.api_list_directeurs_direction_by_activite,
        name='directeurs-direction-by-activite'),

    path('activites/<str:activite_id>/vice-presidents/',
        views.api_list_vice_presidents_by_activite,
        name='vice-presidents-by-activite'),

    path('activites/<str:activite_id>/directeurs-direction-activite/',
        views.api_list_directeurs_direction_activite_by_activite,
        name='directeurs-direction-activite-by-activite'),

    path('directions-centrales/<str:direction_centrale_id>/directeurs-centrale/',
        views.api_list_directeurs_centrale_by_direction_centrale,
        name='directeurs-centrale-by-direction-centrale'),

    path('directions-centrales/<str:direction_centrale_id>/assistants/',
        views.api_list_assistants_by_direction_centrale,
        name='assistants-by-direction-centrale'),

    path('structures/<str:structure_id>/directeurs-division-activite/',
        views.api_list_directeurs_division_activite_by_structure,
        name='directeurs-division-activite-by-structure'),

    path('structures/<str:structure_id>/responsables-direction-division/',
        views.api_list_responsables_direction_division_by_structure,
        name='responsables-direction-division-by-structure'),

    path('structures/<str:structure_id>/responsables-departement-division/',
        views.api_list_responsables_departement_division_by_structure,
        name='responsables-departement-division-by-structure'),




    ]