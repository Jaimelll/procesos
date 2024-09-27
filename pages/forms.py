from django import forms
from .models import Proceso, Evento, Parametro, Formula
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        # Asegúrate de incluir todos los campos del modelo Proceso
        fields = [
            'numero', 'nombre', 'descripcion', 'previsto', 'estimado', 'estado', 'fecha_inicio',
            'especialista_uare', 'acotaciones_adicionales', 'direccion', 'grupo', 'obtencion',
            'cant_items', 'cant_unidades'
        ]

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['actividad', 'documento', 'fecha', 'situacion', 'importe']
    
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
    numero = forms.IntegerField(
        required=False, 
        label='Número', 
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese número'})  # Cambiar a TextInput para permitir entrada manual
    )
    nombre = forms.CharField(required=False, label='Nombre', max_length=100)
    
    direccion = forms.CharField(required=False, label='Dirección', max_length=50)
    
    previsto = forms.DecimalField(
        required=False, 
        label='Previsto', 
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese monto previsto'})  # Cambiar a TextInput para el campo de monto
    )
    previsto_condition = forms.ChoiceField(
        required=False,
        label='Condición Previsto',
        choices=[('lt', 'Menor que'), ('gt', 'Mayor que')],
        widget=forms.Select()
    )

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

