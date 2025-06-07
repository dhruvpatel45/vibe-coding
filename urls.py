from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_team, name='register_team'),
    path('success/<uuid:team_id>/', views.registration_success, name='registration_success'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/export-csv/', views.export_teams_csv, name='export_teams_csv'),
    path('admin/send-reminders/', views.send_update_reminders, name='send_update_reminders'),
    path('update/<uuid:token>/', views.team_update, name='team_update'),
    path('update-success/<uuid:token>/', views.update_success, name='update_success'),
    path('mentor/dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
]
