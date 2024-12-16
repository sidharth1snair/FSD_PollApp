from django.contrib import admin
from .models import Poll, Option

class OptionInline(admin.TabularInline):
    model = Option

class PollAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('question', 'is_active', 'created_at')  # Ensure 'is_active' is a field in Poll
    list_filter = ('is_active',)  # Ensure 'is_active' is a field in Poll

    # Add custom actions to activate/deactivate polls
    actions = ['activate_polls', 'deactivate_polls']

    def activate_polls(self, request, queryset):
        queryset.update(is_active=True)
    activate_polls.short_description = "Activate selected polls"

    def deactivate_polls(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_polls.short_description = "Deactivate selected polls"

admin.site.register(Poll, PollAdmin)
