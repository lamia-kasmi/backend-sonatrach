
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
    
]