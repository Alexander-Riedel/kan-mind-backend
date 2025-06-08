from rest_framework import mixins, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from kanban_app.models import Board, Task, Comment
from auth_app.models import UserProfile
from .serializers import BoardSerializer, BoardDetailSerializer, TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer


class BoardListCreateView(generics.ListCreateAPIView):
    """
    - GET /api/boards/: List all boards where the current user is a member or owner.
    - POST /api/boards/: Create a new board. The creator becomes the owner.
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET /api/boards/<id>/: View a specific board (if user is owner or member).
    - PATCH /api/boards/<id>/: Update board (if owner or member).
    - DELETE /api/boards/<id>/: Delete board (only if user is owner).
    """
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return BoardDetailSerializer if self.request.method == 'GET' else BoardSerializer

    def get_object(self):
        board = super().get_object()
        user = self.request.user

        if self.request.method == 'GET' and user != board.owner and user not in board.members.all():
            raise PermissionDenied("You do not have access to view this board.")
        if self.request.method in ['PUT', 'PATCH'] and user != board.owner and user not in board.members.all():
            raise PermissionDenied("You do not have permission to edit this board.")
        if self.request.method == 'DELETE' and user != board.owner:
            raise PermissionDenied("Only the owner can delete this board.")

        return board

    def retrieve(self, request, *args, **kwargs):
        board = self.get_object()
        serializer = self.get_serializer(board)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        board = self.get_object()
        serializer = self.get_serializer(board, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_board = serializer.save()

        return Response({
            "id": updated_board.id,
            "title": updated_board.title,
            "owner_data": {
                "id": updated_board.owner.id,
                "email": updated_board.owner.email,
                "fullname": f"{updated_board.owner.first_name} {updated_board.owner.last_name}".strip()
            },
            "members_data": [
                {
                    "id": m.id,
                    "email": m.email,
                    "fullname": f"{m.first_name} {m.last_name}".strip()
                } for m in updated_board.members.all()
            ]
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        board = self.get_object()
        board.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class EmailCheckView(APIView):
    """
    - GET /api/email-check/?email=...:
      Checks if a user exists for the given email. Returns user data if found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'detail': 'Email address is required.'}, status=400)

        try:
            user = User.objects.get(email=email)
            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.userprofile.fullname if hasattr(user, 'userprofile') else ""
            })
        except User.DoesNotExist:
            return Response({'detail': 'Email not found.'}, status=404)
    

class AssignedTasksView(generics.ListAPIView):
    """
    - GET /api/tasks/assigned-to-me/: Returns tasks assigned to the current user.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTasksView(generics.ListAPIView):
    """
    - GET /api/tasks/reviewing/: Returns tasks where the user is the reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)
    

class TaskCreateView(generics.CreateAPIView):
    """
    - POST /api/tasks/: Creates a new task.
      User must be authenticated and belong to the board.
    """
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        created_task = Task.objects.get(pk=response.data['id'])
        full_data = TaskSerializer(created_task).data
        return Response(full_data, status=status.HTTP_201_CREATED)
    

class TaskUpdateDeleteView(generics.GenericAPIView,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin):
    """
    - PATCH /api/tasks/<id>/: Update task (if board member).
    - DELETE /api/tasks/<id>/: Delete task (if creator or board owner).
    """
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        task = get_object_or_404(Task, pk=self.kwargs['pk'])
        user = self.request.user

        if self.request.method == 'PATCH' and user != task.board.owner and user not in task.board.members.all():
            raise PermissionDenied("You are not allowed to edit this task.")
        if self.request.method == 'DELETE' and user != task.creator and user != task.board.owner:
            raise PermissionDenied("Only the creator or board owner can delete this task.")
        return task

    def get_serializer_context(self):
        return {'request': self.request}

    def patch(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        full_data = TaskSerializer(instance).data
        return Response(full_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    - GET /api/tasks/<task_id>/comments/: List all comments on a task.
    - POST /api/tasks/<task_id>/comments/: Add a new comment to the task.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id).order_by('created_at')

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        serializer.save(author=self.request.user, task=task)


class CommentDeleteView(generics.DestroyAPIView):
    """
    - DELETE /api/tasks/<task_id>/comments/<comment_id>/:
      Only the author of the comment can delete it.
    """
    queryset = Comment.objects.all()

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if comment.author != self.request.user:
            raise PermissionDenied("You may only delete your own comments.")
        return comment