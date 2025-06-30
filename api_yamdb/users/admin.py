from django.contrib import admin

from .models import YamdbUserInterface


@admin.register(YamdbUserInterface)
class YamdbUserInterfaceAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role',)
    fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role',)
    search_fields = ('username',)
