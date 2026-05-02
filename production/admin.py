from django.contrib import admin
from .models import ProductionTask


@admin.register(ProductionTask)
class ProductionAdmin(admin.ModelAdmin):
    # This controls the columns you see in the main list
    list_display = ('production_date', 'line', 'lot_number', 'model_name', 'prd_customer', 'daily_quantity')
    
    # This adds a filter sidebar on the right
    list_filter = ('production_date', 'line', 'prd_customer')
    
    # This adds a search bar at the top
    search_fields = ('lot_number', 'model_name', 'prd_customer')

