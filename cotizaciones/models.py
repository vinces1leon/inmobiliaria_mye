# cotizaciones/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class Departamento(models.Model):

    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('vendido', 'Vendido'),
        ('separado', 'Separado'),
    ]

    """Modelo para los departamentos disponibles"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    area_m2 = models.DecimalField(max_digits=6, decimal_places=2)
    area_libre = models.DecimalField(max_digits=6, decimal_places=2)
    habitaciones = models.IntegerField()
    banos = models.IntegerField()
    pisos = models.CharField(max_length=50, null=True, blank=True)
    disponible = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    imagen = models.ImageField(upload_to='departamentos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} - S/.{self.precio}"
    
    class Meta:
        ordering = ['codigo']
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'


class Cotizacion(models.Model):
    """Modelo para las cotizaciones"""
    numero_cotizacion = models.CharField(max_length=20, unique=True, editable=False)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cotizaciones', null=True, blank=True)

    # Datos del cliente
    nombre_cliente = models.CharField(max_length=200)
    dni_cliente = models.CharField(max_length=8)
    direccion_cliente = models.CharField(blank=True, null=True)
    distrito_cliente = models.CharField(max_length=100)
    telefono_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(blank=True, null=True)
    cuota_inicial = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Departamento cotizado
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='cotizaciones')
    
    # Información adicional
    observaciones = models.TextField(blank=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(default=timezone.now)
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)

    TIPO_DESCUENTO_CHOICES = [
        ('PORC', 'Porcentaje'),
        ('MONTO', 'Monto')
    ]

    tipo_descuento = models.CharField(
        max_length=5,
        choices=TIPO_DESCUENTO_CHOICES,
        default='PORC'
    )
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    precio_final = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    datos_estaticos = models.JSONField(null=True, blank=True)

    
    def save(self, *args, **kwargs):
        # Generar número de cotización automáticamente
        if not self.numero_cotizacion:
            ultimo = Cotizacion.objects.order_by('-id').first()
            if ultimo:
                numero = int(ultimo.numero_cotizacion.split('_')[1]) + 1 
            else:
                numero = 1
            self.numero_cotizacion = f"cotizacion_{numero:02d}"


        precio_base = self.departamento.precio + 50000

        # Calcular precio final considerando descuento
        if self.tipo_descuento == 'PORC':
            self.precio_final = precio_base - (precio_base * self.valor_descuento / 100)
        else:  # MONTO
            self.precio_final = precio_base - self.valor_descuento

        # Guardar datos estáticos del departamento (con el precio visible)
        if not self.datos_estaticos and self.departamento:
            self.datos_estaticos = {
                "nombre": self.departamento.nombre,
                "codigo": self.departamento.codigo.replace("DEP-", ""),
                "area_m2": f"{self.departamento.area_m2} m²",
                "area_libre": f"{self.departamento.area_libre} m²",
                "precio": f"S/. {float(precio_base):,.2f}",
            }

        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.numero_cotizacion} - {self.nombre_cliente}"
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'


