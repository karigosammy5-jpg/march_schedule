from django.db import models

class MarchProductionTask(models.Model):
    LINE_SERIES_CHOICES = [
        ('N', 'N-SERIES'),
        ('F', 'F-SERIES'),
    ]
    line = models.CharField(max_length=1, choices=LINE_SERIES_CHOICES)
    model_name = models.CharField(max_length=100)


    lot_number = models.CharField(max_length=20)

    ckd_arrival_iea = models.CharField(max_length=50, default="ISUZU EA")
    ckd_thailand = models.CharField(max_length=50, blank=True, null=True)



    prd_customer = models.CharField(max_length=200, blank=True, null=True, help_text="e.g., GSU Green, Tanesco green")
    production_date = models.DateField()
    daily_quantity = models.PositiveIntegerField(default=1)
    lot_total_units = models.PositiveIntegerField()

    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['production_date', 'line', 'lot_number']
    def __str__(self):
        return f"{self.production_date} | {self.get_line_display()} | {self.model_name} | Lot {self.lot_number}"
                       
