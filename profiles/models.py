from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import geocode_address
               
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
    
    street = models.CharField(max_length=255, blank=True)
    apartment = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    
    @property
    def full_address(self):
        """Combine fields for geocoding."""
        parts = [self.street, self.apartment, self.city, self.state, self.postal_code, self.country]
        return ", ".join([p for p in parts if p])

    def save(self, *args, **kwargs):
        """Geocode when address fields change."""
        if self.full_address:
            if self.pk:
                old = JobSeekerProfile.objects.filter(pk=self.pk).first()
                if not old or old.full_address != self.full_address:
                    lat, lng = geocode_address(self.full_address)
                    self.lat, self.lng = lat, lng
            else:
                lat, lng = geocode_address(self.full_address)
                self.lat, self.lng = lat, lng
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.headline}"

