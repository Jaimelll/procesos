from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Proceso, Evento
from .forms import ProcesoForm, CustomUserCreationForm, ProcesoFilterForm, EventoForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Count, Sum
from datetime import datetime, date
import locale
from django.core.paginator import Paginator  # Importar Paginator

# Importar los gráficos desde los archivos separados
from .graphic import generate_graphic
from .graphic2 import generate_pie_chart

# Manejo del locale de manera segura
try:
    locale.setlocale(locale.LC_ALL, 'es_PE.UTF-8')  # Cambiado a 'es_PE'
except locale.Error:
    # Puedes manejar el error aquí si el locale no está disponible
    pass

@login_required
def home_view(request):
    direcciones = Proceso.objects.values_list('direccion', flat=True).distinct()

    direccion_seleccionada = request.GET.get('direccion', None)
    if direccion_seleccionada:
        procesos = Proceso.objects.filter(direccion=direccion_seleccionada)
    else:
        direccion_seleccionada = Proceso.objects.values('direccion').annotate(total=Count('id')).order_by('-total').first()['direccion']
        procesos = Proceso.objects.filter(direccion=direccion_seleccionada)
    
    eventos = Evento.objects.filter(proceso__in=procesos).order_by('fecha')

    # Colores y actividades definidos para el gráfico de líneas de tiempo
    colors = {
        'Requerimiento': 'skyblue',
        'Indagación de Mercado': 'orange',
        'Convocatoria': 'green',
        'Firma de contrato': 'purple',
        'Entrega del bien': 'red'
    }
    activities = [
        'Fecha de Requerimiento',
        'Indagación Mercado',
        'Fecha de Convocatoria',
        'Firma Estimada de Contrato',
        'Ingreso Estimado Almacén',
        'Fecha Estimada de Conformidad'
    ]
    max_label_length = len("AUDÍFONOS CON MICRÓFONO PARA LOS")

    # Generar el primer gráfico
    graphic = generate_graphic(procesos, eventos, colors, activities, max_label_length)

    # Generar el gráfico de torta
    procesos_por_direccion = Proceso.objects.values('direccion').annotate(total_procesos=Count('id'), total_previsto=Sum('previsto'))
    graphic2 = generate_pie_chart(procesos_por_direccion)

    context = {
        'graphic': graphic,
        'graphic2': graphic2,
        'direcciones': direcciones,
        'direccion_seleccionada': direccion_seleccionada
    }
    return render(request, 'home.html', context)

@login_required
def proceso_list(request):
    form = ProcesoFilterForm(request.GET)  # Inicializa el formulario con los datos GET
    procesos = Proceso.objects.all()

    # Filtrado basado en los campos del formulario
    if form.is_valid():
        if form.cleaned_data['numero']:
            procesos = procesos.filter(numero=form.cleaned_data['numero'])
        if form.cleaned_data['nombre']:
            procesos = procesos.filter(nombre__icontains=form.cleaned_data['nombre'])
        if form.cleaned_data['previsto']:
            condition = form.cleaned_data.get('previsto_condition')
            if condition == 'gt':  # Si la condición es "Mayor que"
                procesos = procesos.filter(previsto__gt=form.cleaned_data['previsto'])
            elif condition == 'lt':  # Si la condición es "Menor que"
                procesos = procesos.filter(previsto__lt=form.cleaned_data['previsto'])

    # Añadir paginación: 10 elementos por página
    paginator = Paginator(procesos, 10)  # Mostrar 10 elementos por página
    page_number = request.GET.get('page')  # Obtener el número de la página actual
    page_obj = paginator.get_page(page_number)  # Obtener los objetos de la página actual

    context = {
        'form': form,
        'page_obj': page_obj  # Pasar el objeto de la página al contexto
    }
    return render(request, 'pages/proceso_list.html', context)

@login_required
def proceso_detail(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    return render(request, 'pages/proceso_detail.html', {'proceso': proceso})

@login_required
def proceso_create(request):
    if request.method == "POST":
        form = ProcesoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('proceso_list')
    else:
        form = ProcesoForm()
    return render(request, 'pages/proceso_form.html', {'form': form})

@login_required
def proceso_update(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    if request.method == "POST":
        form = ProcesoForm(request.POST, instance=proceso)
        if form.is_valid():
            form.save()
            return redirect('proceso_list')
    else:
        form = ProcesoForm(instance=proceso)
    return render(request, 'pages/proceso_form.html', {'form': form})

@login_required
def proceso_delete(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    if request.method == "POST":
        proceso.delete()
        return redirect('proceso_list')
    return render(request, 'pages/proceso_confirm_delete.html', {'proceso': proceso})

@method_decorator(login_required, name='dispatch')
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'



# Vistas para Eventos
@login_required
def evento_list(request, proceso_id):
    proceso = get_object_or_404(Proceso, id=proceso_id)
    eventos = Evento.objects.filter(proceso=proceso)
    return render(request, 'pages/evento_list.html', {'eventos': eventos, 'proceso': proceso})

@login_required
def evento_detail(request, proceso_id, pk):
    proceso = get_object_or_404(Proceso, id=proceso_id)
    evento = get_object_or_404(Evento, pk=pk, proceso=proceso)
    return render(request, 'pages/evento_detail.html', {'evento': evento, 'proceso': proceso})

@login_required
def evento_create(request, proceso_id):
    proceso = get_object_or_404(Proceso, id=proceso_id)
    if request.method == "POST":
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.proceso = proceso  # Asigna el proceso automáticamente
            evento.save()
            return redirect('evento_list', proceso_id=proceso.id)
    else:
        form = EventoForm()
    return render(request, 'pages/evento_form.html', {'form': form, 'proceso': proceso})

@login_required
def evento_update(request, proceso_id, pk):
    proceso = get_object_or_404(Proceso, id=proceso_id)
    evento = get_object_or_404(Evento, pk=pk, proceso=proceso)
    if request.method == "POST":
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('evento_list', proceso_id=proceso.id)
    else:
        form = EventoForm(instance=evento)
    return render(request, 'pages/evento_form.html', {'form': form, 'evento': evento, 'proceso': proceso})

@login_required
def evento_delete(request, proceso_id, pk):
    proceso = get_object_or_404(Proceso, id=proceso_id)
    evento = get_object_or_404(Evento, pk=pk, proceso=proceso)
    if request.method == "POST":
        evento.delete()
        return redirect('evento_list', proceso_id=proceso.id)
    return render(request, 'pages/evento_confirm_delete.html', {'evento': evento, 'proceso': proceso})

def about_view(request):
    """Vista para la página 'About'."""
    return render(request, 'about.html')