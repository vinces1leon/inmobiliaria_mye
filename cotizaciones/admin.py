# cotizaciones/admin.py

from django.contrib import admin
from .models import Departamento, Cotizacion

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'precio','area_m2', 'area_libre', 'habitaciones', 'banos', 'pisos', 'disponible']
    list_filter = ['disponible', 'habitaciones', 'banos', 'pisos']
    search_fields = ['codigo', 'nombre', 'descripcion']
    list_editable = ['disponible', 'precio']
    ordering = ['codigo']

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['numero_cotizacion', 'nombre_cliente', 'departamento', 'precio_final', 'fecha_creacion', 'creado_por', 'activo']
    list_filter = ['activo', 'fecha_creacion', 'creado_por']
    search_fields = ['numero_cotizacion', 'nombre_cliente', 'dni_cliente']
    readonly_fields = ['numero_cotizacion', 'precio_final', 'fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('departamento', 'creado_por')