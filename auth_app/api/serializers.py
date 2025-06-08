from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    # Full name of the user; not used internally by Django's User model, 
    # but can be stored in a custom user model or profile.
    fullname = serializers.CharField()

    # Email address used for login and identification.
    email = serializers.EmailField()

    # Password input; write_only ensures it won't appear in serialized output.
    password = serializers.CharField(write_only=True)

    # Repeated password for confirmation; also write_only.
    repeated_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the input fields for user registration.

        - Ensures that 'password' and 'repeated_password' match.
        - Ensures that the provided email address is not already registered.

        Returns:
            dict: The validated data if all checks pass.

        Raises:
            serializers.ValidationError: If passwords don't match or email is already taken.
        """

        # Check if the entered passwords are identical
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not mtach.")
        
        # Ensure the email address is not already associated with another user
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("This email address is already in use.")

        return data