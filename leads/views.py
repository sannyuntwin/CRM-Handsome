from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse
from .models import Lead, UserProfile, Communication
from .forms import LeadForm
from .forms_auth import CustomUserCreationForm
from .forms_communication import CommunicationForm

@login_required
def lead_list(request):
    status_filter = request.GET.get('status', '')
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    leads = Lead.objects.all()
    
    if user_profile.role == 'sales_rep':
        leads = leads.filter(assigned_to=request.user)
    
    if status_filter:
        leads = leads.filter(status=status_filter)
    
    leads = leads.order_by('-date_created')
    
    return render(request, 'leads/lead_list.html', {
        'leads': leads,
        'status_filter': status_filter,
        'status_choices': Lead.STATUS_CHOICES,
        'user_role': user_profile.role
    })

@login_required
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST, user=request.user)
        if form.is_valid():
            lead = form.save(commit=False)
            if request.user.is_authenticated:
                lead.assigned_to = request.user
            lead.save()
            messages.success(request, 'Lead created successfully!')
            return redirect('lead_list')
    else:
        form = LeadForm(user=request.user)
    return render(request, 'leads/lead_form.html', {'form': form, 'title': 'Create Lead'})

@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    if user_profile.role == 'sales_rep' and lead.assigned_to != request.user:
        messages.error(request, "You don't have permission to view this lead.")
        return redirect('lead_list')
    
    communications = lead.communications.all()
    
    return render(request, 'leads/lead_detail.html', {'lead': lead, 'communications': communications})

@login_required
def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    if user_profile.role == 'sales_rep' and lead.assigned_to != request.user:
        messages.error(request, "You don't have permission to edit this lead.")
        return redirect('lead_list')
    
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully!')
            return redirect('lead_detail', pk=lead.pk)
    else:
        form = LeadForm(instance=lead, user=request.user)
    return render(request, 'leads/lead_form.html', {'form': form, 'title': 'Edit Lead', 'lead': lead})

@login_required
def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    if user_profile.role == 'sales_rep' and lead.assigned_to != request.user:
        messages.error(request, "You don't have permission to delete this lead.")
        return redirect('lead_list')
    
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully!')
        return redirect('lead_list')
    return render(request, 'leads/lead_confirm_delete.html', {'lead': lead})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    leads = Lead.objects.all()
    
    if user_profile.role == 'sales_rep':
        leads = leads.filter(assigned_to=request.user)
    
    status_counts = {}
    for status, _ in Lead.STATUS_CHOICES:
        status_counts[status] = leads.filter(status=status).count()
    
    recent_leads = leads.order_by('-date_created')[:5]
    
    # Communication statistics
    communications = Communication.objects.all()
    if user_profile.role == 'sales_rep':
        communications = communications.filter(lead__assigned_to=request.user)
    
    total_communications = communications.count()
    recent_communications = communications.order_by('-date_time')[:5]
    
    communication_types = {}
    for comm_type, _ in Communication.TYPE_CHOICES:
        communication_types[comm_type] = communications.filter(type=comm_type).count()
    
    return render(request, 'dashboard.html', {
        'status_counts': status_counts,
        'recent_leads': recent_leads,
        'total_leads': leads.count(),
        'user_role': user_profile.role,
        'total_communications': total_communications,
        'recent_communications': recent_communications,
        'communication_types': communication_types
    })

@login_required
def communication_create(request, lead_pk):
    lead = get_object_or_404(Lead, pk=lead_pk)
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    if user_profile.role == 'sales_rep' and lead.assigned_to != request.user:
        messages.error(request, "You don't have permission to add communications to this lead.")
        return redirect('lead_detail', pk=lead_pk)
    
    if request.method == 'POST':
        form = CommunicationForm(request.POST, lead=lead, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Communication added successfully!')
            return redirect('lead_detail', pk=lead_pk)
    else:
        form = CommunicationForm(lead=lead, user=request.user)
    
    return render(request, 'communications/communication_form.html', {
        'form': form,
        'lead': lead,
        'title': 'Add Communication'
    })

@login_required
def communication_edit(request, lead_pk, pk):
    lead = get_object_or_404(Lead, pk=lead_pk)
    communication = get_object_or_404(Communication, pk=pk, lead=lead)
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    if user_profile.role == 'sales_rep' and lead.assigned_to != request.user:
        messages.error(request, "You don't have permission to edit communications for this lead.")
        return redirect('lead_detail', pk=lead_pk)
    
    if request.method == 'POST':
        form = CommunicationForm(request.POST, instance=communication, lead=lead, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Communication updated successfully!')
            return redirect('lead_detail', pk=lead_pk)
    else:
        form = CommunicationForm(instance=communication, lead=lead, user=request.user)
    
    return render(request, 'communications/communication_form.html', {
        'form': form,
        'lead': lead,
        'communication': communication,
        'title': 'Edit Communication'
    })

@login_required
def communication_delete(request, lead_pk, pk):
    lead = get_object_or_404(Lead, pk=lead_pk)
    communication = get_object_or_404(Communication, pk=pk, lead=lead)
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    if user_profile.role == 'sales_rep' and lead.assigned_to != request.user:
        messages.error(request, "You don't have permission to delete communications for this lead.")
        return redirect('lead_detail', pk=lead_pk)
    
    if request.method == 'POST':
        communication.delete()
        messages.success(request, 'Communication deleted successfully!')
        return redirect('lead_detail', pk=lead_pk)
    
    return render(request, 'communications/communication_confirm_delete.html', {
        'communication': communication,
        'lead': lead
    })

@login_required
def analytics(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    # Date range filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    # Base queryset based on user role
    leads = Lead.objects.all()
    communications = Communication.objects.all()
    
    if user_profile.role == 'sales_rep':
        leads = leads.filter(assigned_to=request.user)
        communications = communications.filter(lead__assigned_to=request.user)
    
    leads = leads.filter(date_created__date__range=[start_date, end_date])
    communications = communications.filter(date_time__date__range=[start_date, end_date])
    
    # Lead Statistics
    total_leads = leads.count()
    lead_status_counts = dict(leads.values('status').annotate(count=Count('id')).values_list('status', 'count'))
    
    # Conversion Rates
    converted_leads = leads.filter(status='converted').count()
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Lead Funnel Analysis
    funnel_data = []
    for status, label in Lead.STATUS_CHOICES:
        count = leads.filter(status=status).count()
        percentage = (count / total_leads * 100) if total_leads > 0 else 0
        funnel_data.append({
            'status': label,
            'count': count,
            'percentage': percentage
        })
    
    # Sales Performance by User
    if user_profile.role in ['admin', 'manager']:
        sales_performance = []
        users = User.objects.filter(userprofile__role='sales_rep')
        for user in users:
            user_leads = Lead.objects.filter(assigned_to=user, date_created__date__range=[start_date, end_date])
            user_converted = user_leads.filter(status='converted').count()
            user_conversion_rate = (user_converted / user_leads.count() * 100) if user_leads.count() > 0 else 0
            
            sales_performance.append({
                'user': user.get_full_name() or user.username,
                'total_leads': user_leads.count(),
                'converted_leads': user_converted,
                'conversion_rate': user_conversion_rate,
                'communications': communications.filter(lead__assigned_to=user).count()
            })
    else:
        sales_performance = [{
            'user': request.user.get_full_name() or request.user.username,
            'total_leads': total_leads,
            'converted_leads': converted_leads,
            'conversion_rate': conversion_rate,
            'communications': communications.count()
        }]
    
    # Communication Analytics
    total_communications = communications.count()
    communication_types = dict(communications.values('type').annotate(count=Count('id')).values_list('type', 'count'))
    
    # Daily Trends (Last 7 days)
    daily_trends = []
    for i in range(7):
        date = (timezone.now().date() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_leads = leads.filter(date_created__date=date).count()
        day_communications = communications.filter(date_time__date=date).count()
        daily_trends.append({
            'date': (timezone.now().date() - timedelta(days=i)).strftime('%m/%d'),
            'leads': day_leads,
            'communications': day_communications
        })
    daily_trends.reverse()
    
    # Top Performing Leads (most communications)
    top_leads = []
    lead_comm_counts = dict(communications.values('lead_id').annotate(count=Count('id')).values_list('lead_id', 'count')[:10])
    for lead_id, count in lead_comm_counts.items():
        lead = Lead.objects.get(id=lead_id)
        top_leads.append({
            'lead': f"{lead.first_name} {lead.last_name}",
            'communications': count,
            'status': lead.get_status_display()
        })
    
    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_leads': total_leads,
        'converted_leads': converted_leads,
        'conversion_rate': round(conversion_rate, 2),
        'total_communications': total_communications,
        'lead_status_counts': lead_status_counts,
        'funnel_data': funnel_data,
        'sales_performance': sales_performance,
        'communication_types': communication_types,
        'daily_trends': daily_trends,
        'top_leads': top_leads,
        'user_role': user_profile.role
    }
    
    return render(request, 'analytics.html', context)

@login_required
def export_analytics_csv(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='sales_rep')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    leads = Lead.objects.filter(date_created__date__range=[start_date, end_date])
    if user_profile.role == 'sales_rep':
        leads = leads.filter(assigned_to=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="crm_analytics_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Lead Name', 'Email', 'Phone', 'Status', 'Assigned To', 'Created Date', 'Communications Count'])
    
    for lead in leads:
        comm_count = Communication.objects.filter(lead=lead).count()
        writer.writerow([
            f"{lead.first_name} {lead.last_name}",
            lead.email,
            lead.phone,
            lead.get_status_display(),
            lead.assigned_to.get_full_name() or lead.assigned_to.username if lead.assigned_to else 'Unassigned',
            lead.date_created.strftime('%Y-%m-%d %H:%M'),
            comm_count
        ])
    
    return response
