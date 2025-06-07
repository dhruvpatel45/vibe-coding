from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
import uuid
from datetime import datetime, timedelta

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_name = models.CharField(max_length=200)
    leader_name = models.CharField(max_length=100)
    leader_email = models.EmailField(validators=[EmailValidator()])
    leader_phone = models.CharField(max_length=15)
    leader_college = models.CharField(max_length=200)
    project_title = models.CharField(max_length=300)
    project_description = models.TextField()
    technology_stack = models.TextField(help_text="Comma-separated technologies")
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    update_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    class Meta:
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.team_name} - {self.leader_name}"
    
    @property
    def tech_stack_list(self):
        return [tech.strip() for tech in self.technology_stack.split(',')]

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    
    def __str__(self):
        return f"{self.name} ({self.team.team_name})"

class StatusUpdate(models.Model):
    UPDATE_TYPES = [
        ('image', 'Image'),
        ('pdf', 'PDF Document'),
        ('text', 'Text Update'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='status_updates')
    update_type = models.CharField(max_length=10, choices=UPDATE_TYPES)
    text_content = models.TextField(blank=True, null=True)
    file_upload = models.FileField(upload_to='status_updates/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.team.team_name} - {self.update_type} - {self.submitted_at.strftime('%Y-%m-%d')}"

class EmailNotification(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='notifications')
    email_type = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.team.team_name} - {self.email_type}"

class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    expertise = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
