from django.contrib import admin

from qmra.risk_assessment.models import Health, DoseResponse, RiskAssessment


# Register your models here.
@admin.register(Health)
class HealthAdmin(admin.ModelAdmin):
    pass


@admin.register(DoseResponse)
class DoseResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "pathogen")


admin.site.register(RiskAssessment)
