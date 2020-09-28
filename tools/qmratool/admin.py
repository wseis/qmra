from django.contrib import admin
from .models import Treatment, RiskAssessment, User, LogRemoval, Exposure, Reference, SourceWater, PathogenGroup
# Register your models here.


admin.site.register(Treatment)
admin.site.register(RiskAssessment)
admin.site.register(User)
admin.site.register(LogRemoval)
admin.site.register(Exposure)
admin.site.register(Reference)
admin.site.register(SourceWater)
admin.site.register(PathogenGroup)