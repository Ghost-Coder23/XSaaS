from django.contrib import admin
from .models import ReportCardTemplate, GeneratedReport

admin.site.register(ReportCardTemplate)
admin.site.register(GeneratedReport)
