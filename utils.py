from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_update_reminder_email(team):
    """Send update reminder email to team leader"""
    update_url = f"{settings.SITE_URL}{reverse('team_update', kwargs={'token': team.update_token})}"
    
    subject = f'Project Update Request - {team.team_name}'
    message = f"""
    Dear {team.leader_name},
    
    We hope your hackathon project "{team.project_title}" is progressing well!
    
    Please provide an update on your project progress by clicking the link below:
    {update_url}
    
    You can submit:
    - Text description of your progress
    - Images of your work
    - PDF documents with detailed updates
    
    This secure link is unique to your team and can be used multiple times.
    
    Best regards,
    Hackathon Organizing Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [team.leader_email],
        fail_silently=False,
    )

def generate_team_report(team):
    """Generate a comprehensive report for a team"""
    return {
        'team_info': team,
        'members': team.members.all(),
        'updates': team.status_updates.all(),
        'notifications': team.notifications.all()
    }
