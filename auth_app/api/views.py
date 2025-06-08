from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from auth_app.models import UserProfile
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    # This endpoint is publicly accessible – no authentication required
    permission_classes = [AllowAny]

    def post(self, request):
        # Load request data into serializer for validation
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # Extract validated fields
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            fullname = serializer.validated_data['fullname']

            # Create a new User object using email as username
            user = User.objects.create_user(
                username=email, email=email, password=password)

            # Create a related UserProfile to store additional info (fullname)
            UserProfile.objects.create(user=user, fullname=fullname)

            # Create an authentication token for the newly registered user
            token = Token.objects.create(user=user)

            # Return token and user info
            return Response({
                "fullname": fullname,
                "email": email,
                "user_id": user.id,
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        # If validation failed, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    # Publicly accessible – no authentication required
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract credentials from request data
        email = request.data.get('email')
        password = request.data.get('password')

        # Special guest login: If credentials match predefined values,
        # and the user doesn't exist, create a guest account on the fly
        if email == "kevin@kovacsi.de" and password == "asdasdasd":
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                # Create guest user with hashed password
                user = User.objects.create(
                    username=email,
                    email=email,
                    password=make_password(password)
                )
                # Set a default fullname for the guest user
                UserProfile.objects.create(user=user, fullname="Guest User")

        # Authenticate user using email as username
        user = authenticate(username=email, password=password)

        if not user:
            # Authentication failed
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve or create an auth token for the authenticated user
        token, _ = Token.objects.get_or_create(user=user)

        # Fetch user's profile for fullname
        profile = UserProfile.objects.get(user=user)

        # Return token and user info
        return Response({
            'token': token.key,
            'fullname': profile.fullname,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_200_OK)
