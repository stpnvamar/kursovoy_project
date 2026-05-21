from rest_framework import serializers
from .models import Task, TaskCompletion


class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCompletion
        fields = ('id', 'task', 'completed_at', 'comment')
        read_only_fields = ('id', 'completed_at', 'task')


class TaskSerializer(serializers.ModelSerializer):
    completions = TaskCompletionSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'created_at', 'deadline',
            'status', 'priority', 'owner_email', 'is_overdue', 'completions'
        )
        read_only_fields = ('id', 'created_at', 'owner_email')

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'deadline', 'status', 'priority', 'is_overdue', 'created_at')
        read_only_fields = ('id', 'created_at')


class StatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    overdue = serializers.IntegerField()
    pending = serializers.IntegerField()
    completion_rate = serializers.FloatField()
