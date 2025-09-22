from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_jobseeker_profile(sender, instance, created, **kwargs):
    if created:
        JobSeekerProfile.objects.create(user=instance)
        
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
        return f"{self.username} - {self.headline}"

