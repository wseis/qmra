from django.contrib import admin
from .models import Treatment, QA, Text, RiskAssessment, User, LogRemoval, Exposure, Reference, SourceWater, Pathogen, PathogenGroup, Health, Inflow, Guideline, DoseResponse

#from import_export.admin import ImportExportModelAdmin
# Register your models here.

@admin.register(SourceWater)
class SourceWaterAdmin(admin.ModelAdmin):
    pass


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display=("id", "name", "group", "category")
    pass

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display=("id", "name", "link")
    pass

@admin.register(PathogenGroup)
class PathogenGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Pathogen)
class PathogenAdmin(admin.ModelAdmin):
    pass

@admin.register(LogRemoval)
class LogRemovalAdmin(admin.ModelAdmin):
    list_display=("id", "treatment", "pathogen_group", "min", "max", "reference")
    pass


@admin.register(Exposure)
class ExposureAdmin(admin.ModelAdmin):
    pass


@admin.register(Inflow)
class InflowAdmin(admin.ModelAdmin):
    list_display=("id", "pathogen", "water_source", "min", "max")
    pass


@admin.register(Guideline)
class GuidelineAdmin(admin.ModelAdmin):
    pass


@admin.register(Health)
class HealthAdmin(admin.ModelAdmin):
    pass


@admin.register(DoseResponse)
class DoseResponseAdmin(admin.ModelAdmin):
    list_display=("id", "pathogen")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display=("id", "username")
    
  #  pass
#admin.site.register(Treatment)
admin.site.register(RiskAssessment)
#admin.site.register(User)
admin.site.register(Text)
admin.site.register(QA)
#admin.site.register(LogRemoval)
#admin.site.register(Exposure)
#admin.site.register(Reference)
#admin.site.register(SourceWater)
#admin.site.register(PathogenGroup)