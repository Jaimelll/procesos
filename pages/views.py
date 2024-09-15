from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Proceso, Evento
from .forms import ProcesoForm, CustomUserCreationForm, ProcesoFilterForm, EventoForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, date, timedelta
import matplotlib.dates as mdates

@login_required
def home_view(request):
    procesos = Proceso.objects.all()
    eventos = Evento.objects.all().order_by('fecha')

    # Generar gráfico de líneas de tiempo
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {
        'Requerimiento': 'skyblue',
        'Indagación de Mercado': 'orange',
        'Convocatoria': 'green',
        'Firma de contrato': 'purple',
        'Entrega del bien': 'red'
    }
    
    # Fecha de referencia: inicio del año (como `date`)
    start_of_year = date(datetime.now().year, 1, 1)
    today_date = date.today()  # Fecha actual

    # Definir las fases y las actividades correspondientes
    phases = ['Requerimiento', 'Indagación de Mercado', 'Convocatoria', 'Firma de contrato', 'Entrega del bien']
    activities = [
        'Fecha de Requerimiento',
        'Indagación Mercado',
        'Fecha de Convocatoria',
        'Firma Estimada de Contrato',
        'Ingreso Estimado Almacén',
        'Fecha Estimada de Conformidad'
    ]

    # Definir la longitud máxima para truncar los nombres de los procesos
    max_label_length = len("AUDÍFONOS CON MICRÓFONO PARA LOS SEHO")

    for proceso in procesos:
        evento_proceso = eventos.filter(proceso=proceso).order_by('fecha')
        if evento_proceso.exists():
            phase_start_dates = []
            phase_durations = []

            # Inicializar la fecha de inicio
            start_date = evento_proceso.filter(actividad=activities[0]).first().fecha if evento_proceso.filter(actividad=activities[0]).exists() else start_of_year

            # Calcular las duraciones de las fases
            for i in range(len(phases)):
                current_activity = activities[i]
                next_activity = activities[i + 1] if i + 1 < len(activities) else None
                
                phase_event = evento_proceso.filter(actividad=current_activity).first()
                
                if phase_event:
                    phase_start = phase_event.fecha
                    phase_start_dates.append(phase_start)

                    if next_activity:
                        next_phase_event = evento_proceso.filter(actividad=next_activity).first()
                        if next_phase_event:
                            phase_durations.append((next_phase_event.fecha - phase_event.fecha).days)
                        else:
                            phase_durations.append(5)  # Duración por defecto si no existe la siguiente fase
                    else:
                        phase_durations.append(5)  # Duración por defecto para la última fase
                else:
                    phase_start_dates.append(phase_start_dates[-1] if phase_start_dates else start_of_year)
                    phase_durations.append(0)

            # Truncar el nombre del proceso y agregar el número
            proceso_label = f"{proceso.numero} - {proceso.nombre[:max_label_length]}{'...' if len(proceso.nombre) > max_label_length else ''}"

            # Graficar las fases de tiempo solo con etapas conocidas
            ax.barh(
                proceso_label, 
                phase_durations, 
                left=mdates.date2num(phase_start_dates),  # Convertir fechas a números para matplotlib
                color=[colors.get(phase, 'grey') for phase in phases]
            )

    # Configuración del eje x para mostrar fechas
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # Ubicar una línea en cada mes
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))  # Formato de fecha (día-mes)

    # Reducir aún más el tamaño de la fuente de las etiquetas del eje y
    ax.tick_params(axis='y', labelsize=7)

    # Ajustar los márgenes para que haya más espacio para los nombres y la leyenda
    plt.subplots_adjust(left=0.35, right=0.95, bottom=0.2)  # Ajustar el espacio izquierdo, derecho, y el inferior del gráfico

    # Agregar líneas verticales para cada mes
    for month in range(1, 13):
        ax.axvline(x=date(datetime.now().year, month, 1), color='grey', linestyle='--', linewidth=0.5)

    # Línea vertical para la fecha actual
    ax.axvline(x=today_date, color='red', linestyle='-', linewidth=1.5, label='Fecha Actual')

    # Rotar las etiquetas de fechas para mayor legibilidad
    plt.xticks(rotation=45)

    ax.set_xlabel('Fecha')
    ax.set_title('Líneas de tiempo de procesos')
    
    # Agregar leyenda en la parte inferior
    ax.legend(
        handles=[plt.Line2D([0], [0], color=color, lw=4) for phase, color in colors.items()] + 
               [plt.Line2D([0], [0], color='red', lw=1.5)],  # Agregar línea de leyenda para la fecha actual
        labels=list(colors.keys()) + ['Fecha Actual'],
        loc='lower center',  # Colocar la leyenda en la parte inferior
        bbox_to_anchor=(0.5, -0.3),  # Ajustar la posición de la leyenda
        ncol=len(colors) + 1  # Mostrar todas las leyendas en una fila
    )

    # Guardar gráfico en un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    context = {'graphic': graphic}
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
        if form.cleaned_data['descripcion']:
            procesos = procesos.filter(descripcion__icontains=form.cleaned_data['descripcion'])

    context = {
        'form': form,
        'procesos': procesos
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
