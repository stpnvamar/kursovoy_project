from django.contrib import admin
from .models import Task, TaskCompletion


class TaskCompletionInline(admin.TabularInline):
    model = TaskCompletion
    extra = 0
    readonly_fields = ('completed_at',)
    fields = ('completed_at', 'comment')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'priority', 'deadline', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'owner__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    list_select_related = ('owner',)
    inlines = [TaskCompletionInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основное', {'fields': ('title', 'description', 'owner')}),
        ('Статус и приоритет', {'fields': ('status', 'priority', 'deadline')}),
        ('Служебное', {'fields': ('created_at',)}),
    )


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('task', 'completed_at', 'comment_preview')
    list_filter = ('completed_at',)
    search_fields = ('task__title', 'comment')
    ordering = ('-completed_at',)
    readonly_fields = ('completed_at',)
    list_select_related = ('task',)

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Комментарий'
