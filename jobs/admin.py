from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'job_type', 'visa_sponsorship', 'created_at')
    list_filter  = ('job_type', 'visa_sponsorship', 'location')
    search_fields = ('title', 'skills', 'location')

