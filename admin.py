from django.contrib import admin
from django.utils.html import format_html
from .models import Team, TeamMember, StatusUpdate, EmailNotification, Mentor

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'leader_name', 'leader_email', 'project_title', 'registration_date', 'is_active']
    list_filter = ['registration_date', 'is_active', 'technology_stack']
    search_fields = ['team_name', 'leader_name', 'leader_email', 'project_title']
    readonly_fields = ['id', 'update_token', 'registration_date']
    
    fieldsets = (
        ('Team Information', {
            'fields': ('team_name', 'is_active')
        }),
        ('Leader Information', {
            'fields': ('leader_name', 'leader_email', 'leader_phone', 'leader_college')
        }),
        ('Project Information', {
            'fields': ('project_title', 'project_description', 'technology_stack')
        }),
        ('System Information', {
            'fields': ('id', 'update_token', 'registration_date'),
            'classes': ('collapse',)
        })
    )

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'team']
    list_filter = ['team']
    search_fields = ['name', 'email', 'team__team_name']

@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['team', 'update_type', 'submitted_at', 'file_preview']
    list_filter = ['update_type', 'submitted_at']
    search_fields = ['team__team_name', 'text_content']
    readonly_fields = ['submitted_at']
    
    def file_preview(self, obj):
        if obj.file_upload:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file_upload.url)
        return "No file"
    file_preview.short_description = "File"

@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['team', 'email_type', 'sent_at', 'is_successful']
    list_filter = ['email_type', 'is_successful', 'sent_at']
    search_fields = ['team__team_name']

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'expertise']
    search_fields = ['name', 'expertise']
