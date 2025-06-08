from django.urls import path
from .views import LoginView, RegistrationView

# URL patterns for authentication-related endpoints
urlpatterns = [
    # Handles user registration (POST)
    # Endpoint: /api/registration/
    path('registration/', RegistrationView.as_view(), name='registration'),

    # Handles user login/authentication (POST)
    # Endpoint: /api/login/
    path('login/', LoginView.as_view(), name='login'),
]