from django.urls import path
from .views import generate_training_plan, view_training_plan

app_name = 'training_plans'

urlpatterns = [
    path('generate/', generate_training_plan, name='generate_training_plan'),
    path('view/<int:pk>/', view_training_plan, name='view_training_plan'),
]
