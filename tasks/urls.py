from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CompletionViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'tasks/<int:task_pk>/completions/',
        CompletionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='task-completions-list'
    ),
    path(
        'tasks/<int:task_pk>/completions/<int:pk>/',
        CompletionViewSet.as_view({'get': 'retrieve'}),
        name='task-completions-detail'
    ),
]
