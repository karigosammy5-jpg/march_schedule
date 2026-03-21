from django.shortcuts import render
from .models import MarchProductionTask

def dashboard(request):
    all_tasks = MarchProductionTask.objects.all().order_by('production_date')
    
    # We create a dictionary to group everything by Lot Number
    # Key: lot_number, Value: dictionary of all the lot's info
    n_series_grouped = {}
    f_series_grouped = {}

    for task in all_tasks:
        target_group = n_series_grouped if task.line == 'N' else f_series_grouped
        
        if task.lot_number not in target_group:
            target_group[task.lot_number] = {
                'model_name': task.model_name,
                'lot_number': task.lot_number,
                'ckd_arrival_iea': task.ckd_arrival_iea,
                'prd_customer': task.prd_customer,
                'lot_total_units': task.lot_total_units,
                'days': {} # We'll store the daily quantities here
            }
        
        # Assign the quantity to the specific day
        target_group[task.lot_number]['days'][task.production_date.day] = task.daily_quantity

    context = {
        'n_series_lots': n_series_grouped.values(),
        'f_series_lots': f_series_grouped.values(),
        'march_days': range(1, 32),
    }
    return render(request, 'production/dashboard.html', context)