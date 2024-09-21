import matplotlib.pyplot as plt
import io
import base64

def format_currency(value):
    try:
        return f"{value:,.2f} PEN"
    except ValueError:
        return f"{value:,.2f} PEN"

def generate_pie_chart(procesos_por_direccion):
    fig2, ax2 = plt.subplots(figsize=(8, 6))

    direcciones = [item['direccion'] for item in procesos_por_direccion]
    cantidades = [item['total_procesos'] for item in procesos_por_direccion]

    etiquetas = [f"{item['direccion']}\nProcesos: {item['total_procesos']}\nMonto: {format_currency(item['total_previsto'])}" for item in procesos_por_direccion]

    ax2.pie(cantidades, labels=etiquetas, autopct='%1.1f%%', startangle=140)
    ax2.axis('equal')

    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    image_png2 = buffer2.getvalue()
    buffer2.close()

    return base64.b64encode(image_png2).decode('utf-8')
