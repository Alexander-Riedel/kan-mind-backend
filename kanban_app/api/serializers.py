from rest_framework import serializers
from kanban_app.models import Board #, Task
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
        return 0  # to be replaced once Task model is ready

    def get_tasks_to_do_count(self, obj):
        return 0  # placeholder

    def get_tasks_high_prio_count(self, obj):
        return 0  # placeholder

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board
