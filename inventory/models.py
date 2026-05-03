from django.db import models
from schools.models import School
from core.models import TenantManager

class AssetCategory(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='asset_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ('school', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name

class AssetItem(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='assets')
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    condition = models.CharField(max_length=50, blank=True)  # e.g., New, Good, Fair, Damaged
    location = models.CharField(max_length=100, blank=True)
    date_added = models.DateField(auto_now_add=True)

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"
