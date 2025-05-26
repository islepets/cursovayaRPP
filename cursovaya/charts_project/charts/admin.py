from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Graph


class GraphAdmin(admin.ModelAdmin):
    list_display = ('user', 'x_value', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'x_value')

admin.site.unregister(Group)
admin.site.register(Graph, GraphAdmin)