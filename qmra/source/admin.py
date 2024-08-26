from django.contrib import admin

from qmra.source.models import WaterSource, Inflow


# Register your models here.
@admin.register(WaterSource)
class SourceWaterAdmin(admin.ModelAdmin):
    pass


@admin.register(Inflow)
class InflowAdmin(admin.ModelAdmin):
    list_display = ("id", "pathogen", "water_source", "min", "max")
    pass
