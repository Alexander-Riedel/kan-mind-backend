from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    fullname = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not mtach.")
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("This email address is already in use.")

        return data