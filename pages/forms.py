from django import forms
from .models import Proceso, Evento
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
    numero = forms.IntegerField(required=False, label='Número')
    nombre = forms.CharField(required=False, max_length=100, label='Nombre')
    descripcion = forms.CharField(required=False, max_length=100, label='Descripción')
