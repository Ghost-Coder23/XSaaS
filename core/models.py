from django.db import models
from .middleware import get_current_school

class TenantManager(models.Manager):
    """Manager to automatically filter querysets by the current school (tenant)"""
    def get_queryset(self):
        queryset = super().get_queryset()
        school = get_current_school()
        if school:
            return queryset.filter(school=school)
        return queryset
