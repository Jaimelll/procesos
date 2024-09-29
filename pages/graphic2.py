import matplotlib.pyplot as plt
import io
import base64

def format_currency(value):
    return f"{value:,.2f} PEN"

def generate_pie_chart(procesos):
    fig2, ax2 = plt.subplots(figsize=(20, 16))

    mercados = {"Extranjero": 0, "Nacional": 0}
    montos = {"Extranjero": 0, "Nacional": 0}

    for proceso in procesos:
        nombre = proceso.get('nombre') if isinstance(proceso, dict) else getattr(proceso, 'nombre', None)
        estimado = proceso.get('estimado', 0) if isinstance(proceso, dict) else getattr(proceso, 'estimado', 0)
        
        if nombre:
            mercado = "Extranjero" if nombre.startswith("RE") else "Nacional"
            mercados[mercado] += 1
            montos[mercado] += estimado

    etiquetas = [f"{mercado}\nProcesos: {cantidad}\nMonto: {format_currency(montos[mercado])}" 
                 for mercado, cantidad in mercados.items()]

    ax2.pie(list(mercados.values()), labels=etiquetas, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 48})
    ax2.axis('equal')

    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    image_png2 = buffer2.getvalue()
    buffer2.close()

    return base64.b64encode(image_png2).decode('utf-8')
