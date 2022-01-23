from django.contrib import admin
from .models import User

EMPTY_VALUE = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'role')
    search_fields = ('username',)
    list_filter = ('email', 'username',)
    empty_value_display = EMPTY_VALUE
