from rest_framework import serializers
from .models import MarchProductionTask

class ProductionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarchProductionTask
        fields = '__all__'