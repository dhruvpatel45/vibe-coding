from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
import csv
import io
from .models import Team, TeamMember, StatusUpdate, EmailNotification, Mentor
from .forms import TeamRegistrationForm, TeamMemberFormSet, StatusUpdateForm, TeamSearchForm
from .utils import send_update_reminder_email

def home(request):
    """Home page with registration information"""
    return render(request, 'hackathon/home.html')

def register_team(request):
    """Team registration view with dynamic member forms"""
    if request.method == 'POST':
        team_form = TeamRegistrationForm(request.POST)
        member_formset = TeamMemberFormSet(request.POST)
        
        if team_form.is_valid() and member_formset.is_valid():
            # Save team
            team = team_form.save()
            
            # Save team members
            for form in member_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    member = form.save(commit=False)
                    member.team = team
                    member.save()
            
            # Send confirmation email
            send_confirmation_email(team)
            
            messages.success(request, f'Team "{team.team_name}" registered successfully!')
            return redirect('registration_success', team_id=team.id)
    else:
        team_form = TeamRegistrationForm()
        member_formset = TeamMemberFormSet()
    
    return render(request, 'hackathon/register.html', {
        'team_form': team_form,
        'member_formset': member_formset
    })

def registration_success(request, team_id):
    """Registration success page"""
    team = get_object_or_404(Team, id=team_id)
    return render(request, 'hackathon/registration_success.html', {'team': team})

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with search and filter capabilities"""
    search_form = TeamSearchForm(request.GET)
    teams = Team.objects.all()
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        tech_stack = search_form.cleaned_data.get('tech_stack')
        
        if search_query:
            teams = teams.filter(
                Q(team_name__icontains=search_query) |
                Q(project_title__icontains=search_query) |
                Q(leader_name__icontains=search_query)
            )
        
        if tech_stack:
            teams = teams.filter(technology_stack__icontains=tech_stack)
    
    return render(request, 'hackathon/admin_dashboard.html', {
        'teams': teams,
        'search_form': search_form,
        'total_teams': Team.objects.count(),
        'total_updates': StatusUpdate.objects.count()
    })

@staff_member_required
def export_teams_csv(request):
    """Export team data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hackathon_teams.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Team Name', 'Leader Name', 'Leader Email', 'Leader Phone', 'Leader College',
        'Project Title', 'Project Description', 'Technology Stack', 'Registration Date',
        'Team Members'
    ])
    
    for team in Team.objects.all():
        members = ', '.join([f"{m.name} ({m.email})" for m in team.members.all()])
        writer.writerow([
            team.team_name, team.leader_name, team.leader_email, team.leader_phone,
            team.leader_college, team.project_title, team.project_description,
            team.technology_stack, team.registration_date.strftime('%Y-%m-%d %H:%M'),
            members
        ])
    
    return response

def team_update(request, token):
    """Team status update view using secure token"""
    team = get_object_or_404(Team, update_token=token)
    
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.team = team
            update.save()
            
            messages.success(request, 'Status update submitted successfully!')
            return redirect('update_success', token=token)
    else:
        form = StatusUpdateForm()
    
    return render(request, 'hackathon/team_update.html', {
        'form': form,
        'team': team,
        'previous_updates': team.status_updates.all()[:5]
    })

def update_success(request, token):
    """Update submission success page"""
    team = get_object_or_404(Team, update_token=token)
    return render(request, 'hackathon/update_success.html', {'team': team})

@staff_member_required
def send_update_reminders(request):
    """Send update reminder emails to all teams"""
    teams = Team.objects.filter(is_active=True)
    sent_count = 0
    
    for team in teams:
        try:
            send_update_reminder_email(team)
            EmailNotification.objects.create(
                team=team,
                email_type='update_reminder',
                is_successful=True
            )
            sent_count += 1
        except Exception as e:
            EmailNotification.objects.create(
                team=team,
                email_type='update_reminder',
                is_successful=False
            )
    
    messages.success(request, f'Update reminders sent to {sent_count} teams!')
    return redirect('admin_dashboard')

@login_required
def mentor_dashboard(request):
    """Mentor dashboard to view team progress"""
    if not hasattr(request.user, 'mentor'):
        messages.error(request, 'Access denied. Mentor account required.')
        return redirect('home')
    
    teams = Team.objects.filter(is_active=True)
    updates = StatusUpdate.objects.all()[:20]  # Recent updates
    
    return render(request, 'hackathon/mentor_dashboard.html', {
        'teams': teams,
        'recent_updates': updates,
        'mentor': request.user.mentor
    })

def send_confirmation_email(team):
    """Send registration confirmation email"""
    subject = f'Registration Confirmed - {team.team_name}'
    message = f"""
    Dear {team.leader_name},
    
    Your team "{team.team_name}" has been successfully registered for the hackathon!
    
    Team Details:
    - Project Title: {team.project_title}
    - Technology Stack: {team.technology_stack}
    - Registration Date: {team.registration_date.strftime('%Y-%m-%d %H:%M')}
    
    You will receive update requests via email during the hackathon period.
    
    Best regards,
    Hackathon Organizing Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [team.leader_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")
