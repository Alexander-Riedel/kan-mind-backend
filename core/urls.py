from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin interface – accessible via /admin/
    path('admin/', admin.site.urls),

    # Authentication-related API endpoints (registration, login, etc.)
    # These are defined in auth_app/api/urls.py
    path('api/', include('auth_app.api.urls')),

    # Kanban board-related API endpoints (boards, tasks, comments, etc.)
    # These are defined in kanban_app/api/urls.py
    path('api/', include('kanban_app.api.urls')),
]
