from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_dashboard, name='dashboard'),
    path('add-category/', views.add_asset_category, name='add_category'),
    path('add-item/', views.add_asset_item, name='add_item'),
]
