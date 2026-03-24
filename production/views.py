from django.shortcuts import render
from .models import MarchProductionTask
from rest_framework import generics, filters
from .serializers import ProductionTaskSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

class ProductionTaskListView(generics.ListAPIView):
    queryset = MarchProductionTask.objects.all().order_by('production_date')
    serializer_class = ProductionTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['lot_number', 'line']
    search_fields = ['model_name', 'prd_customer']

class ProductionTaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = MarchProductionTask.objects.all()
    serializer_class = ProductionTaskSerializer

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

@api_view(['POST'])
def update_task_by_lot_day(request):
    # 1. Catch the data sent by your JavaScript
    lot_number = request.data.get('lot_number')
    day = request.data.get('day')
    quantity = request.data.get('quantity')
    
    try:
        # 2. Find the specific Isuzu Task for that Lot and Day in March
        task = MarchProductionTask.objects.get(
            lot_number=lot_number, 
            production_date__day=day
        )
        # 3. Update the quantity and save it to the database
        task.daily_quantity = quantity
        task.save()
        
        return Response({'status': 'Success!'}, status=status.HTTP_200_OK)
        
    except MarchProductionTask.DoesNotExist:
        return Response({'error': 'No scheduled task found for that Lot on that Day.'}, status=status.HTTP_404_NOT_FOUND)