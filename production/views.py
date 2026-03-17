from django.shortcuts import render
from .models import MarchProductionTask
from django.db.models import Sum

def dashboard(request):
    tasks = MarchProductionTask.objects.all()
    grand_total = tasks.aggregate(Sum('daily_quantity'))['daily_quantity__sum'] or 0

    context = {
        'tasks': tasks,
        'grand_total': grand_total,
    }

    return render(request, 'production/dashboard.html', context)
