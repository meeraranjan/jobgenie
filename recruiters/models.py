from django.db import models
from django.contrib.auth.models import User

class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="recruiter_profile")
    company_name = models.CharField(max_length=255, default="Unknown Company")
    position = models.CharField(max_length=255, blank=True, null=True)

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    is_public = models.BooleanField(default=False, help_text="Allow job seekers/recruiters to view your profile and contact details")

    def __str__(self):
        return f"{self.user.username} ({self.company_name})"


class SavedCandidateSearch(models.Model):
    recruiter = models.ForeignKey(
        Recruiter,
        on_delete=models.CASCADE,
        related_name="saved_searches",
    )
    name = models.CharField(max_length=100)
    query_string = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_run_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.recruiter.user.username})"