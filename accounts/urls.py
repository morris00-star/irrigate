from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import regenerate_api_key, confirm_token_regeneration

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/regenerate-key/', regenerate_api_key, name='regenerate_api_key'),
    path('profile/regenerate-key/confirm/', confirm_token_regeneration, name='confirm_token_regeneration'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('default-avatar/', views.default_avatar, name='default_avatar'),
    path('check-profile-picture/', views.check_profile_picture, name='check_profile_picture'),
]

