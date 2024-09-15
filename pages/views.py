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

@login_required
def home_view(request):
    procesos = Proceso.objects.all()
    eventos = Evento.objects.all().order_by('fecha')

    # Generar gráfico de líneas de tiempo
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {'Actos preparatorios': 'skyblue', 'Selección': 'orange', 'Etapa contractual': 'green'}
    
    for proceso in procesos:
        evento_proceso = eventos.filter(proceso=proceso).order_by('fecha')
        if evento_proceso.exists():
            start_date = evento_proceso.first().fecha  # Fecha de inicio del primer evento
            phases = ['Actos preparatorios', 'Selección', 'Etapa contractual']
            phase_durations = []
            phase_start_dates = []

            # Calcular las duraciones de las fases
            for i in range(len(phases)):
                phase_start = evento_proceso.filter(actividad=phases[i]).first()
                if phase_start:
                    phase_start = phase_start.fecha
                    phase_start_dates.append((phase_start - start_date).days)
                    if i < len(phases) - 1:
                        next_phase_start = evento_proceso.filter(actividad=phases[i + 1]).first()
                        if next_phase_start:
                            next_phase_start = next_phase_start.fecha
                            phase_durations.append((next_phase_start - phase_start).days)
                        else:
                            phase_durations.append(0)  # Duración por defecto si no hay siguiente fase
                    else:
                        phase_durations.append(5)  # Duración por defecto para la última fase
                else:
                    phase_start_dates.append(0)
                    phase_durations.append(0)

            # Graficar las fases de tiempo solo con etapas conocidas
            ax.barh(
                proceso.nombre, 
                phase_durations, 
                left=phase_start_dates, 
                color=[colors.get(etapa, 'grey') for etapa in phases]  # Usar 'grey' si no se encuentra la clave
            )

    ax.set_xlabel('Días desde el inicio')
   # ax.set_title('Líneas de tiempo de procesos')

    # Mover la leyenda debajo del gráfico, debajo del eje X
    ax.legend(
        handles=[plt.Line2D([0], [0], color=color, lw=4) for phase, color in colors.items()],
        labels=colors.keys(),
        loc='upper center',
        bbox_to_anchor=(0.5, -0.15),  # Ajustar la posición debajo del eje X
        fancybox=True,
        shadow=True,
        ncol=3
    )

    # Guardar gráfico en un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')  # Ajustar el gráfico para incluir la leyenda
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')

    context = {'graphic': graphic}
    return render(request, 'home.html', context)




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
