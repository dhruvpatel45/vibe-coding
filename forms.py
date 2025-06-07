from django import forms
from django.forms import formset_factory
from .models import Team, TeamMember, StatusUpdate

class TeamRegistrationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'team_name', 'leader_name', 'leader_email', 'leader_phone',
            'leader_college', 'project_title', 'project_description', 'technology_stack'
        ]
        widgets = {
            'team_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter team name'}),
            'leader_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Team leader full name'}),
            'leader_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'leader@example.com'}),
            'leader_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'leader_college': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College/University name'}),
            'project_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your project title'}),
            'project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your project idea...'}),
            'technology_stack': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'React, Node.js, MongoDB, etc.'})
        }

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Member name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'member@example.com'})
        }

# Create a formset for dynamic team members
TeamMemberFormSet = formset_factory(TeamMemberForm, extra=1, max_num=5, can_delete=True)

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['update_type', 'text_content', 'file_upload']
        widgets = {
            'update_type': forms.Select(attrs={'class': 'form-control'}),
            'text_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your progress...'}),
            'file_upload': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        update_type = cleaned_data.get('update_type')
        text_content = cleaned_data.get('text_content')
        file_upload = cleaned_data.get('file_upload')
        
        if update_type == 'text' and not text_content:
            raise forms.ValidationError("Text content is required for text updates.")
        
        if update_type in ['image', 'pdf'] and not file_upload:
            raise forms.ValidationError("File upload is required for image/PDF updates.")
        
        return cleaned_data

class TeamSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by team name, project title, or leader name...'
        })
    )
    tech_stack = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by technology...'
        })
    )
