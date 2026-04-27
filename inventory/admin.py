from django.contrib import admin
from .models import AssetCategory, AssetItem

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'description')
    search_fields = ('name', 'school__name')
    list_filter = ('school',)

@admin.register(AssetItem)
class AssetItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'school', 'quantity', 'condition', 'location', 'date_added')
    search_fields = ('name', 'category__name', 'school__name')
    list_filter = ('category', 'school', 'condition')
