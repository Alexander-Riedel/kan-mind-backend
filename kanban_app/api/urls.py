from django.urls import path
from .views import BoardListCreateView, BoardDetailView, BoardUpdateView, BoardDeleteView, EmailCheckView, AssignedTasksView, ReviewingTasksView, TaskCreateView, TaskUpdateDeleteView, CommentListView, CommentCreateView, CommentDeleteView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('boards/<int:pk>/', BoardUpdateView.as_view(), name='board-update'),
    path('boards/<int:pk>/', BoardDeleteView.as_view(), name='board-delete'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='reviewing-tasks'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskUpdateDeleteView.as_view(), name='task-update-delete'),
    path('tasks/<int:task_id>/comments/', CommentListView.as_view(), name='comment-list'),
    path('tasks/<int:task_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDeleteView.as_view(), name='comment-delete'),
]