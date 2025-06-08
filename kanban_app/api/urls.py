from django.urls import path
from .views import BoardListCreateView, BoardRetrieveUpdateDeleteView, EmailCheckView, AssignedTasksView, ReviewingTasksView, TaskCreateView, TaskUpdateDeleteView, CommentListCreateView, CommentDeleteView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardRetrieveUpdateDeleteView.as_view(), name='board-rud'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='reviewing-tasks'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskUpdateDeleteView.as_view(), name='task-update-delete'),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDeleteView.as_view(), name='comment-delete'),
]