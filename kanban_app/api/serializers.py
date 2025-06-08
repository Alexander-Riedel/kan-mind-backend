from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from django.contrib.auth.models import User


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
            'members',
        ]
        extra_kwargs = {
            'members': {'write_only': True}
        }

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board


# Used to represent a user as { id, email, fullname }
class UserSummarySerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# Task output serializer
class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    creator = UserSummarySerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority',
            'assignee', 'reviewer', 'creator',
            'due_date', 'created_at',
            'comments_count'
        ]

    def get_comments_count(self, obj):
        # Will be updated when Comment model is available
        return 0
    

class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority',
            'assignee_id', 'reviewer_id',
            'due_date'
        ]

    def validate(self, data):
        user = self.context['request'].user
        board = data.get('board') or self.instance.board  # 🔧 Fallback bei PATCH

        # Check: is the user a member of the board (or owner)?
        if user != board.owner and user not in board.members.all():
            raise serializers.ValidationError("You must be a member of the board to create a task.")

        # Optional: Check if assignee and reviewer (if given) are also members
        for role_field in ['assignee_id', 'reviewer_id']:
            uid = data.get(role_field)
            if uid:
                try:
                    u = User.objects.get(pk=uid)
                    if u != board.owner and u not in board.members.all():
                        raise serializers.ValidationError(f"{role_field} is not a member of the board.")
                except User.DoesNotExist:
                    raise serializers.ValidationError(f"{role_field} is invalid.")

        return data

    def create(self, validated_data):
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)

        task = Task.objects.create(creator=self.context['request'].user, **validated_data)

        if assignee_id:
            task.assignee = User.objects.get(pk=assignee_id)
        if reviewer_id:
            task.reviewer = User.objects.get(pk=reviewer_id)

        task.save()
        return task
    

class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'assignee_id',
            'reviewer_id'
        ]

    def update(self, instance, validated_data):
        # Diese Felder setzen wir direkt
        for field in ['title', 'description', 'status', 'priority', 'due_date']:
            if field not in validated_data:
                validated_data[field] = getattr(instance, field)

        # Sonderfall: assignee_id & reviewer_id
        assignee_id = validated_data.get('assignee_id', serializers.empty)
        if assignee_id is serializers.empty:
            validated_data['assignee_id'] = instance.assignee.id if instance.assignee else None

        reviewer_id = validated_data.get('reviewer_id', serializers.empty)
        if reviewer_id is serializers.empty:
            validated_data['reviewer_id'] = instance.reviewer.id if instance.reviewer else None

        # assignee aktualisieren
        if 'assignee_id' in validated_data:
            assignee_id = validated_data.pop('assignee_id')
            instance.assignee = User.objects.get(pk=assignee_id) if assignee_id else None

        # reviewer aktualisieren
        if 'reviewer_id' in validated_data:
            reviewer_id = validated_data.pop('reviewer_id')
            instance.reviewer = User.objects.get(pk=reviewer_id) if reviewer_id else None

        # übrige Felder setzen
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip()
    

class BoardDetailSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserSummarySerializer(many=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks'
        ]