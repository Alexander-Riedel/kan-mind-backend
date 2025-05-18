from rest_framework import generics, permissions
from kanban_app.models import Board
from .serializers import BoardSerializer
from django.db import models


# This view handles:
# - GET /api/boards/ to list all boards for the current user
# - POST /api/boards/ to create a new board
class BoardListCreateView(generics.ListCreateAPIView):
    # Use the BoardSerializer for both input and output
    serializer_class = BoardSerializer

    # Only authenticated users can access this endpoint
    permission_classes = [permissions.IsAuthenticated]

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
