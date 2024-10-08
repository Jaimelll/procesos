from django import forms
from .models import Proceso, Evento, Parametro, Formula
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProcesoForm(forms.ModelForm):
    periodo = forms.ModelChoiceField(queryset=Formula.objects.filter(parametro_id=11), required=False, to_field_name='orden')
    convocado = forms.ModelChoiceField(queryset=Formula.objects.filter(parametro_id=11), required=False, to_field_name='orden')

    class Meta:
        model = Proceso
        fields = ['nomenclatura', 'nombre', 'descripcion', 'moneda', 'cambio', 'estimado', 'expediente', 'periodo', 'convocatoria', 'convocado', 'derivado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['periodo'].label_from_instance = lambda obj: f"{obj.nombre} (Orden: {obj.orden})"
        self.fields['convocado'].label_from_instance = lambda obj: f"{obj.nombre} (Orden: {obj.orden})"

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data['periodo']:
            instance.periodo_id = self.cleaned_data['periodo'].orden
        if self.cleaned_data['convocado']:
            instance.convocado_id = self.cleaned_data['convocado'].orden
        if commit:
            instance.save()
        return instance

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
    estimado_condition = forms.ChoiceField(choices=[('gt', 'Mayor que'), ('lt', 'Menor que'), ('eq', 'Igual a')], required=False)
    estado = forms.ChoiceField(required=False)  # Descomentamos esta línea
    convoca = forms.ModelChoiceField(queryset=Formula.objects.filter(parametro_id=11), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener las opciones de estado desde la base de datos
        estados = Formula.objects.filter(parametro_id=29).values_list('nombre', 'nombre').distinct()
        self.fields['estado'].choices = [('', 'Todos')] + list(estados)

        # Establecer el valor por defecto para el campo 'convoca'
        default_convoca = Formula.objects.filter(parametro_id=11, cantidad=2).first()
        if default_convoca:
            self.fields['convoca'].initial = default_convoca.id

        # Modificar las opciones de convoca para incluir el orden
        self.fields['convoca'].queryset = Formula.objects.filter(parametro_id=11)
        self.fields['convoca'].label_from_instance = lambda obj: f"{obj.nombre} (Orden: {obj.orden})"

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