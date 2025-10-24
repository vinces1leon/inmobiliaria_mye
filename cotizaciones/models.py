# cotizaciones/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Departamento(models.Model):
    """Modelo para los departamentos disponibles"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    area_m2 = models.DecimalField(max_digits=6, decimal_places=2)
    habitaciones = models.IntegerField()
    banos = models.IntegerField()
    pisos = models.CharField(max_length=50, null=True, blank=True)
    disponible = models.BooleanField(default=True)
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
    
    # Datos del cliente
    nombre_cliente = models.CharField(max_length=200)
    dni_cliente = models.CharField(max_length=8)
    direccion_cliente = models.CharField(max_length=300)
    telefono_cliente = models.CharField(max_length=15)
    email_cliente = models.EmailField(blank=True, null=True)
    
    # Departamento cotizado
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='cotizaciones')
    
    # Información adicional
    observaciones = models.TextField(blank=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    precio_final = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(default=timezone.now)
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # Generar número de cotización automáticamente
        if not self.numero_cotizacion:
            ultimo = Cotizacion.objects.order_by('-id').first()
            if ultimo:
                numero = int(ultimo.numero_cotizacion.split('_')[1]) + 1
            else:
                numero = 1
            self.numero_cotizacion = f"cotizacion_{numero:02d}"
        
        # Calcular precio final
        self.precio_final = self.departamento.precio - (self.departamento.precio * self.descuento / 100)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero_cotizacion} - {self.nombre_cliente}"
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
