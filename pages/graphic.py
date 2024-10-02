import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
from datetime import datetime, date
from django.db.models import OuterRef, Subquery
from .models import Formula, Evento

def generate_graphic(procesos, eventos, colors, activities, max_label_length, mercado_seleccionado='Nacional'):
    # Tamaño del gráfico ajustado
    fig, ax = plt.subplots(figsize=(32, 16))  # Ancho 32, altura 16

    today_date = date.today()

    # Obtener los estados (leyendas) de la tabla Formula
    estados = Formula.objects.filter(parametro_id=29).values_list('nombre', flat=True)
    
    # Crear un diccionario de colores para los estados
    color_map = {estado: colors.get(estado, plt.cm.Set3(i/len(estados))) for i, estado in enumerate(estados)}

    # Separar procesos por mercado
    procesos_por_mercado = {"Nacional": [], "Extranjero": []}
    for proceso in procesos:
        mercado = "Extranjero" if proceso.nombre.startswith("RE") else "Nacional"
        procesos_por_mercado[mercado].append(proceso)

    # Procesar solo el mercado seleccionado
    for proceso in procesos_por_mercado[mercado_seleccionado]:
        evento_proceso = eventos.filter(proceso=proceso).order_by('fecha')
        if evento_proceso.exists():
            estado_dates = []
            estado_durations = []
            current_estado = None

            for evento in evento_proceso:
                formula = Formula.objects.filter(parametro_id=29, cantidad=evento.acti).first()
                if formula:
                    estado = formula.nombre
                    if estado != current_estado:
                        if current_estado is not None:
                            estado_durations.append((evento.fecha - estado_dates[-1]).days)
                        estado_dates.append(evento.fecha)
                        current_estado = estado

            # Añadir la duración del último estado hasta el último evento
            if estado_dates:
                ultimo_evento = evento_proceso.last()
                estado_durations.append((ultimo_evento.fecha - estado_dates[-1]).days)

            proceso_label = f"{proceso.nombre} - {proceso.descripcion[:max_label_length]}{'...' if len(proceso.descripcion) > max_label_length else ''}"

            ax.barh(
                proceso_label, 
                estado_durations, 
                left=mdates.date2num(estado_dates),
                color=[color_map.get(Formula.objects.filter(parametro_id=29, cantidad=e.acti).first().nombre, 'grey') if Formula.objects.filter(parametro_id=29, cantidad=e.acti).first() else 'grey' for e in evento_proceso]
            )

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    # Ajustar los márgenes para que las etiquetas del eje y sean visibles
    ax.tick_params(axis='y', labelsize=30)  # Tamaño de la fuente (30)

    # Ajustar el espaciado de los márgenes
    plt.subplots_adjust(left=0.35, right=0.95, top=0.95, bottom=0.25)

    # Mantener las líneas de referencia para los meses
    for month in range(1, 13):
        ax.axvline(x=date(datetime.now().year, month, 1), color='grey', linestyle='--', linewidth=0.5)

    # Asegurar que la línea vertical roja de "Hoy" sea visible
    ax.axvline(x=today_date, color='red', linestyle='-', linewidth=2, label='Fecha Actual')

    plt.xticks(rotation=45, fontsize=24)  # Tamaño de las etiquetas de fecha
    ax.set_xlabel('Fecha', fontsize=32)  # Tamaño del texto del eje x (32)

    # Crear la leyenda con los estados de Formula
    handles = [plt.Rectangle((0,0),1,1, color=color_map[estado]) for estado in estados]
    ax.legend(
        handles=handles + [plt.Line2D([0], [0], color='red', lw=12)],
        labels=list(estados) + ['Fecha Actual'],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.35),
        ncol=len(estados) + 1,
        fontsize=30
    )

    # Guardar el gráfico en un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return base64.b64encode(image_png).decode('utf-8')

# Función para obtener los botones de mercado
def get_market_buttons():
    return ['Nacional', 'Extranjero']
