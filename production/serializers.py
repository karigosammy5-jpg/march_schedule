from rest_framework import serializers
from .models import ProductionTask

class ProductionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionTask
        fields = '__all__'