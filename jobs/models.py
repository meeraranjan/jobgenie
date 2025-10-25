from django.db import models
from django.conf import settings
from recruiters.models import Recruiter
from django.urls import reverse
from .utils import geocode_address


class Job(models.Model):
    JOB_TYPES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('IN', 'Internship'),
        ('CT', 'Contractor'),
    ]
    REMOTE_TYPES = [
        ('ON', 'On-site'),
        ('RE', 'Remote'),
        ('HY', 'Hybrid'),
    ]
    SPONSORSHIP_OPT = [
        ('YES', 'Sponsorship Available'),
        ('NO', 'No Sponsorship'),
    ]

    recruiter = models.ForeignKey(
    Recruiter,
    on_delete=models.CASCADE,
    related_name="jobs",
    null=True,
    blank=True
    )

    def get_absolute_url(self):
        return reverse('job_detail', args=[str(self.pk)])
    
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, default="")
    skills = models.TextField(help_text="List required skills, separated by commas", blank=True, default="")
    address = models.CharField(max_length=255, blank=True, help_text="Type office location or adjust pin on map")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=2, choices=JOB_TYPES)
    visa_sponsorship = models.CharField(max_length=3, choices=SPONSORSHIP_OPT, default='NO')
    remote_type = models.CharField(max_length=2, choices=REMOTE_TYPES, default='ON')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(',')] if self.skills else []
    
    @property
    def full_address(self):
        """Return a combined address string for display/geocoding."""
        parts = [self.address, self.city, self.state, self.postal_code, self.country]
        return ", ".join([p for p in parts if p])

    def save(self, *args, **kwargs):
        """Geocode automatically if lat/lng are missing or address changed."""
        address = self.full_address
        if address:
            old = Job.objects.filter(pk=self.pk).first() if self.pk else None
            if not old or old.full_address != address or not (self.lat and self.lng):
                lat, lng = geocode_address(address)
                if lat and lng:
                    self.lat = lat
                    self.lng = lng
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['job_type']),
            models.Index(fields=['remote_type']),
            models.Index(fields=['city']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.city})"

class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('review', 'Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('closed', 'Closed'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    note = models.TextField(blank=True)  # tailored note from candidate
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.candidate} for {self.job}"

    def get_status_badge_class(self):
        return {
            'applied': 'bg-secondary',
            'review': 'bg-info text-dark',
            'interview': 'bg-warning text-dark',
            'offer': 'bg-success',
            'closed': 'bg-danger'
        }.get(self.status, 'bg-dark')