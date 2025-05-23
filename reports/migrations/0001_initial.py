# Generated by Django 5.1.7 on 2025-05-14 08:50

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('report_type', models.CharField(choices=[('condition', 'Condition Assessment Report'), ('maintenance', 'Maintenance Planning Report'), ('network', 'Network Overview Report'), ('budget', 'Budget Allocation Report'), ('custom', 'Custom Report')], max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_range_start', models.DateField(blank=True, null=True)),
                ('date_range_end', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='reports/pdf/')),
                ('parameters', models.JSONField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('road_sections', models.ManyToManyField(blank=True, to='inventory.roadsection')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
