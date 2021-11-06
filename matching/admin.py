from django.contrib import admin
from .models import MatchingInfo, MatchingResult

class MatchingInfoAdmin(admin.ModelAdmin):
    search_fields = ['id']

class MatchingResultAdmin(admin.ModelAdmin):
    search_fields = ['uid']

admin.site.register(MatchingInfo, MatchingInfoAdmin)
admin.site.register(MatchingResult, MatchingInfoAdmin)
