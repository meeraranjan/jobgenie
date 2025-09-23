from django.db import models

class Job(models.Model):
    JOB_TYPES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('IN', 'Internship'),
        ('CT', 'Contractor'),
    ]

    SPONSORSHIP_OPT = [
        ('YES', 'Sponsorship Available'), 
        ('NO', 'No Sponsorship'),
    ]
    
    title = models.CharField(max_length=255)
    skills = models.TextField(help_text="List required skills, separated by commas")
    location = models.CharField(max_length=255)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=2, choices=JOB_TYPES)
    visa_sponsorship = models.CharField(max_length=3, choices=SPONSORSHIP_OPT, default='NO')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company_name = models.CharField(max_length=255, blank=True, default="")

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(',')] if self.skills else []

    def __str__(self):
        return f"{self.title} ({self.location})"
