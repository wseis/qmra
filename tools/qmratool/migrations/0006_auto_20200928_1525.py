# Generated by Django 3.1.1 on 2020-09-28 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qmratool', '0005_auto_20200928_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riskassessment',
            name='exposure',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.PROTECT, to='qmratool.exposure'),
        ),
        migrations.AlterField(
            model_name='riskassessment',
            name='source',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.PROTECT, to='qmratool.sourcewater'),
        ),
        migrations.AlterField(
            model_name='riskassessment',
            name='treatment',
            field=models.ManyToManyField(blank=True, default=1, related_name='treatment', to='qmratool.Treatment'),
        ),
    ]
