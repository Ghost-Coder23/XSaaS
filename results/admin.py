from django.contrib import admin
from .models import Term, GradeScale, StudentResult, TermSummary, YearlyResult

admin.site.register(Term)
admin.site.register(GradeScale)
admin.site.register(StudentResult)
admin.site.register(TermSummary)
admin.site.register(YearlyResult)
