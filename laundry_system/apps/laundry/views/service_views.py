from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.laundry.models import Service


@login_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'laundry/services/service_list.html', {'services': services})


def landing_page(request):
    return render(request, 'laundry/landing.html')