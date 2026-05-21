from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Task, TaskCompletion
from .serializers import (
    TaskSerializer, TaskListSerializer,
    TaskCompletionSerializer, StatisticsSerializer
)
from .permissions import IsOwnerOrAdmin


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.select_related('owner').prefetch_related('completions').all()
        return Task.objects.select_related('owner').prefetch_related('completions').filter(
            owner=user
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        queryset = Task.objects.filter(owner=request.user)
        now = timezone.now()

        queryset.filter(
            status=Task.Status.PENDING,
            deadline__lt=now
        ).update(status=Task.Status.OVERDUE)

        aggregated = queryset.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status=Task.Status.COMPLETED)),
            overdue=Count('id', filter=Q(status=Task.Status.OVERDUE)),
            pending=Count('id', filter=Q(status=Task.Status.PENDING)),
        )
        total = aggregated['total'] or 0
        completed = aggregated['completed'] or 0
        completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

        data = {
            'total': total,
            'completed': completed,
            'overdue': aggregated['overdue'] or 0,
            'pending': aggregated['pending'] or 0,
            'completion_rate': completion_rate,
        }
        serializer = StatisticsSerializer(data)
        return Response(serializer.data)


class CompletionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)
    serializer_class = TaskCompletionSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        user = self.request.user
        if user.is_staff:
            return TaskCompletion.objects.filter(task_id=task_id).select_related('task')
        return TaskCompletion.objects.filter(
            task_id=task_id,
            task__owner=user
        ).select_related('task')

    def get_task(self):
        task_id = self.kwargs.get('task_pk')
        user = self.request.user
        if user.is_staff:
            return Task.objects.get(pk=task_id)
        return Task.objects.get(pk=task_id, owner=user)

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(task=task)
