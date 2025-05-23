# Generated by Django 5.1.7 on 2025-05-13 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaintenanceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('average_cost_per_sqm', models.DecimalField(decimal_places=2, max_digits=10)),
                ('typical_lifespan_years', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='planned', max_length=20)),
                ('planned_date', models.DateField()),
                ('completed_date', models.DateField(blank=True, null=True)),
                ('estimated_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('actual_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('contractor', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('road_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.roadsection')),
                ('maintenance_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maintenance.maintenancetype')),
            ],
        ),
    ]
