from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='boards', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=50, blank=True)
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')
    reviewer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_tasks')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title