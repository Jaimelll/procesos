# Generated by Django 5.0.3 on 2024-09-29 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_alter_evento_fecha_alter_formula_orden_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proceso',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
