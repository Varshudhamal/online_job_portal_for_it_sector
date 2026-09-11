from datetime import date
from django import forms
from django.db import models
from django.contrib.auth.models import User


class JobCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Company(models.Model):
    employer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/')

    def __str__(self):
        return self.name


class Job(models.Model):
    # Define the categories as a tuple of tuples
    CATEGORY_CHOICES = [
        ('software_development', 'Software Development'),
        ('data_science', 'Data Science & Analytics'),
        ('web_development', 'Web Development'),
        ('cloud_computing', 'Cloud Computing'),
        ('cybersecurity', 'Cybersecurity'),
        ('devops', 'DevOps'),
        ('networking', 'Networking'),
        ('database_management', 'Database Management'),
        ('ai_ml', 'Artificial Intelligence & Machine Learning'),
        ('project_management', 'Project Management & IT Consultancy'),
        ('it_support', 'Systems & IT Support'),
        ('quality_assurance', 'Quality Assurance & Testing'),
        ('blockchain', 'Blockchain'),
        ('digital_marketing', 'Digital Marketing & SEO'),
        ('business_intelligence', 'Business Intelligence & Reporting'),
    ]

    job_title = models.CharField(max_length=200)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='job_set')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)  # Use choices for categories
    location = models.CharField(max_length=100)
    description = models.TextField()
    posted_on = models.DateField(default=date.today)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional
    application_deadline = models.DateField(null=True, blank=True)  # Optional
    vacancies = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.job_title

    def total_applications(self):
        return self.application_set.count()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='user_resumes/', blank=True, null=True)
    
    # Changed company field to a ForeignKey to Company
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_employer = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=True)
    preferred_location = models.CharField(max_length=255, blank=True, null=True)
    employment_type = models.CharField(max_length=100, blank=True, null=True)
    preferred_job_title = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username



class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    applied_on = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(upload_to='applications_resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.job.job_title} Application"
