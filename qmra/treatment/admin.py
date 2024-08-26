from django.contrib import admin

from qmra.treatment.models import Treatment, Reference, PathogenGroup, Pathogen, LogRemoval


# Register your models here.
@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group", "category")
    pass


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "link")
    pass


@admin.register(PathogenGroup)
class PathogenGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Pathogen)
class PathogenAdmin(admin.ModelAdmin):
    pass


@admin.register(LogRemoval)
class LogRemovalAdmin(admin.ModelAdmin):
    list_display = ("id", "treatment", "pathogen_group", "min", "max", "reference")
    pass
