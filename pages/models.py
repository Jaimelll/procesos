from django.db import models
from django.utils import timezone

class Proceso(models.Model):
    id = models.IntegerField(primary_key=True)
    nomenclatura = models.CharField(max_length=100, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, unique=True, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    moneda = models.IntegerField(default=1)
    cambio = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expediente = models.IntegerField(null=True, blank=True)
    periodo = models.IntegerField(default=10)
    convocatoria = models.IntegerField(default=1)
    convocado = models.IntegerField(default=10)
    derivado = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nombre or ''

    class Meta:
        verbose_name = "Proceso"
        verbose_name_plural = "Procesos"

    def get_estado(self):
        ultimo_evento = self.eventos.order_by('-fecha', '-id').first()
        if ultimo_evento:
            formula_estado = Formula.objects.filter(parametro_id=29, cantidad=ultimo_evento.acti).first()
            if formula_estado:
                return formula_estado.nombre
        return "Sin estado"

    def get_orden_estado(self):
        ultimo_evento = self.eventos.order_by('-fecha', '-id').first()
        if ultimo_evento:
            formula_orden = Formula.objects.filter(parametro_id=12, descripcion=ultimo_evento.acti).first()
            if formula_orden:
                return formula_orden.orden
        return 0

class Evento(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name='eventos')  # Relación con Proceso
    actividad = models.CharField(max_length=100, blank=True, null=True)  # Campo de texto corto
    documento = models.CharField(max_length=100, blank=True, null=True)  # Campo de texto corto
    fecha = models.DateField(default=timezone.now)  # Usa la fecha actual como valor por defecto
    situacion = models.TextField(blank=True, null=True)  # Campo de texto largo
    importe = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Campo numérico con 2 decimales, por defecto 0
    acti = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.actividad or ''} - {self.proceso.nombre or ''}"

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

class Formula(models.Model):
    parametro = models.ForeignKey(Parametro, on_delete=models.CASCADE, related_name='formulas', null=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)  # O cualquier otro valor por defecto que tenga sentido para tu aplicación
    obs = models.CharField(max_length=255, blank=True, null=True)
    cantidad = models.IntegerField(null=True, blank=True)
    numero = models.IntegerField(null=True, blank=True)
    acti = models.CharField(max_length=50, blank=True, null=True)
    respon = models.CharField(max_length=100, blank=True, null=True)
    respon2 = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.parametro.nombre if self.parametro else ''} - {self.nombre}"

    class Meta:
        verbose_name = "Fórmula"
        verbose_name_plural = "Fórmulas"