from flask import Flask, render_template, request, send_file, abort
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
import os

app = Flask(__name__)

BACKEND_URL = os.getenv(
    'BACKEND_URL',
    'http://backend:8000'
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():

    try:

        # Obtener ID factura
        id_factura = request.form['id_factura']

        # Consultar backend
        response = requests.get(
            f'{BACKEND_URL}/facturas/v1/{id_factura}'
        )

        if response.status_code != 200:
            abort(404, description="Factura no encontrada")

        factura = response.json()

        # Crear buffer PDF en memoria
        buffer = BytesIO()

        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm
        )

        # Estilos
        styles = getSampleStyleSheet()

        # Elementos PDF
        elements = []

        # =========================
        # TÍTULO
        # =========================

        titulo = Paragraph(
            f"<b>FACTURA {factura['numero_factura']}</b>",
            styles['Title']
        )

        elements.append(titulo)
        elements.append(Spacer(1, 10))

        # =========================
        # INFORMACIÓN EMPRESA
        # =========================

        empresa = factura['empresa']

        info_empresa = Paragraph(
            f"""
            <b>EMPRESA</b><br/>
            {empresa['nombre']}<br/>
            {empresa['direccion']}<br/>
            {empresa['telefono']}<br/>
            {empresa['email']}
            """,
            styles['BodyText']
        )

        elements.append(info_empresa)
        elements.append(Spacer(1, 10))

        # =========================
        # INFORMACIÓN CLIENTE
        # =========================

        cliente = factura['cliente']

        info_cliente = Paragraph(
            f"""
            <b>CLIENTE</b><br/>
            {cliente['nombre']}<br/>
            {cliente['direccion']}<br/>
            {cliente['telefono']}
            """,
            styles['BodyText']
        )

        elements.append(info_cliente)
        elements.append(Spacer(1, 15))

        # =========================
        # TABLA DETALLE FACTURA
        # =========================

        data = [
            [
                "Cantidad",
                "Descripción",
                "Precio Unitario",
                "Total"
            ]
        ]

        for item in factura['detalle']:

            data.append([
                item['cantidad'],
                item['descripcion'],
                f"${item['precio_unitario']}",
                f"${item['total']}"
            ])

        tabla = Table(
            data,
            colWidths=[30 * mm, 70 * mm, 40 * mm, 40 * mm]
        )

        tabla.setStyle(TableStyle([

            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

            ('GRID', (0, 0), (-1, -1), 1, colors.black),

            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            ('BACKGROUND', (0, 1), (-1, -1), colors.beige)

        ]))

        elements.append(tabla)
        elements.append(Spacer(1, 20))

        # =========================
        # TOTALES
        # =========================

        resumen = Paragraph(
            f"""
            <b>Subtotal:</b> ${factura['subtotal']}<br/>
            <b>Impuesto:</b> ${factura['impuesto']}<br/>
            <b>Total:</b> ${factura['total']}
            """,
            styles['BodyText']
        )

        elements.append(resumen)

        # =========================
        # GENERAR PDF
        # =========================

        doc.build(elements)

        buffer.seek(0)

        # =========================
        # RETORNAR PDF
        # =========================

        return send_file(
            buffer,
            as_attachment=False,
            download_name=f'factura_{id_factura}.pdf',
            mimetype='application/pdf'
        )

    except requests.exceptions.ConnectionError:
        abort(
            503,
            description="Error de conexión con el servidor backend"
        )

    except Exception as e:
        abort(500, description=str(e))


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=3000,
        debug=True
    )