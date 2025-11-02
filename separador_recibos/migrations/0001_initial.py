# Generated migration for separador_recibos app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcesamientoRecibo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('archivo_original', models.FileField(upload_to='pdfs_originales/')),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PROCESANDO', 'Procesando'), ('COMPLETADO', 'Completado'), ('ERROR', 'Error')], default='PENDIENTE', max_length=20)),
                ('total_recibos', models.PositiveIntegerField(default=0)),
                ('archivo_resultado', models.FileField(blank=True, null=True, upload_to='pdfs_procesados/')),
                ('mensaje_error', models.TextField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReciboDetectado',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('numero_secuencial', models.PositiveIntegerField()),
                ('coordenada_x', models.FloatField()),
                ('coordenada_y', models.FloatField()),
                ('ancho', models.FloatField()),
                ('alto', models.FloatField()),
                ('imagen_recibo', models.ImageField(blank=True, null=True, upload_to='imagenes_recibos/')),
                ('nombre_beneficiario', models.CharField(blank=True, max_length=255)),
                ('valor', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('entidad_bancaria', models.CharField(blank=True, max_length=100)),
                ('numero_cuenta', models.CharField(blank=True, max_length=50)),
                ('referencia', models.CharField(blank=True, max_length=100)),
                ('fecha_aplicacion', models.DateField(blank=True, null=True)),
                ('concepto', models.CharField(blank=True, max_length=100)),
                ('estado_pago', models.CharField(blank=True, max_length=50)),
                ('tipo_cuenta', models.CharField(blank=True, max_length=20)),
                ('documento', models.CharField(blank=True, max_length=50)),
                ('texto_extraido', models.TextField(blank=True)),
                ('fecha_deteccion', models.DateTimeField(auto_now_add=True)),
                ('validado', models.BooleanField(default=False)),
                ('procesamiento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='separador_recibos.procesamientorecibo')),
            ],
            options={
                'ordering': ['numero_secuencial'],
            },
        ),
        migrations.AddIndex(
            model_name='recibodetectado',
            index=models.Index(fields=['procesamiento', 'numero_secuencial'], name='separador_r_procesa_f381e7_idx'),
        ),
        migrations.AddIndex(
            model_name='recibodetectado',
            index=models.Index(fields=['nombre_beneficiario'], name='separador_r_nombre_b_1a8c5c_idx'),
        ),
        migrations.AddIndex(
            model_name='recibodetectado',
            index=models.Index(fields=['fecha_aplicacion'], name='separador_r_fecha_a_2c8b4e_idx'),
        ),
    ]