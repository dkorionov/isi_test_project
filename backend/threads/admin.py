from django.contrib import admin

from threads.models import Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('creator__username',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_select_related = ('participants',)
