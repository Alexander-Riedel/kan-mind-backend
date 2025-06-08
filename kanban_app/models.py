from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    """
    Represents a Kanban board that groups tasks and users.

    - `title`: The name of the board.
    - `owner`: The user who created the board and has full permissions.
    - `members`: Other users who are allowed to view/edit tasks on the board.
    - `created_at`: Timestamp of when the board was created.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards'  # Access via user.owned_boards.all()
    )
    members = models.ManyToManyField(
        User,
        related_name='boards',  # Access via user.boards.all()
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Task(models.Model):
    """
    Represents a task (or ticket) within a board.

    - `board`: The board to which this task belongs.
    - `title`: Short title or label for the task.
    - `description`: Optional detailed description.
    - `status`: Current status (e.g. to-do, in-progress, done).
    - `priority`: Priority level (e.g. low, medium, high).
    - `assignee`: User responsible for completing the task.
    - `reviewer`: User responsible for reviewing the task.
    - `due_date`: Optional deadline.
    - `creator`: The user who created the task.
    - `created_at`: Timestamp when the task was created.
    """
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks'  # Access via board.tasks.all()
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=50, blank=True)

    assignee = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks'
    )
    reviewer = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_tasks'
    )

    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        null=True, blank=True
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Represents a comment on a task.

    - `task`: The task this comment belongs to.
    - `author`: The user who wrote the comment.
    - `content`: The actual text content of the comment.
    - `created_at`: Timestamp when the comment was created.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'  # Access via task.comments.all()
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on Task {self.task_id}"
