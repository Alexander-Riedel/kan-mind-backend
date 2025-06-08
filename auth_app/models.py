from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """
    Extends the default Django User model with additional user-related information.
    
    This model uses a one-to-one relationship to associate extra fields (e.g., fullname)
    with each user in the system.
    """

    # Links this profile to a single User instance.
    # If the user is deleted, the associated UserProfile will also be deleted.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Stores the user's full name; required field (not blank or null)
    fullname = models.TextField(blank=False, null=False)

    def __str__(self):
        # Returns the associated user's username when this object is printed
        return self.user.username
