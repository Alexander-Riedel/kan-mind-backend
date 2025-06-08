from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from auth_app.models import UserProfile
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Load incoming data into the serializer
        serializer = RegistrationSerializer(data=request.data)

        # Check if the data is valid
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            fullname = serializer.validated_data['fullname']

            # Create the User object (using email as the username)
            user = User.objects.create_user(
                username=email, email=email, password=password)

            # Create the related UserProfile with the provided fullname
            UserProfile.objects.create(user=user, fullname=fullname)

            # Create the auth token after the user has been created
            token = Token.objects.create(user=user)

            # Return a success response with user info
            return Response({
                "fullname": fullname,
                "email": email,
                "user_id": user.id,
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        # If validation failed, return error message
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # 🔍 Falls Gastlogin + Benutzer existiert nicht → anlegen
        if email == "kevin@kovacsi.de" and password == "asdasdasd":
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=email,
                    email=email,
                    password=make_password(password)
                )
                UserProfile.objects.create(user=user, fullname="Guest User")

        # Because we stored email as the username:
        user = authenticate(username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        profile = UserProfile.objects.get(user=user)

        return Response({
            'token': token.key,
            'fullname': profile.fullname,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_200_OK)
