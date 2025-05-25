from rest_framework import mixins, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from kanban_app.models import Board, Task
from .serializers import BoardSerializer, TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer
from django.db import models
from django.contrib.auth.models import User

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


# This view handles:
# - GET /api/boards/ to list all boards for the current user
# - POST /api/boards/ to create a new board
class BoardListCreateView(generics.ListCreateAPIView):
    # Use the BoardSerializer for both input and output
    serializer_class = BoardSerializer

    # Only authenticated users can access this endpoint
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the currently authenticated user making the request
        user = self.request.user
        
        # Return all boards where the user is either:
        # - the owner of the board (creator)
        # - OR listed as a member of the board
        # Use Q objects to allow OR logic in the query
        # Use .distinct() to avoid duplicate entries if the user is both owner and member
        return Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        # Automatically assign the currently logged-in user as the board owner
        # when creating a new board
        serializer.save(owner=self.request.user)


# This view handles:
# - GET /api/boards/{board_id}/ to retrieve the details of a specific board
# 
# Requirements:
# - The user must be authenticated
# - The user must either be:
#   - the owner (creator) of the board
#   - OR a member of the board
# 
# Response includes:
# - The board’s ID, title, owner ID, and list of member user IDs
# - Additional fields like member_count, ticket_count (placeholder), etc.
class BoardDetailView(generics.RetrieveAPIView):
    # This view retrieves one specific Board object based on the ID (pk) from the URL
    queryset = Board.objects.all()

    # Use the existing BoardSerializer for serializing the output
    serializer_class = BoardSerializer

    # Only authenticated users can access this endpoint
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        # Call the superclass method to get the Board object using the URL parameter 'pk'
        board = super().get_object()

        # Get the currently authenticated user
        user = self.request.user

        # Check if the user has permission to access this board
        # A user can access the board if they are either:
        # - the owner of the board
        # - OR listed as a member of the board
        if board.owner != user and user not in board.members.all():
            # If the user is neither the owner nor a member, deny access
            raise PermissionDenied("Du darfst dieses Board nicht sehen.")

        # Return the board object if access is allowed
        return board
    

class BoardUpdateView(generics.UpdateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    # permission_classes = [IsAuthenticated]

    def get_object(self):
        board = super().get_object()
        user = self.request.user

        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("Du darfst dieses Board nicht bearbeiten.")
        return board

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        board = self.get_object()
        serializer = self.get_serializer(board, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Speichern
        updated_board = serializer.save()

        # Ausgabe wie in Success-Response
        response_data = {
            'id': updated_board.id,
            'title': updated_board.title,
            'owner_data': {
                'id': updated_board.owner.id,
                'email': updated_board.owner.email,
                'fullname': f"{updated_board.owner.first_name} {updated_board.owner.last_name}".strip()
            },
            'members_data': [
                {
                    'id': m.id,
                    'email': m.email,
                    'fullname': f"{m.first_name} {m.last_name}".strip()
                } for m in updated_board.members.all()
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class BoardDeleteView(generics.DestroyAPIView):
    queryset = Board.objects.all()

    # permission_classes = [IsAuthenticated]

    def get_object(self):
        board = super().get_object()
        user = self.request.user

        if board.owner != user:
            raise PermissionDenied("Nur der Besitzer darf dieses Board löschen.")
        return board

    def delete(self, request, *args, **kwargs):
        board = self.get_object()
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class EmailCheckView(APIView):
    # permission_classes = [IsAuthenticated]  # aktuell offen

    def get(self, request):
        email = request.query_params.get('email')
        if email is None:
            return Response({'detail': 'E-Mail-Adresse muss angegeben werden.'}, status=400)

        exists = User.objects.filter(email=email).exists()
        return Response({'exists': exists})
    

# This view handles:
# - GET /api/tasks/assigned-to-me/
# 
# Returns all tasks where the currently authenticated user is the assignee.
# The user must be logged in (IsAuthenticated).
class AssignedTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer

    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the current user
        user = self.request.user

        # Return all tasks where the user is assigned
        return Task.objects.filter(assignee=user)
    

# This view handles:
# - GET /api/tasks/reviewing/
#
# Returns all tasks where the current user is the reviewer.
# Requires authentication (IsAuthenticated).
class ReviewingTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer

    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user)
    

# This view handles:
# - POST /api/tasks/
#
# It creates a new task on a board.
# The user must be authenticated AND a member of the board.
class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskCreateSerializer

    # permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Needed so the serializer can access request.user in `validate`
        return {'request': self.request}

    def perform_create(self, serializer):
        # Let the serializer handle validation and saving
        serializer.save()

    def create(self, request, *args, **kwargs):
        # Standard CreateAPIView behavior, but return full TaskSerializer after creation
        response = super().create(request, *args, **kwargs)
        created_task = Task.objects.get(pk=response.data['id'])
        full_data = TaskSerializer(created_task).data
        return Response(full_data, status=status.HTTP_201_CREATED)
    

class TaskUpdateDeleteView(generics.GenericAPIView,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin):
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    # permission_classes = [IsAuthenticated]

    def get_object(self):
        task = get_object_or_404(Task, pk=self.kwargs['pk'])
        user = self.request.user
        if self.request.method == 'PATCH':
            if user != task.board.owner and user not in task.board.members.all():
                raise PermissionDenied("Du darfst diese Aufgabe nicht bearbeiten.")
        elif self.request.method == 'DELETE':
            if user != task.creator and user != task.board.owner:
                raise PermissionDenied("Du darfst diese Aufgabe nicht löschen.")
        return task

    def get_serializer_context(self):
        return {'request': self.request}

    def patch(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        full_data = TaskSerializer(self.get_object()).data
        return Response(full_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

from kanban_app.models import Comment

# GET /api/tasks/{task_id}/comments/
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id).order_by('created_at')


# POST /api/tasks/{task_id}/comments/
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        serializer.save(author=self.request.user, task=task)


# DELETE /api/tasks/{task_id}/comments/{comment_id}/
class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if comment.author != self.request.user:
            raise PermissionDenied("Du darfst nur deine eigenen Kommentare löschen.")
        return comment