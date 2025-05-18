from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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