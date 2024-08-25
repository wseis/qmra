from django.contrib import admin

from qmra.scenario.models import ExposureScenario


# Register your models here.
@admin.register(ExposureScenario)
class ExposureAdmin(admin.ModelAdmin):
    pass
