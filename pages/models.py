from django.db import models

class Proceso(models.Model):
    numero = models.IntegerField(unique=True)  # Corresponde a la columna 'Nº' en el Excel
    nombre = models.CharField(max_length=100, blank=True, null=True)  # Otro campo de ejemplo
    descripcion = models.TextField(blank=True, null=True)  # Campo de descripción
    direccion = models.CharField(max_length=50, blank=True, null=True)  # Nuevo campo 'direccion'
    grupo = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo 'grupo'
    obtencion = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo 'obtencion'
    cant_items = models.IntegerField(null=True, blank=True)  # Nuevo campo 'cant_items'
    cant_unidades = models.IntegerField(null=True, blank=True)  # Nuevo campo 'cant_unidades'
    previsto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Nuevo campo 'previsto'
    estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Nuevo campo 'estimado'
    estado = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo 'estado'
    fecha_inicio = models.DateField(null=True, blank=True)  # Nuevo campo 'fecha_inicio'
    especialista_uare = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo 'especialista_uare'
    acotaciones_adicionales = models.TextField(blank=True, null=True)  # Nuevo campo 'acotaciones_adicionales'
    creado_en = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática

    def __str__(self):
        return f"{self.numero} - {self.nombre}"

class Evento(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name='eventos')  # Relación con Proceso
    actividad = models.CharField(max_length=100, blank=True, null=True)  # Campo de texto corto
    documento = models.CharField(max_length=100, blank=True, null=True)  # Campo de texto corto
    fecha = models.DateField()  # Campo de tipo fecha
    situacion = models.TextField(blank=True, null=True)  # Campo de texto largo
    importe = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Campo numérico con 2 decimales, por defecto 0

    def __str__(self):
        return f"{self.actividad} - {self.proceso.nombre}"

class Parametro(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.tipo}: {self.nombre}"

    class Meta:
        verbose_name = "Parámetro"
        verbose_name_plural = "Parámetros"
        unique_together = ['tipo', 'nombre']