from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company_name', 'location', 'job_type',
        'visa_sponsorship', 'remote_type', 'latitude', 'longitude', 'created_at'
    )
    list_filter  = ('job_type', 'visa_sponsorship', 'remote_type', 'location')
    search_fields = ('title', 'skills', 'location', 'company_name')
    
    fields = (
        'title', 'company_name', 'skills', 'location',
        'salary_min', 'salary_max',
        'job_type', 'visa_sponsorship', 'remote_type',
        'latitude', 'longitude'
    )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'applied_at')
    list_filter  = ('status', 'applied_at', 'job')
    search_fields = ('candidate__username', 'job__title')