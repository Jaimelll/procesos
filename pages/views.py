from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Proceso, Evento, Parametro, Formula
from .forms import ProcesoForm, CustomUserCreationForm, ProcesoFilterForm, EventoForm, ParametroForm, ParametroFilterForm, FormulaForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Count, Sum, F, Value, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.utils import timezone
from .graphic import generate_graphic, get_market_buttons
from .graphic2 import generate_pie_chart

@login_required
def home_view(request):
    mercados = get_market_buttons()
    mercado_seleccionado = request.GET.get('mercado', 'Nacional')
    
    procesos = Proceso.objects.all()
    eventos = Evento.objects.filter(proceso__in=procesos).order_by('fecha')

    if mercado_seleccionado == 'Extranjero':
        procesos = procesos.filter(nombre__startswith='RE')
    else:
        procesos = procesos.exclude(nombre__startswith='RE')

    # Obtener las actividades (suponiendo que están relacionadas con los eventos)
    activities = eventos.values_list('acti', flat=True).distinct()

    # Definir una longitud máxima para las etiquetas (ajusta según tus necesidades)
    max_label_length = 20

    graphic = generate_graphic(procesos, eventos, mercado_seleccionado, activities, max_label_length)
    procesos_por_nombre = Proceso.objects.values('nombre').annotate(
        total_procesos=Count('id'),
        total_estimado=Sum('estimado')
    )
    print(f"Procesos por nombre: {list(procesos_por_nombre)}")  # Agregar esta línea para depuración
    graphic2 = generate_pie_chart(procesos_por_nombre)

    context = {
        'graphic': graphic,
        'graphic2': graphic2,
        'procesos': procesos,
        'mercados': mercados,
        'mercado_seleccionado': mercado_seleccionado,
    }
    return render(request, 'home.html', context)

@login_required
def proceso_list(request):
    form = ProcesoFilterForm(request.GET)
    procesos = Proceso.objects.all()

    if form.is_valid():
        # Aplicar otros filtros
        if form.cleaned_data.get('nombre'):
            procesos = procesos.filter(nombre__icontains=form.cleaned_data['nombre'])
        if form.cleaned_data.get('descripcion'):
            procesos = procesos.filter(descripcion__icontains=form.cleaned_data['descripcion'])
        if form.cleaned_data.get('estimado') and form.cleaned_data.get('estimado_condition'):
            if form.cleaned_data['estimado_condition'] == 'gt':
                procesos = procesos.filter(estimado__gt=form.cleaned_data['estimado'])
            elif form.cleaned_data['estimado_condition'] == 'lt':
                procesos = procesos.filter(estimado__lt=form.cleaned_data['estimado'])
            elif form.cleaned_data['estimado_condition'] == 'eq':
                procesos = procesos.filter(estimado=form.cleaned_data['estimado'])
        if form.cleaned_data.get('estado'):
            procesos = procesos.filter(estado=form.cleaned_data['estado'])

        # Aplicar filtro de convoca
        convoca = form.cleaned_data.get('convoca')
        if convoca:
            if convoca.orden == 20:
                # Si el orden es 20, no aplicamos ningún filtro (se muestran todos los procesos)
                pass
            else:
                procesos = procesos.filter(convocado=convoca.orden)
        else:
            # Aplicar filtro por defecto si no se ha seleccionado ningún valor
            default_convoca = Formula.objects.filter(parametro_id=11, cantidad=2).first()
            if default_convoca and default_convoca.orden != 20:
                procesos = procesos.filter(convocado=default_convoca.orden)

    # Ordenación
    order_by = request.GET.get('order_by', 'nombre')
    if order_by.startswith('-'):
        procesos = procesos.order_by(F(order_by[1:]).desc(nulls_last=True))
    else:
        procesos = procesos.order_by(F(order_by).asc(nulls_last=True))

    paginator = Paginator(procesos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
        'order_by': order_by,
    }
    return render(request, 'pages/proceso_list.html', context)

@login_required
def proceso_detail(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    periodo = proceso.get_periodo()
    convocado = proceso.get_convocado()
    context = {
        'proceso': proceso,
        'periodo': periodo.nombre if periodo else "No especificado",
        'convocado': convocado.nombre if convocado else "No especificado",
    }
    return render(request, 'pages/proceso_detail.html', context)

@login_required
def proceso_create(request):
    if request.method == "POST":
        form = ProcesoForm(request.POST)
        if form.is_valid():
            proceso = form.save()
            return redirect('proceso_detail', pk=proceso.pk)
    else:
        form = ProcesoForm()
    return render(request, 'pages/proceso_form.html', {'form': form})

@login_required
def proceso_update(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    if request.method == "POST":
        form = ProcesoForm(request.POST, instance=proceso)
        if form.is_valid():
            proceso = form.save()
            return redirect('proceso_detail', pk=proceso.pk)
    else:
        form = ProcesoForm(instance=proceso)
    
    # Asegurarse de que los campos periodo y convocado solo muestren opciones con parametro_id=11
    form.fields['periodo'].queryset = Formula.objects.filter(parametro_id=11)
    form.fields['convocado'].queryset = Formula.objects.filter(parametro_id=11)
    
    context = {
        'form': form,
        'proceso': proceso,
    }
    return render(request, 'pages/proceso_form.html', context)

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
def evento_list(request, proceso_id):
    proceso = get_object_or_404(Proceso, pk=proceso_id)
    order_by = request.GET.get('order_by', 'fecha')  # Default a ordenar por fecha ascendente
    
    eventos = proceso.eventos.all().order_by(order_by)
    
    formulas = Formula.objects.filter(parametro_id=12).order_by('orden')
    
    for evento in eventos:
        formula = formulas.filter(orden=evento.acti).first()
        evento.acti_nombre = formula.nombre if formula else "N/A"
    
    context = {
        'proceso': proceso,
        'eventos': eventos,
        'order_by': order_by,
    }
    return render(request, 'pages/evento_list.html', context)

@login_required
def evento_detail(request, proceso_id, evento_id):
    proceso = get_object_or_404(Proceso, pk=proceso_id)
    evento = get_object_or_404(Evento, pk=evento_id, proceso=proceso)
    formula = Formula.objects.filter(parametro_id=12, orden=evento.acti).first()
    evento.acti_nombre = formula.nombre if formula else "N/A"
    
    context = {
        'proceso': proceso,
        'evento': evento,
    }
    return render(request, 'pages/evento_detail.html', context)

@login_required
def evento_create_update(request, proceso_id, evento_id=None):
    proceso = get_object_or_404(Proceso, pk=proceso_id)
    evento = get_object_or_404(Evento, pk=evento_id, proceso=proceso) if evento_id else None

    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            nuevo_evento = form.save(commit=False)
            nuevo_evento.proceso = proceso
            nuevo_evento.save()
            return redirect('evento_list', proceso_id=proceso.id)
    else:
        form = EventoForm(instance=evento)

    context = {
        'proceso': proceso,
        'evento': evento,
        'form': form,
    }
    return render(request, 'pages/evento_form.html', context)

@login_required
def evento_delete(request, proceso_id, pk):
    proceso = get_object_or_404(Proceso, id=proceso_id)
    evento = get_object_or_404(Evento, pk=pk, proceso=proceso)
    if request.method == "POST":
        evento.delete()
        return redirect('evento_list', proceso_id=proceso.id)
    return render(request, 'pages/evento_confirm_delete.html', {'evento': evento, 'proceso': proceso})

def about_view(request):
    return render(request, 'pages/about.html')

@login_required
def parametro_list(request):
    form = ParametroFilterForm(request.GET)
    parametros = Parametro.objects.all()

    if form.is_valid():
        if form.cleaned_data['nombre']:
            parametros = parametros.filter(nombre__icontains=form.cleaned_data['nombre'])
        if form.cleaned_data['tipo']:
            parametros = parametros.filter(tipo=form.cleaned_data['tipo'])

    paginator = Paginator(parametros, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj
    }
    return render(request, 'pages/parametro_list.html', context)

@login_required
def parametro_detail(request, pk):
    parametro = get_object_or_404(Parametro, pk=pk)
    return render(request, 'pages/parametro_detail.html', {'parametro': parametro})

@login_required
def parametro_create(request):
    if request.method == "POST":
        form = ParametroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('parametro_list')
    else:
        form = ParametroForm()
    return render(request, 'pages/parametro_form.html', {'form': form})

@login_required
def parametro_update(request, pk):
    parametro = get_object_or_404(Parametro, pk=pk)
    if request.method == "POST":
        form = ParametroForm(request.POST, instance=parametro)
        if form.is_valid():
            form.save()
            return redirect('parametro_list')
    else:
        form = ParametroForm(instance=parametro)
    return render(request, 'pages/parametro_form.html', {'form': form})

@login_required
def parametro_delete(request, pk):
    parametro = get_object_or_404(Parametro, pk=pk)
    if request.method == "POST":
        parametro.delete()
        return redirect('parametro_list')
    return render(request, 'pages/parametro_confirm_delete.html', {'parametro': parametro})

@login_required
def formula_list(request, parametro_id):
    parametro = get_object_or_404(Parametro, id=parametro_id)
    formulas = Formula.objects.filter(parametro=parametro)
    return render(request, 'pages/formula_list.html', {'formulas': formulas, 'parametro': parametro})

@login_required
def formula_detail(request, parametro_id, pk):
    parametro = get_object_or_404(Parametro, id=parametro_id)
    formula = get_object_or_404(Formula, pk=pk, parametro=parametro)
    return render(request, 'pages/formula_detail.html', {'formula': formula, 'parametro': parametro})

@login_required
def formula_create(request, parametro_id):
    parametro = get_object_or_404(Parametro, id=parametro_id)
    if request.method == "POST":
        form = FormulaForm(request.POST)
        if form.is_valid():
            formula = form.save(commit=False)
            formula.parametro = parametro
            formula.save()
            return redirect('formula_list', parametro_id=parametro.id)
    else:
        form = FormulaForm()
    return render(request, 'pages/formula_form.html', {'form': form, 'parametro': parametro})

@login_required
def formula_update(request, parametro_id, pk):
    parametro = get_object_or_404(Parametro, id=parametro_id)
    formula = get_object_or_404(Formula, pk=pk, parametro=parametro)
    if request.method == "POST":
        form = FormulaForm(request.POST, instance=formula)
        if form.is_valid():
            form.save()
            return redirect('formula_list', parametro_id=parametro.id)
    else:
        form = FormulaForm(instance=formula)
    return render(request, 'pages/formula_form.html', {'form': form, 'formula': formula, 'parametro': parametro})

@login_required
def formula_delete(request, parametro_id, pk):
    parametro = get_object_or_404(Parametro, id=parametro_id)
    formula = get_object_or_404(Formula, pk=pk, parametro=parametro)
    if request.method == "POST":
        formula.delete()
        return redirect('formula_list', parametro_id=parametro.id)
    return render(request, 'pages/formula_confirm_delete.html', {'formula': formula, 'parametro': parametro})