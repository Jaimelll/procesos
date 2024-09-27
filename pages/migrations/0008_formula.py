# Generated by Django 5.0.3 on 2024-09-27 02:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_parametro'),
    ]

    operations = [
        migrations.CreateModel(
            name='Formula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('orden', models.IntegerField()),
                ('obs', models.CharField(blank=True, max_length=255, null=True)),
                ('cantidad', models.IntegerField(blank=True, null=True)),
                ('numero', models.IntegerField(blank=True, null=True)),
                ('acti', models.CharField(blank=True, max_length=50, null=True)),
                ('respon', models.CharField(blank=True, max_length=100, null=True)),
                ('respon2', models.CharField(blank=True, max_length=100, null=True)),
                ('parametro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='formulas', to='pages.parametro')),
            ],
            options={
                'verbose_name': 'Fórmula',
                'verbose_name_plural': 'Fórmulas',
            },
        ),
    ]
