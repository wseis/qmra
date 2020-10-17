from django.contrib import admin
from .models import Treatment, RiskAssessment, User, LogRemoval, Exposure, Reference, SourceWater, Pathogen, PathogenGroup
# Register your models here.

from import_export.admin import ImportExportModelAdmin
# Register your models here.

@admin.register(SourceWater)
class SourceWaterAdmin(ImportExportModelAdmin):
    pass


@admin.register(Treatment)
class TreatmentAdmin(ImportExportModelAdmin):
    pass

@admin.register(Reference)
class ReferenceAdmin(ImportExportModelAdmin):
    pass

@admin.register(PathogenGroup)
class PathogenGroupAdmin(ImportExportModelAdmin):
    pass


@admin.register(Pathogen)
class PathogenAdmin(ImportExportModelAdmin):
    pass

@admin.register(LogRemoval)
class LogRemovalAdmin(ImportExportModelAdmin):
    pass

@admin.register(Exposure)
class ExposureAdmin(ImportExportModelAdmin):
    pass
#admin.site.register(Treatment)
admin.site.register(RiskAssessment)
admin.site.register(User)
#admin.site.register(LogRemoval)
#admin.site.register(Exposure)
#admin.site.register(Reference)
#admin.site.register(SourceWater)
#admin.site.register(PathogenGroup)