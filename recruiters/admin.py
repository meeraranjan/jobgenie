from django.contrib import admin
from .models import Recruiter

@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')  # adjust fields as needed
    search_fields = ('user__username', 'company_name')

# Register your models here.
