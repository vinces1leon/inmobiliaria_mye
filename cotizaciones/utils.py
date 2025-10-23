# cotizaciones/utils.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime

def generar_pdf_cotizacion(cotizacion):
    """Genera un PDF para la cotización"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    subtitulo_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    # Título principal
    elements.append(Paragraph("COTIZACIÓN DE DEPARTAMENTO", titulo_style))
    elements.append(Spacer(1, 12))
    
    # Información de la cotización
    info_data = [
        ['N° Cotización:', cotizacion.numero_cotizacion],
        ['Fecha:', cotizacion.fecha_creacion.strftime('%d/%m/%Y %H:%M')],
        ['Asesor:', cotizacion.creado_por.get_full_name() or cotizacion.creado_por.username]
    ]
    
    info_table = Table(info_data, colWidths=[120, 350])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Datos del cliente
    elements.append(Paragraph("DATOS DEL CLIENTE", subtitulo_style))
    
    cliente_data = [
        ['Nombre:', cotizacion.nombre_cliente],
        ['DNI:', cotizacion.dni_cliente],
        ['Dirección:', cotizacion.direccion_cliente],
        ['Teléfono:', cotizacion.telefono_cliente],
    ]
    
    if cotizacion.email_cliente:
        cliente_data.append(['Email:', cotizacion.email_cliente])
    
    cliente_table = Table(cliente_data, colWidths=[120, 350])
    cliente_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(cliente_table)
    elements.append(Spacer(1, 20))
    
    # Datos del departamento
    elements.append(Paragraph("INFORMACIÓN DEL DEPARTAMENTO", subtitulo_style))
    
    depto = cotizacion.departamento
    depto_data = [
        ['Código:', depto.codigo],
        ['Nombre:', depto.nombre],
        ['Piso:', f'{depto.piso}°'],
        ['Área:', f'{depto.area_m2} m²'],
        ['Habitaciones:', str(depto.habitaciones)],
        ['Baños:', str(depto.banos)],
    ]
    
    if depto.descripcion:
        depto_data.append(['Descripción:', depto.descripcion[:100] + '...' if len(depto.descripcion) > 100 else depto.descripcion])
    
    depto_table = Table(depto_data, colWidths=[120, 350])
    depto_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(depto_table)
    elements.append(Spacer(1, 20))
    
    # Resumen de precios
    elements.append(Paragraph("RESUMEN DE INVERSIÓN", subtitulo_style))
    
    precio_data = [
        ['Precio base:', f'S/. {depto.precio:,.2f}'],
    ]
    
    if cotizacion.descuento > 0:
        descuento_monto = depto.precio * cotizacion.descuento / 100
        precio_data.append(['Descuento:', f'- S/. {descuento_monto:,.2f} ({cotizacion.descuento}%)'])
    
    precio_data.append(['', ''])  # Línea vacía
    precio_data.append(['PRECIO FINAL:', f'S/. {cotizacion.precio_final:,.2f}'])
    
    precio_table = Table(precio_data, colWidths=[120, 350])
    precio_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1a5490')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(precio_table)
    
    # Observaciones (si existen)
    if cotizacion.observaciones:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("OBSERVACIONES", subtitulo_style))
        obs_style = ParagraphStyle('Observations', parent=styles['Normal'], fontSize=10)
        elements.append(Paragraph(cotizacion.observaciones, obs_style))
    
    # Nota al pie
    elements.append(Spacer(1, 40))
    nota_style = ParagraphStyle(
        'Note',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        "Esta cotización tiene una validez de 15 días a partir de la fecha de emisión. "
        "Los precios están sujetos a cambios sin previo aviso.",
        nota_style
    ))
    
    # Generar el PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf