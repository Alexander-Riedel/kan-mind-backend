from django.urls import path
from .views import (
    BoardListCreateView,
    BoardRetrieveUpdateDeleteView,
    EmailCheckView,
    AssignedTasksView,
    ReviewingTasksView,
    TaskCreateView,
    TaskUpdateDeleteView,
    CommentListCreateView,
    CommentDeleteView
)

# URL patterns for Kanban-related API endpoints
urlpatterns = [
    # GET: List all boards the user is a member of
    # POST: Create a new board
    # Endpoint: /api/boards/
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),

    # GET: Retrieve a specific board by ID
    # PATCH: Update a board
    # DELETE: Delete a board
    # Endpoint: /api/boards/<id>/
    path('boards/<int:pk>/', BoardRetrieveUpdateDeleteView.as_view(), name='board-rud'),

    # GET: Check if an email belongs to a registered user (used for inviting team members, etc.)
    # Endpoint: /api/email-check/
    path('email-check/', EmailCheckView.as_view(), name='email-check'),

    # GET: Get tasks assigned to the current user
    # Endpoint: /api/tasks/assigned-to-me/
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(), name='assigned-tasks'),

    # GET: Get tasks the user is reviewing
    # Endpoint: /api/tasks/reviewing/
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='reviewing-tasks'),

    # POST: Create a new task
    # Endpoint: /api/tasks/
    path('tasks/', TaskCreateView.as_view(), name='task-create'),

    # PATCH: Update an existing task
    # DELETE: Delete a task
    # Endpoint: /api/tasks/<id>/
    path('tasks/<int:pk>/', TaskUpdateDeleteView.as_view(), name='task-update-delete'),

    # GET: List all comments for a task
    # POST: Add a new comment to a task
    # Endpoint: /api/tasks/<task_id>/comments/
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),

    # DELETE: Remove a specific comment from a task
    # Endpoint: /api/tasks/<task_id>/comments/<comment_id>/
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDeleteView.as_view(), name='comment-delete'),
]
