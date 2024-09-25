from django.contrib import admin
from .models import Proceso, Evento

@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nombre', 'estado', 'fecha_inicio']
    search_fields = ['numero', 'nombre']
    list_filter = ['estado', 'direccion', 'grupo']

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['proceso', 'actividad', 'fecha', 'importe']
    search_fields = ['proceso__nombre', 'actividad']
    list_filter = ['fecha']
