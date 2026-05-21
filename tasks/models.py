from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Активная'
        COMPLETED = 'completed', 'Выполнена'
        OVERDUE = 'overdue', 'Просрочена'

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Владелец'
    )
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Дедлайн')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус'
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name='Приоритет'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return f'{self.title} ({self.owner.email})'

    def update_overdue_status(self):
        if (
            self.status == self.Status.PENDING
            and self.deadline
            and self.deadline < timezone.now()
        ):
            self.status = self.Status.OVERDUE
            self.save(update_fields=['status'])

    @property
    def is_overdue(self):
        return (
            self.deadline is not None
            and self.deadline < timezone.now()
            and self.status != self.Status.COMPLETED
        )


class TaskCompletion(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='completions',
        verbose_name='Задача'
    )
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отметки')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Отметка выполнения'
        verbose_name_plural = 'Отметки выполнения'
        ordering = ['-completed_at']

    def __str__(self):
        return f'Выполнение задачи "{self.task.title}" — {self.completed_at.strftime("%d.%m.%Y %H:%M")}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.task.status = Task.Status.COMPLETED
        self.task.save(update_fields=['status'])
