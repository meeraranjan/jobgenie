from django.db import models
from django.contrib.auth.models import User

class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="recruiter_profile")
    company_name = models.CharField(max_length=255, default="Unknown Company")
    position = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.company_name})"

