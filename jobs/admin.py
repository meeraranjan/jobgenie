from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'job_type', 'visa_sponsorship', 'created_at')
    list_filter  = ('job_type', 'visa_sponsorship', 'location')
    search_fields = ('title', 'skills', 'location')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'applied_at')
    list_filter  = ('status', 'applied_at', 'job')
    search_fields = ('candidate__username', 'job__title')