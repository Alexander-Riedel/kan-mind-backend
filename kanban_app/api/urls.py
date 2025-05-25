from django.urls import path
from .views import BoardListCreateView, BoardDetailView, AssignedTasksView, ReviewingTasksView, TaskCreateView, TaskUpdateDeleteView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='reviewing-tasks'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskUpdateDeleteView.as_view(), name='task-update-delete'),
]