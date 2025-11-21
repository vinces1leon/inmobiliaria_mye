# cotizaciones/utils.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable
from io import BytesIO
from datetime import datetime, timedelta
from django.templatetags.static import static
from django.conf import settings
import os
import requests
from PIL import Image as PILImage
import json


class LineFlowable(Flowable):
    """Línea horizontal personalizada"""
    def __init__(self, width, height=1):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def __repr__(self):
        return "Line(w=%s)" % self.width

    def draw(self):
        self.canv.setStrokeColor(colors.black)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, self.height, self.width, self.height)

def generar_pdf_cotizacion(cotizacion):
    """Genera un PDF para la cotización estilo MyE Grupo Inmobiliario"""

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_empresa = ParagraphStyle(
        'TituloEmpresa',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        textColor=colors.HexColor('#2c3e50')
    )
    
    titulo_proforma = ParagraphStyle(
        'TituloProforma',
        parent=styles['Normal'],
        fontSize=20,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#8B0000')
    )
    
    numero_proforma = ParagraphStyle(
        'NumeroProforma',
        parent=styles['Normal'],
        fontSize=18,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        textColor=colors.red
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#34495e'),
        spaceAfter=4
    )
    
    normal_style = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica'
    )
    
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica'
    )
    
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    logo = Image(logo_path, width=120, height=70)
    logo_table = Table([[logo]], colWidths=[100])
    logo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    logo_table.hAlign = 'LEFT'
    elements.append(logo_table)

    # ENCABEZADO CON LOGO Y NÚMERO DE PROFORMA
    header_data = [
        [
            Paragraph('<b>MyE Grupo Inmobiliario SAC</b>', titulo_empresa),
            '',
            Paragraph('PROFORMA', titulo_proforma)
        ],
        [
            Paragraph('Construyendo tu Futuro<br/>Dirección del Proyecto: Av. Pío XII 318 San Miguel', small_style),
            '',
            Paragraph(f'N° {cotizacion.numero_cotizacion.replace("cotizacion_", "00")}', numero_proforma)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[10*cm, 2*cm, 6*cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('SPAN', (0, 1), (1, 1)),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    
    # SECCIÓN CLIENTE
    elements.append(Paragraph('<b>CLIENTE</b>', subtitulo_style))
    
    # Datos del cliente en formato de líneas con puntos
    fecha_actual = cotizacion.fecha_creacion.strftime('%d/%m/%Y')
    fecha_vencimiento = (cotizacion.fecha_creacion + timedelta(days=15)).strftime('%d/%m/%Y')
    
    cliente_data = [
        ['Nombre:', cotizacion.nombre_cliente, f'Fecha: {fecha_actual}'],
        ['DNI:', cotizacion.dni_cliente, f'Presupuesto válido hasta: {fecha_vencimiento}'],
        ['Domicilio:', cotizacion.direccion_cliente or '', ''],
        ['Teléfono:', cotizacion.telefono_cliente or '', ''],
        ['E-mail:', cotizacion.email_cliente or '', ''],
        ['Distrito:', cotizacion.distrito_cliente or '', ''],
    ]
    
    bold_style = ParagraphStyle('bold_style', fontName='Helvetica-Bold', fontSize=10)
    normal_style = ParagraphStyle('normal_style', fontName='Helvetica', fontSize=10)

    for row in cliente_data:

        left_text = Paragraph(f"<b>{row[0]}</b> {row[1]}", normal_style)
        right_text = Paragraph(row[2], normal_style)
        data_table = Table(
            [[left_text, right_text]],
            colWidths=[8*cm, 10*cm]
        )
        
        data_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Primera columna a la izquierda
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Segunda columna a la derecha
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(data_table)
    
    
    # --- TABLA DE COTIZACIÓN ---
    depto = cotizacion.departamento
    precio_base_asignado = float(depto.precio) + 500000.0

    if not cotizacion.datos_estaticos:
        datos_estaticos = {
            "nombre": depto.nombre,
            "codigo": depto.codigo.replace("DEP-", ""),
            "area_m2": f"{depto.area_m2} m²",
            "area_libre": f"{depto.area_libre} m²",
            "precio": f"S/. {precio_base_asignado:,.2f}",
        }
        cotizacion.datos_estaticos = datos_estaticos

        try:
            cotizacion.save()
        except Exception:
            pass

    else:
        datos_estaticos = cotizacion.datos_estaticos

    cotizacion_header = ['COTIZACIÓN', 'N°', 'Área techada', 'Área Libre', 'Precio']
    cotizacion_data = [
        cotizacion_header,
        [
            datos_estaticos["nombre"],
            datos_estaticos["codigo"],
            datos_estaticos["area_m2"],
            datos_estaticos["area_libre"],
            datos_estaticos["precio"],
        ]
    ]
    
    cotizacion_table = Table(cotizacion_data, colWidths=[5*cm, 2*cm, 3*cm, 3*cm, 4*cm])
    cotizacion_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Datos
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))
    
    elements.append(cotizacion_table)
    elements.append(Spacer(1, 15))
   
    # Tabla de descuento y precio total
    resumen_data = []

    if cotizacion.tipo_descuento == 'PORC' and cotizacion.valor_descuento > 0:
        descuento_monto = float(precio_base_asignado) * float(cotizacion.valor_descuento) / 100
        resumen_data.append([
            Paragraph(f'<b>Descuento ({cotizacion.valor_descuento}%)</b>', normal_style),
            f'S/. {descuento_monto:,.2f}'
        ])
    elif cotizacion.tipo_descuento == 'MONTO' and cotizacion.valor_descuento > 0:
        resumen_data.append([
            Paragraph('<b>Descuento </b>', normal_style),
            f'S/. {cotizacion.valor_descuento:,.2f}'
        ])

    # Siempre mostrar precio final
    resumen_data.append([
        Paragraph('<b>Precio Total</b>', subtitulo_style),
        f'S/. {cotizacion.precio_final:,.2f}'
    ])
    
    resumen_table = Table(resumen_data, colWidths=[5*cm, 3*cm])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#34495e')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    cuota_inicial = float(cotizacion.cuota_inicial) if cotizacion.cuota_inicial else 0
    separacion = 1500
    saldo_financiar = float(cotizacion.precio_final) - cuota_inicial - separacion

    # FORMA DE PAGO Y RESUMEN DE PRECIOS
    forma_pago_data = [
        [Paragraph('<b>FORMA DE PAGO</b>', subtitulo_style), '', Paragraph('<b>MONTOS</b>', subtitulo_style)],
        ['PRECIO', '', f'S/. {cotizacion.precio_final:,.2f}'],
        ['CUOTA INICIAL', '', f'S/. {cuota_inicial:,.2f}'],
        ['SEPARACIÓN','', f'S/. {separacion:,.2f}'],
        ['SALDO A FINANCIAR', '', f'S/. {saldo_financiar:,.2f}'],
    ]
    
    forma_pago_table = Table(forma_pago_data, colWidths=[6*cm, 0*cm, 3*cm])
    forma_pago_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.grey),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    

    
    # Agregar tablas de forma de pago
    tabla_contenedora = Table(
        [[forma_pago_table, resumen_table]],
        colWidths=[11*cm, 7*cm]  # Ajusta si deseas más o menos espacio
    )

    tabla_contenedora.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Ambas arriba, a la misma altura
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    elements.append(tabla_contenedora)
    elements.append(Spacer(1, 10))
    
    # PROCESO DE COMPRA
    elements.append(Paragraph('<b>PROCESO DE COMPRA:</b>', subtitulo_style))
    proceso_texto = """
    1.- Pago de Separación S/. 1,500.00<br/>
    2.- Aprobación de Crédito<br/>
    3.- Cancelación de Cuota Inicial y firma de minuta<br/>
    4.- Desembolso por parte del Banco del saldo financiado.
    """
    elements.append(Paragraph(proceso_texto, small_style))
    elements.append(Spacer(1, 5))
    
    # INFORMACIÓN DE LA EMPRESA
    empresa_data = [
        ['MyE Grupo Inmobiliario SAC', 'RUC 20604554161'],
        ['Cuenta Corriente BBVA Soles:', '0011-0467-0100005905'],
        ['CCI BBVA Soles:', '011-467-000100005905-83']
    ]
    
    empresa_table = Table(empresa_data, colWidths=[8*cm, 8*cm])
    empresa_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(empresa_table)
    elements.append(Spacer(1, 5))
    
    # NOTAS Y CONDICIONES
    elements.append(Paragraph('<b>Notas y Condiciones:</b>', subtitulo_style))
    notas_texto = """
    1. Luego del pago por concepto de separación, el Cliente tiene 10 días útiles para entregar todos los documentos a la Entidad Financiera<br/>
    2. La Presente proforma no implica reserva del inmueble cotizado<br/>
    3. El Cliente autoriza a la empresa para brindar sus datos de contacto e información para la evaluación de la solicitud de crédito<br/>
    4. En caso de no aprobar el crédito hipotecario, se devolverá el 100% del monto de la Separación.<br/>
    5. La presente proforma tiene una vigencia de 10 días y solo el stock sigue vigente.<br/>
    6. Las imágenes entregadas en material gráfico, departamento, áreas, medios digitales, entre otros son referenciales. Las características del proyecto indicadas en los anexos del contrato de compra y venta.<br/>
    7. Nuestro proyecto cuenta con una edificación sismo resistente que cumple con lo dispuesto en el Reglamento Nacional de Edificaciones y todas las técnicas de la materia.
    """
    elements.append(Paragraph(notas_texto, ParagraphStyle('NotasStyle', parent=small_style, fontSize=8)))
    elements.append(Spacer(1, 5))
    
    # INFORMES
    informes_data = [
        [Paragraph('<b>INFORMES:</b><br/>' +
                  'Caseta de Ventas: Av. Pío XII 318, San Miguel<br/>' +
                  'Horario de Atención: Lun. - Dom. de 10:00am. a 7:00 pm.<br/>' +
                  'Teléfono: 987 615 200<br/>' +
                  'Correo electrónico: ventas@myegrupoinmobiliario.com', small_style)]
    ]
    
    informes_table = Table(informes_data, colWidths=[11*cm], hAlign='LEFT')
    informes_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),      # Borde negro alrededor
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),             # Texto alineado a la izquierda
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),             # Texto arriba del cuadro
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(informes_table)



    depto_image_path = None

    if getattr(depto, 'imagen', None):  # verifica que exista el campo
        try:
            if depto.imagen and hasattr(depto.imagen, 'url'):
                depto_image_path = depto.imagen.url
        except ValueError:
            depto_image_path = None

    c = canvas.Canvas(buffer, pagesize=A4)

    if depto_image_path:
        try:
            response = requests.get(depto_image_path)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                pil_img = PILImage.open(img_data)
                pil_img = pil_img.rotate(90, expand=True)

                rotated_img_data = BytesIO()
                pil_img.save(rotated_img_data, format='PNG')
                rotated_img_data.seek(0)

                depto_image = Image(rotated_img_data, width=550, height=650)  # intercambiamos ancho/alto
                depto_image.hAlign = 'CENTER'
                elements.append(PageBreak())
                elements.append(depto_image)

        except Exception as e:
            print("Error cargando imagen del departamento:", e)

    
    # Generar el PDF 
    doc.build(elements) 
    pdf = buffer.getvalue() 
    buffer.close() 
    return pdf