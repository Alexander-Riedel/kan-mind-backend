from django.urls import path
from .views import BoardListCreateView, BoardDetailView, AssignedTasksView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='assigned-tasks'),
]