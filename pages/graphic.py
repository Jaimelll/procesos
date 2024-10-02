import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
from datetime import datetime, date

def generate_graphic(procesos, eventos, colors, activities, max_label_length, mercado_seleccionado='Nacional'):
    # Tamaño del gráfico ajustado
    fig, ax = plt.subplots(figsize=(32, 16))  # Ancho 32, altura 16

    start_of_year = date(datetime.now().year, 1, 1)
    today_date = date.today()

    phases = ['Requerimiento', 'Indagación de Mercado', 'Convocatoria', 'Firma de contrato', 'Entrega del bien']

    # Separar procesos por mercado
    procesos_por_mercado = {"Nacional": [], "Extranjero": []}
    for proceso in procesos:
        mercado = "Extranjero" if proceso.nombre.startswith("RE") else "Nacional"
        procesos_por_mercado[mercado].append(proceso)

    # Procesar solo el mercado seleccionado
    for proceso in procesos_por_mercado[mercado_seleccionado]:
        evento_proceso = eventos.filter(proceso=proceso).order_by('fecha')
        if evento_proceso.exists():
            phase_start_dates = []
            phase_durations = []

            start_date = evento_proceso.filter(actividad=activities[0]).first().fecha if evento_proceso.filter(actividad=activities[0]).exists() else start_of_year

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
                            next_available_event = evento_proceso.filter(actividad__in=activities[i+1:]).first()
                            if next_available_event:
                                phase_durations.append((next_available_event.fecha - phase_event.fecha).days)
                            else:
                                phase_durations.append(5)
                    else:
                        phase_start_dates.append(phase_start_dates[-1] if phase_start_dates else start_of_year)
                        phase_durations.append(0)

            proceso_label = f"{proceso.nombre} - {proceso.descripcion[:max_label_length]}{'...' if len(proceso.descripcion) > max_label_length else ''}"

            ax.barh(
                proceso_label, 
                phase_durations, 
                left=mdates.date2num(phase_start_dates),
                color=[colors.get(phase, 'grey') for phase in phases]
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

    # Aumentar el tamaño de los elementos en la leyenda y hacer más gruesos los colores
    ax.legend(
        handles=[plt.Line2D([0], [0], color=color, lw=12) for phase, color in colors.items()] + 
               [plt.Line2D([0], [0], color='red', lw=12)],  # Hacer las líneas de colores más gruesas (12)
        labels=list(colors.keys()) + ['Fecha Actual'],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.35),  # Mover la leyenda más abajo
        ncol=len(colors) + 1,
        fontsize=30  # Tamaño de la fuente de la leyenda (30)
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
