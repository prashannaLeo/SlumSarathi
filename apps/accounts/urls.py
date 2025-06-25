from django.urls import path
from . import views

urlpatterns = [
    # Example:
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('edit/<int:user_id>/', views.edit_profile_view, name='edit_profile'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password_view, name='reset_password'),
    path('verify-email/<uuid:uuid>/', views.verify_email_view, name='verify_email'),
    path('newsletter-signup/', views.newsletter_signup_view, name='newsletter_signup'),
]