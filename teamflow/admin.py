from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (User,
                     Task,
                     Project)

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (
            ('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ['last_login', 'date_joined']  # Corrigido aqui
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
    )


class ProjectAdmin(admin.ModelAdmin):
    ordering = ['-start_date']
    list_display = ['name', 'created_by', 'start_date', 'due_date', 'get_members']
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Datas', {'fields': ('start_date', 'due_date')}),
        ('Criador', {'fields': ('created_by',)}),
        ('Membros', {'fields': ('members',)}),
    )

    filter_horizontal = ('members',)

    def get_members(self, obj):
        return ", ".join([member.username for member in obj.members.all()])
    get_members.short_description = 'Members'

class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'project_name']

    def project_name(self, obj):
        return obj.project.name
    project_name.admin_order_field = 'project__name'
    project_name.short_description = 'Project Name'

admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Project, ProjectAdmin)