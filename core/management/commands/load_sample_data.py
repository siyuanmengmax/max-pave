# core/management/commands/load_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import RoadSection
from assessments.models import AssessmentMethod
from maintenance.models import MaintenanceType
import datetime


class Command(BaseCommand):
    help = 'Load sample data for the pavement management system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin/admin'))

        # Create road sections
        if RoadSection.objects.count() == 0:
            roads = [
                {
                    'name': 'Main Street',
                    'road_id': 'MS-001',
                    'length': 1200,
                    'width': 7.5,
                    'surface_type': 'Asphalt',
                    'construction_date': datetime.date(2010, 5, 15),
                },
                {
                    'name': 'Oak Avenue',
                    'road_id': 'OA-002',
                    'length': 850,
                    'width': 6.0,
                    'surface_type': 'Asphalt',
                    'construction_date': datetime.date(2015, 7, 22),
                },
                {
                    'name': 'Pine Road',
                    'road_id': 'PR-003',
                    'length': 1500,
                    'width': 8.0,
                    'surface_type': 'Concrete',
                    'construction_date': datetime.date(2005, 3, 10),
                },
            ]

            for road_data in roads:
                RoadSection.objects.create(**road_data)

            self.stdout.write(self.style.SUCCESS(f'Created {len(roads)} road sections'))

        # Create assessment methods
        if AssessmentMethod.objects.count() == 0:
            methods = [
                {
                    'name': 'Visual Inspection',
                    'description': 'Manual visual inspection by trained personnel',
                    'is_automated': False,
                },
                {
                    'name': 'Computer Vision Analysis',
                    'description': 'Automated crack detection using image processing',
                    'is_automated': True,
                },
                {
                    'name': 'LiDAR Scan',
                    'description': 'High-precision laser scanning for detailed surface analysis',
                    'is_automated': True,
                },
            ]

            for method_data in methods:
                AssessmentMethod.objects.create(**method_data)

            self.stdout.write(self.style.SUCCESS(f'Created {len(methods)} assessment methods'))

        # Create maintenance types
        if MaintenanceType.objects.count() == 0:
            types = [
                {
                    'name': 'Crack Sealing',
                    'description': 'Filling and sealing cracks to prevent water infiltration',
                    'average_cost_per_sqm': 5.50,
                    'typical_lifespan_years': 3,
                },
                {
                    'name': 'Asphalt Overlay',
                    'description': 'Applying a new layer of asphalt over the existing surface',
                    'average_cost_per_sqm': 25.00,
                    'typical_lifespan_years': 8,
                },
                {
                    'name': 'Full Reconstruction',
                    'description': 'Complete removal and replacement of the pavement structure',
                    'average_cost_per_sqm': 75.00,
                    'typical_lifespan_years': 20,
                },
            ]

            for type_data in types:
                MaintenanceType.objects.create(**type_data)

            self.stdout.write(self.style.SUCCESS(f'Created {len(types)} maintenance types'))

        self.stdout.write(self.style.SUCCESS('Sample data creation completed'))