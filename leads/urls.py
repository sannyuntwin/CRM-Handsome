from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.lead_list, name='lead_list'),
    path('create/', views.lead_create, name='lead_create'),
    path('<int:pk>/', views.lead_detail, name='lead_detail'),
    path('<int:pk>/edit/', views.lead_update, name='lead_update'),
    path('<int:pk>/delete/', views.lead_delete, name='lead_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('<int:lead_pk>/communications/add/', views.communication_create, name='communication_create'),
    path('<int:lead_pk>/communications/<int:pk>/edit/', views.communication_edit, name='communication_edit'),
    path('<int:lead_pk>/communications/<int:pk>/delete/', views.communication_delete, name='communication_delete'),
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/export/', views.export_analytics_csv, name='export_analytics_csv'),
]
