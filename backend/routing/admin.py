from django.contrib import admin
from .models import RoutingResult

@admin.register(RoutingResult)
class RoutingResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'urgency', 'specialty', 'created_at')
    list_filter = ('urgency', 'specialty')