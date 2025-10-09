from django.contrib import admin
from django.http import HttpResponse
from .models import Job, Application
import csv


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'recruiter', 'location', 'job_type', 'visa_sponsorship', 'created_at')
    list_filter  = ('job_type', 'visa_sponsorship', 'location')
    search_fields = ('title', 'skills', 'location', 'recruiter_company')
    actions = ['export_jobs_to_csv']

    @admin.action(description="Export selected jobs to CSV")
    def export_jobs_to_csv(self, request, queryset):
        """Admin action to export selected Job records as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="jobs_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Title', 'Recruiter', 'Company', 'Location', 'Job Type',
            'Visa Sponsorship', 'Remote Type', 'Salary Min', 'Salary Max', 'Created At'
        ])

        for job in queryset:
            writer.writerow([
                job.title,
                getattr(job.recruiter, 'user', None),  
                getattr(job, 'company_name', ''),      
                job.location,
                job.job_type,
                job.visa_sponsorship,
                getattr(job, 'remote_type', ''),
                job.salary_min,
                job.salary_max,
                job.created_at.strftime("%Y-%m-%d"),
            ])
        return response

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'applied_at')
    list_filter  = ('status', 'applied_at', 'job')
    search_fields = ('candidate__username', 'job__title')
    actions = ['export_applications_to_csv'] 

    @admin.action(description="Export selected applications to CSV")
    def export_applications_to_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Job Title', 'Candidate', 'Status', 'Applied At'])
        for app in queryset.select_related('job', 'candidate'):
            writer.writerow([
                app.job.title,
                app.candidate.username,
                app.status,
                app.applied_at.strftime("%Y-%m-%d"),
            ])
        return response


