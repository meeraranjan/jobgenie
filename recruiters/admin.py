from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Recruiter


@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')
    search_fields = ('user__username', 'company_name')
    actions = ['export_recruiters_to_csv']


    @admin.action(description="Export selected recruiters to CSV")
    def export_recruiters_to_csv(self, request, queryset):
        """Export selected recruiter data as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="recruiters.csv"'

        writer = csv.writer(response)
        writer.writerow(['Username', 'Company Name', 'Company Website', 'Contact Email'])

        for r in queryset.select_related('user'):
            writer.writerow([
                r.user.username,
                r.company_name,
                getattr(r, 'company_website', ''),
                getattr(r.user, 'email', ''),
            ])

        return response
