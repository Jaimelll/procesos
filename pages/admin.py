from django.contrib import admin
from .models import Proceso, Evento, Parametro, Formula

class ProcesoAdmin(admin.ModelAdmin):
    list_display = ('nomenclatura', 'nombre', 'estimado', 'periodo')
    list_filter = ('moneda', 'periodo', 'convocatoria')
    search_fields = ('nomenclatura', 'nombre', 'descripcion')

admin.site.register(Proceso, ProcesoAdmin)
admin.site.register(Evento)
admin.site.register(Parametro)
admin.site.register(Formula)
