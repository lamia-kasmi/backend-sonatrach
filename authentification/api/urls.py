
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Auth / Users
    path('login/', views.api_login, name='api_login'),
    path('logout/', views.api_logout, name='api_logout'),
    path('me/', views.api_me, name='api_me'),
    
    # User password management
    path('password/change/', views.api_change_password, name='api_change_password'),
    path('reset-password/', views.api_reset_password, name='reset-password'),
    path('reset-password-confirm/', views.api_reset_password_confirm, name='reset-password-confirm'),

    
    path('users/create/', views.api_create_user, name='api_create_user'),
    path('users/<int:user_id>/', views.api_get_user, name='api_get_user'),
    path('users/<int:user_id>/desactive-user/', views.api_toggle_user_active, name='toggle_user_active'),
    path('users/', views.api_list_users, name='api_list_users'),  
    path('all_users/', views.api_list_all_users, name='api_list_all_users'),
    path('all_users/public/', views.api_list_all_users_public, name='api_users_public'),
    path('all_users/<int:user_id>/', views.api_get_user_by_id, name='api_get_user_by_id'),     
    path('users/<int:user_id>/', views.api_get_user, name='api_get_user'), 
    path('users/<int:user_id>/update/', views.api_update_user, name='api_update_user'),
    path('users/<int:user_id>/update-role/', views.api_update_user_role, name='api_update_user_role'),
    path('users/<int:user_id>/delete/', views.api_delete_user, name='api_delete_user'), 
    path('users/<int:user_id>/update-departement/', views.api_update_user_departement, name='api_update_user_departement'), 

]