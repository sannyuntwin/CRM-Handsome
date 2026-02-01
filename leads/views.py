from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Lead
from .forms import LeadForm

def lead_list(request):
    leads = Lead.objects.all().order_by('-date_created')
    return render(request, 'leads/lead_list.html', {'leads': leads})

def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead created successfully!')
            return redirect('lead_list')
    else:
        form = LeadForm()
    return render(request, 'leads/lead_form.html', {'form': form, 'title': 'Create Lead'})

def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    return render(request, 'leads/lead_detail.html', {'lead': lead})

def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully!')
            return redirect('lead_detail', pk=lead.pk)
    else:
        form = LeadForm(instance=lead)
    return render(request, 'leads/lead_form.html', {'form': form, 'title': 'Edit Lead', 'lead': lead})

def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully!')
        return redirect('lead_list')
    return render(request, 'leads/lead_confirm_delete.html', {'lead': lead})
