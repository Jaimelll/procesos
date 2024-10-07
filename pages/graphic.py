import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
from datetime import datetime, date
from django.db.models import OuterRef, Subquery
from .models import Formula, Evento

def generate_graphic(procesos, eventos, colors, activities, max_label_length, mercado_seleccionado='Nacional'):
    # Tamaño del gráfico ajustado para maximizar la altura
    fig, ax = plt.subplots(figsize=(32, 18))  # Aumentado la altura de 16 a 18

    today_date = date.today()

    # Obtener los estados (leyendas) de la tabla Formula, ordenados por el campo 'orden'
    formulas = list(Formula.objects.filter(parametro_id=50).order_by('orden'))
    estados = [formula.nombre for formula in formulas]
    
    # Definir una lista de colores distintivos
    colores_distintivos = [
        '#FFD700', '#FF4500', '#32CD32', '#1E90FF', '#FF1493', 
        '#9400D3', '#FF0000', '#FF8C00', '#00FF00', '#8B4513', 
        '#4169E1', '#FF69B4', '#20B2AA', '#DAA520', '#800080',
    ]

    # Asegurarse de que hay suficientes colores
    while len(colores_distintivos) < len(estados):
        colores_distintivos.extend(colores_distintivos)
    
    # Crear el mapa de colores
    color_map = {formula.cantidad: colores_distintivos[i] for i, formula in enumerate(formulas)}

    # Obtener los acti válidos de la tabla Formula
    acti_validos = Formula.objects.filter(parametro_id=50).values_list('cantidad', flat=True)

    # Separar procesos por mercado y ordenar por nombre
    procesos_por_mercado = {"Nacional": [], "Extranjero": []}
    for proceso in procesos:
        mercado = "Extranjero" if proceso.nombre.startswith("RE") else "Nacional"
        procesos_por_mercado[mercado].append(proceso)
    
    # Ordenar los procesos del mercado seleccionado por nombre
    procesos_ordenados = sorted(procesos_por_mercado[mercado_seleccionado], key=lambda p: p.nombre)

    # Lista para almacenar las etiquetas de los procesos
    proceso_labels = []

    # Procesar solo el mercado seleccionado
    for proceso in procesos_ordenados:
        # Filtrar eventos válidos para este proceso específico
        evento_proceso = eventos.filter(proceso=proceso, acti__in=acti_validos).order_by('fecha')
        if evento_proceso.exists():
            # Crear una paleta de colores específica para este proceso
            acti_proceso = evento_proceso.values_list('acti', flat=True).distinct()
            color_map_proceso = {acti: color_map.get(acti, 'grey') for acti in acti_proceso}

            estado_dates = []
            estado_durations = []
            estado_colors = []
            current_estado = None
            next_color = 'grey'  # Color inicial

            for i, evento in enumerate(evento_proceso):
                formula = Formula.objects.filter(parametro_id=50, cantidad=evento.acti).first()
                if formula:
                    estado = formula.nombre
                    if estado != current_estado:
                        if current_estado is not None:
                            estado_durations.append((evento.fecha - estado_dates[-1]).days)
                            estado_colors.append(next_color)
                        estado_dates.append(evento.fecha)
                        current_estado = estado
                    
                    # Actualizar el color para el próximo estado
                    next_color = color_map_proceso.get(evento.acti, 'grey')

            # Añadir la duración y color del último estado hasta el último evento
            if estado_dates:
                ultimo_evento = evento_proceso.last()
                estado_durations.append((ultimo_evento.fecha - estado_dates[-1]).days)
                estado_colors.append(next_color)

            proceso_label = f"{proceso.nombre} - {proceso.descripcion[:max_label_length]}{'...' if len(proceso.descripcion) > max_label_length else ''}"
            proceso_labels.append(proceso_label)

            ax.barh(
                proceso_label, 
                estado_durations, 
                left=mdates.date2num(estado_dates),
                color=estado_colors
            )

    # Configurar el eje y con las etiquetas ordenadas
    ax.set_yticks(range(len(proceso_labels)))
    ax.set_yticklabels(proceso_labels)
    ax.invert_yaxis()  # Para que el orden sea de arriba a abajo

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

    # Crear la leyenda con los estados de Formula, omitiendo el último y desplazando los nombres
    handles = [plt.Rectangle((0,0),1,1, color=color_map[formula.cantidad]) for formula in formulas[:-1]]
    etiquetas_leyenda = [formulas[i+1].nombre for i in range(len(formulas)-1)]
    
    # Calcular el número de columnas para la primera fila
    num_cols_first_row = (len(handles) + 1) // 2
    
    # Crear la leyenda para 'Fecha Actual' por encima de las otras
    legend_fecha_actual = ax.legend(
        handles=[plt.Line2D([0], [0], color='red', lw=2)],
        labels=['Fecha Actual'],
        loc='lower center',
        bbox_to_anchor=(0.7, -0.17),  # Ajustado para estar más abajo
        ncol=1,
        fontsize=24,
        columnspacing=1,
        handlelength=1.5,
        handleheight=1.5
    )
    ax.add_artist(legend_fecha_actual)

    # Crear dos filas de leyendas para los estados
    legend1 = ax.legend(
        handles=handles[:num_cols_first_row],
        labels=etiquetas_leyenda[:num_cols_first_row],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.23),  # Ajustado para estar más abajo
        ncol=num_cols_first_row,
        fontsize=24,
        columnspacing=1,
        handlelength=1.5,
        handleheight=1.5
    )
    
    legend2 = ax.legend(
        handles=handles[num_cols_first_row:],
        labels=etiquetas_leyenda[num_cols_first_row:],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.30),  # Ajustado para estar más abajo
        ncol=len(handles) - num_cols_first_row,
        fontsize=24,
        columnspacing=1,
        handlelength=1.5,
        handleheight=1.5
    )

    ax.add_artist(legend1)
    ax.add_artist(legend2)

    # Ajustar los márgenes para maximizar el espacio del gráfico
    plt.subplots_adjust(left=0.35, right=0.95, top=0.95, bottom=0.25)  # Ajustado bottom de 0.20 a 0.25

    # Asegurarse de que la etiqueta del eje x esté visible
    ax.set_xlabel('Fecha', fontsize=32, labelpad=15)  # Aumentado labelpad de 10 a 15

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