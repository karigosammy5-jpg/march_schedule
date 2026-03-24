from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/tasks/', views.ProductionTaskListView.as_view(), name='task-api'),
    path('api/tasks/<int:pk>/', views.ProductionTaskDetailAPI.as_view(), name='task-detail-api'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/tasks/update_by_lot_day/', views.update_task_by_lot_day, name='update_by_lot_day'),
]
