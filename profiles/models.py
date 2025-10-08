from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

               
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('JOB_SEEKER', 'Job Seeker'),
        ('RECRUITER', 'Recruiter'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class JobSeekerProfile(models.Model):
    first_name = models.CharField(max_length=255, default='Unknown')
    last_name = models.CharField(max_length=255, default='Unknown')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    skills = models.TextField()
    education = models.TextField()
    work_experience = models.TextField()
    links = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)  # privacy

    def __str__(self):
        return f"{self.user.username} - {self.headline}"

