from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import JobSeekerProfile
# Register your models here.

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'is_public')
    search_fields = ('user__username', 'headline', 'skills')
    list_filter = ('is_public',)
    actions = ['export_profiles_to_csv'] 

    @admin.action(description="Export selected job seeker profiles to CSV")
    def export_profiles_to_csv(self, request, queryset):
        """Export selected job seeker profiles as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="jobseeker_profiles.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Full Name', 'Headline', 'Skills',
            'Education', 'Work Experience', 'Links', 'Public', 'Created At'
        ])

        for p in queryset.select_related('user'):
            writer.writerow([
                p.user.username,
                f"{p.user.first_name} {p.user.last_name}".strip(),
                p.headline,
                p.skills,
                p.education,
                p.work_experience,
                p.links,
                "Public" if p.is_public else "Private",
                p.created_at.strftime("%Y-%m-%d") if hasattr(p, "created_at") else "",
            ])

        return response