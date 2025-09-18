from django.contrib.auth.models import User
from django.db import models

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    skills = models.TextField()
    education = models.TextField()
    work_experience = models.TextField()
    links = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)  # privacy

    def __str__(self):
        return f"{self.user.username} - {self.headline}"

