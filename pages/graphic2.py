import matplotlib.pyplot as plt
import io
import base64
from decimal import Decimal, InvalidOperation

def format_currency(value):
    return f"{value:,.2f} PEN"

def generate_pie_chart(procesos):
    fig2, ax2 = plt.subplots(figsize=(20, 16))

    mercados = {"Extranjero": 0, "Nacional": 0}
    montos = {"Extranjero": Decimal('0'), "Nacional": Decimal('0')}

    for proceso in procesos:
        nombre = proceso.get('nombre', '')
        estimado = proceso.get('total_estimado')
        
        if nombre:
            mercado = "Extranjero" if nombre.startswith("RE") else "Nacional"
            mercados[mercado] += proceso.get('total_procesos', 1)
            if estimado is not None:
                try:
                    monto_decimal = Decimal(str(estimado))
                    montos[mercado] += monto_decimal
                except (InvalidOperation, ValueError, TypeError) as e:
                    print(f"Error al convertir estimado: {e}")

    etiquetas = []
    for mercado, cantidad in mercados.items():
        monto_formateado = format_currency(float(montos[mercado]))
        etiqueta = f"{mercado}\nProcesos: {cantidad}\nMonto:\n{monto_formateado}"
        etiquetas.append(etiqueta)

    ax2.pie(list(mercados.values()), labels=etiquetas, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 45})
    ax2.axis('equal')

    plt.tight_layout()  # Ajusta automáticamente el diseño

    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png', dpi=300, bbox_inches='tight')
    buffer2.seek(0)
    image_png2 = buffer2.getvalue()
    buffer2.close()

    return base64.b64encode(image_png2).decode('utf-8')
