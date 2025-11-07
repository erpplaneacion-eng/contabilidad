# Generated manually to fix field length issues

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('separador_recibos', '0004_alter_procesamientorecibo_calidad_imagen_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recibodetectado',
            name='entidad_bancaria',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='recibodetectado',
            name='numero_cuenta',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='recibodetectado',
            name='referencia',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='recibodetectado',
            name='concepto',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='recibodetectado',
            name='estado_pago',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='recibodetectado',
            name='tipo_cuenta',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='recibodetectado',
            name='documento',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
