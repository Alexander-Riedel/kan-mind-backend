from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from auth_app.models import UserProfile
from .serializers import RegistrationSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Load incoming data into the serializer
        serializer = RegistrationSerializer(data=request.data)
        
        # Check if the data is valid (e.g., passwords match, email format correct, etc.)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            fullname = serializer.validated_data['fullname']

            # Create the User object (using email as the username)
            user = User.objects.create_user(username=email, email=email, password=password)

            # Create the related UserProfile with the provided fullname
            UserProfile.objects.create(user=user, fullname=fullname)

            # Return a success response with user info (token will be added later)
            return Response({
                "fullname": fullname,
                "email": email,
                "user_id": user.id,
                # "token": ""
            }, status=status.HTTP_201_CREATED)
        
        # If validation failed, return error messages
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
