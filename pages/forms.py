from django import forms
from .models import Proceso, Evento, Parametro, Formula
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = ['nomenclatura', 'nombre', 'descripcion', 'moneda', 'cambio', 'estimado', 'expediente', 'periodo', 'convocatoria', 'convocado', 'derivado']

class EventoForm(forms.ModelForm):
    acti = forms.ChoiceField(label="Actividad (Fórmula)")

    class Meta:
        model = Evento
        fields = ['actividad', 'documento', 'fecha', 'situacion', 'importe', 'acti']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        formulas = Formula.objects.filter(parametro_id=12).order_by('orden')
        self.fields['acti'].choices = [(f.orden, f.nombre) for f in formulas]

    def clean_importe(self):
        # Asegurarse de que el campo importe no sea nulo o vacío y asignar 0 por defecto
        importe = self.cleaned_data.get('importe')
        if importe is None:
            return 0
        return importe

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProcesoFilterForm(forms.Form):
    nombre = forms.CharField(required=False)
    descripcion = forms.CharField(required=False)
    estimado = forms.DecimalField(required=False)
    estimado_condition = forms.ChoiceField(
        choices=[('gt', 'Mayor que'), ('lt', 'Menor que'), ('eq', 'Igual a')],
        required=False
    )
    estado = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener las opciones de estado desde la base de datos
        estados = Formula.objects.filter(parametro_id=29, respon='2').values_list('nombre', 'nombre').distinct()
        self.fields['estado'].choices = [('', 'Todos')] + list(estados)

        # Añadir clases de Bootstrap a los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control mb-2'})

class ParametroForm(forms.ModelForm):
    class Meta:
        model = Parametro
        fields = ['nombre', 'descripcion', 'tipo']

class ParametroFilterForm(forms.Form):
    nombre = forms.CharField(required=False, label='Nombre', max_length=100)
    tipo = forms.CharField(required=False, label='Tipo', max_length=20)

class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula
        fields = ['nombre', 'descripcion', 'orden', 'obs', 'cantidad', 'numero', 'acti', 'respon', 'respon2']

