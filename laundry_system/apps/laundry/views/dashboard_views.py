import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.laundry.services.dashboard_service import get_dashboard_context


@login_required
def dashboard(request):
    context = get_dashboard_context()
    return render(request, 'laundry/dashboard/dashboard.html', context)