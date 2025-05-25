from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from .models import Graph

class GraphAdmin(admin.ModelAdmin):
    list_display = ('user', 'x_value', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'x_value')
    readonly_fields = ('created_at',)

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms['group'] = 'Графы'  # Название группы в единственном числе
        return perms

class CustomUserAdmin(UserAdmin):
    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms['group'] = 'Пользователи'
        return perms

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Graph, GraphAdmin)


admin.site.unregister(Group)
admin.site.register(Group)