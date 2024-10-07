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
    
    # Definir una lista de colores distintivos (asegúrate de que haya al menos 13)
    colores_distintivos = [
        '#FF4500', '#FFD700', '#32CD32', '#1E90FF', '#FFD700', 
        '#9400D3', '#FF8C00', '#FF0000', '#00FF00', '#8B4513', 
        '#4169E1', '#FF69B4', '#20B2AA'
    ]

    # Crear el mapa de colores
    color_map = {formula.cantidad: colores_distintivos[i] for i, formula in enumerate(formulas)}

    # Obtener los acti válidos de la tabla Formula
    acti_validos = set(formula.cantidad for formula in formulas)

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
            current_color = 'grey'  # Color inicial

            for i, evento in enumerate(evento_proceso):
                formula = Formula.objects.filter(parametro_id=50, cantidad=evento.acti).first()
                if formula:
                    estado = formula.nombre
                    if estado != current_estado:
                        if current_estado is not None:
                            estado_durations.append((evento.fecha - estado_dates[-1]).days)
                            estado_colors.append(current_color)
                        estado_dates.append(evento.fecha)
                        current_estado = estado
                    
                    # Actualizar el color con el del próximo evento (si existe)
                    if i + 1 < len(evento_proceso):
                        next_evento = evento_proceso[i + 1]
                        current_color = color_map_proceso.get(next_evento.acti, 'grey')
                    else:
                        # Para el último evento, usar su propio color
                        current_color = color_map_proceso.get(evento.acti, 'grey')

            # Añadir la duración y color del último estado hasta el último evento
            if estado_dates:
                ultimo_evento = evento_proceso.last()
                estado_durations.append((ultimo_evento.fecha - estado_dates[-1]).days)
                estado_colors.append(current_color)

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
    linea_hoy = ax.axvline(x=today_date, color='red', linestyle='-', linewidth=2, label='Fecha Actual')

    # Añadir la leyenda para la línea de "Fecha Actual" primero
    legend_hoy = ax.legend([linea_hoy], ['Fecha Actual'], 
              loc='lower center', 
              bbox_to_anchor=(0.5, -0.22),  # Posición ajustada, ahora más arriba
              ncol=1, 
              fontsize=30,
              handlelength=1.5, 
              handleheight=1.5)

    # Crear la leyenda con todos los estados de Formula, ordenados por el campo 'orden', excluyendo el primero
    handles = [plt.Rectangle((0,0),1,1, color=color_map[formula.cantidad]) for formula in formulas[1:]]
    etiquetas_leyenda = [formula.nombre for formula in formulas[1:]]
    
    # Dividir los handles y etiquetas en dos filas
    handles_fila1 = handles[:6]
    handles_fila2 = handles[6:]
    etiquetas_fila1 = etiquetas_leyenda[:6]
    etiquetas_fila2 = etiquetas_leyenda[6:]

    # Crear la leyenda en dos filas
    ax.add_artist(legend_hoy)  # Añadir la leyenda de "Fecha Actual" al gráfico
    legend1 = ax.legend(handles_fila1, etiquetas_fila1, 
              loc='lower center', 
              bbox_to_anchor=(0.5, -0.30),  # Ajustamos la posición vertical
              ncol=6, 
              fontsize=30,
              columnspacing=1, 
              handlelength=1.5, 
              handleheight=1.5)
    
    # Añadir la segunda fila de la leyenda
    ax.add_artist(legend1)
    legend2 = ax.legend(handles_fila2, etiquetas_fila2, 
              loc='lower center', 
              bbox_to_anchor=(0.5, -0.38),  # Ajustamos la posición vertical
              ncol=6, 
              fontsize=30,
              columnspacing=1, 
              handlelength=1.5, 
              handleheight=1.5)

    # Ajustar los márgenes para maximizar el espacio del gráfico y dar espacio a todas las leyendas
    plt.subplots_adjust(left=0.35, right=0.95, top=0.95, bottom=0.40)  # Ajustamos el margen inferior

    # Asegurarse de que la etiqueta del eje x esté visible
    ax.set_xlabel('Fecha', fontsize=32, labelpad=90)  # Ajustamos el labelpad para subir la etiqueta del eje x

    plt.xticks(rotation=45, fontsize=24)  # Tamaño de las etiquetas de fecha
    ax.set_xlabel('Fecha', fontsize=32)  # Tamaño del texto del eje x (32)

    # Guardar el gráfico en un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Añadir una comprobación de colores utilizados
    colores_utilizados = set()
    for proceso in procesos_ordenados:
        evento_proceso = eventos.filter(proceso=proceso, acti__in=acti_validos)
        for evento in evento_proceso:
            color = color_map.get(evento.acti)
            if color:
                colores_utilizados.add(color)
    
    print("Colores utilizados en el gráfico:")
    for color in colores_utilizados:
        print(color)

    # Identificar colores que no deberían estar
    colores_no_esperados = colores_utilizados - set(color_map.values())
    if colores_no_esperados:
        print("Colores no esperados encontrados:")
        for color in colores_no_esperados:
            print(color)
    else:
        print("No se encontraron colores inesperados.")

    return base64.b64encode(image_png).decode('utf-8')

# Función para obtener los botones de mercado
def get_market_buttons():
    return ['Nacional', 'Extranjero']