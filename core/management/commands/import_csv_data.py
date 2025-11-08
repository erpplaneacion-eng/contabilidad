
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from core.models import Departamento, Municipio

class Command(BaseCommand):
    help = 'Import data from departamentos.csv and municipio.csv files'

    def handle(self, *args, **options):
        # Construct absolute paths to CSV files
        departamentos_csv_path = os.path.join(settings.BASE_DIR, 'archivois_excel', 'departamentos.csv')
        municipios_csv_path = os.path.join(settings.BASE_DIR, 'archivois_excel', 'municipio.csv')

        # Import Departamentos
        with open(departamentos_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                codigo_departamento = row[0]
                nombre_departamento = row[1]
                if not Departamento.objects.filter(codigo_departamento=codigo_departamento).exists():
                    Departamento.objects.create(
                        codigo_departamento=codigo_departamento,
                        nombre_departamento=nombre_departamento
                    )
            self.stdout.write(self.style.SUCCESS('Successfully imported Departamentos'))

        # Import Municipios
        with open(municipios_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                codigo_municipio = row[1]
                nombre_municipio = row[2]
                codigo_departamento = row[3]
                try:
                    departamento = Departamento.objects.get(codigo_departamento=codigo_departamento)
                    if not Municipio.objects.filter(codigo_municipio=codigo_municipio).exists():
                        Municipio.objects.create(
                            codigo_municipio=codigo_municipio,
                            nombre_municipio=nombre_municipio,
                            departamento=departamento
                        )
                except Departamento.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Departamento with code {codigo_departamento} not found for municipio {nombre_municipio}'))
            self.stdout.write(self.style.SUCCESS('Successfully imported Municipios'))
