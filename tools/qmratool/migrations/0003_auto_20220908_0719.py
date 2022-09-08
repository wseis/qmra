# Generated by Django 3.2.6 on 2022-09-08 07:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qmratool', '0002_alter_exposure_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riskassessment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='treatment',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='treatments', to=settings.AUTH_USER_MODEL),
        ),
    ]
