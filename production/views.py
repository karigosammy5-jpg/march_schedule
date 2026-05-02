import calendar
from datetime import datetime
from datetime import date
from django.shortcuts import render
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import ProductionTask
from .serializers import ProductionTaskSerializer

# --- 1. API VIEWS (For Searching and Live Data) ---
class ProductionTaskListView(generics.ListAPIView):
    queryset = ProductionTask.objects.all().order_by('production_date')
    serializer_class = ProductionTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['lot_number', 'line']
    search_fields = ['model_name', 'prd_customer']

class ProductionTaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionTask.objects.all()
    serializer_class = ProductionTaskSerializer

# --- 2. THE DASHBOARD VIEW (Dynamic Month Logic) ---
def dashboard(request):
    today = datetime.now()
    try:
        view_month = int(request.GET.get('month', today.month))
        view_year = int(request.GET.get('year', today.year))
    except (ValueError, TypeError):
        view_month = today.month
        view_year = today.year

    if view_month > 12:
        view_month = 1
        view_year += 1
    elif view_month < 1:
        view_month = 12
        view_year -= 1
    if view_month ==12:
        next_month = 1
        next_year = view_year + 1
    else:
        next_month = view_month + 1
        next_year = view_year
    if view_month == 1:
        prev_month = 12
        prev_year = view_year 
    else:
        prev_month = view_month - 1
        prev_year = view_year


    _, num_days = calendar.monthrange(view_year, view_month)
    current_month_days = range(1, num_days + 1)

    all_tasks = ProductionTask.objects.filter(
        production_date__year=view_year, 
        production_date__month=view_month
    ).order_by('production_date')
    
    n_series_grouped = {}
    f_series_grouped = {}

    for task in all_tasks:
        target_group = n_series_grouped if task.line == 'N' else f_series_grouped
        
        if task.lot_number not in target_group:
            target_group[task.lot_number] = {
                'model_name': task.model_name,
                'lot_number': task.lot_number,
                'ckd_arrival_iea': task.ckd_arrival_iea,
                'ckd_thailand': task.ckd_thailand,
                'prd_customer': task.prd_customer,
                'lot_total_units': task.lot_total_units,
                'days': {} 
            }
        
        target_group[task.lot_number]['days'][task.production_date.day] = task.daily_quantity

    context = {
        'n_series_lots': n_series_grouped.values(),
        'f_series_lots': f_series_grouped.values(),
        'month_days': current_month_days,
        'current_month_name': calendar.month_name[view_month],
        'current_month_number': view_month,
        'current_year': view_year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'now' : today,
    }
    return render(request, 'production/dashboard.html', context)

# --- 3. THE UPDATE API (The Save Button Logic) ---
@api_view(['POST'])
def update_task_by_lot_day(request):
    try:
        # We take whatever the HTML sends us
        html_lot_number = str(request.data.get('lot_number', ''))
        
        raw_day = request.data.get('day')
        raw_month = request.data.get('month')
        raw_year = request.data.get('year')
        raw_qty = request.data.get('quantity')
        
        day = int(raw_day) if raw_day else date.today().day
        current_month = int(raw_month) if raw_month else date.today().month
        current_year = int(raw_year) if raw_year else date.today().year
        quantity = int(raw_qty) if raw_qty else 0

        # FIX 1: Use __icontains so invisible spaces don't break the search
        existing_task = ProductionTask.objects.filter(
            lot_number__icontains=html_lot_number.strip(),
            production_date__year=current_year,
            production_date__month=current_month,
            production_date__day=day
        ).first()

        if existing_task:
            existing_task.daily_quantity = quantity
            existing_task.save()
            return Response({'status': 'Success! Updated existing.'}, status=status.HTTP_200_OK)

        else:
            template = ProductionTask.objects.filter(lot_number__icontains=html_lot_number.strip()).first()
            
            if not template:
                return Response({'error': 'Template not found.'}, status=status.HTTP_404_NOT_FOUND)

            # FIX 2: Strictly use date() so no midnight timezones get attached
            target_date = date(current_year, current_month, day)

            new_task = ProductionTask.objects.create(
                lot_number=template.lot_number, # FIX 3: Force it to use the EXACT string from the DB!
                production_date=target_date,
                daily_quantity=quantity,
                lot_total_units=template.lot_total_units,
                model_name=template.model_name,
                ckd_arrival_iea=template.ckd_arrival_iea,
                ckd_thailand=template.ckd_thailand,
                prd_customer=template.prd_customer
            )
            return Response({'status': 'Success! Created new.'}, status=status.HTTP_200_OK)
            
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)