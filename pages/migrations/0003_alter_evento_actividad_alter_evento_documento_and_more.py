# Generated by Django 5.0.3 on 2024-09-14 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_evento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='actividad',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='documento',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='importe',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='evento',
            name='situacion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
