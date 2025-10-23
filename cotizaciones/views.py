# cotizaciones/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from .models import Cotizacion, Departamento
from .forms import LoginForm, CotizacionForm, DepartamentoForm
from .utils import generar_pdf_cotizacion
from datetime import datetime
import os

def login_view(request):
    """Vista para el login de usuarios"""
    if request.user.is_authenticated:
        return redirect('cotizaciones:lista_cotizaciones')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}!')
            return redirect('cotizaciones:lista_cotizaciones')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    
    return render(request, 'cotizaciones/login.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Sesión cerrada exitosamente')
    return redirect('cotizaciones:login')

@login_required
def lista_cotizaciones(request):
    """Vista principal - Lista de cotizaciones"""
    cotizaciones = Cotizacion.objects.filter(activo=True)
    return render(request, 'cotizaciones/lista_cotizaciones.html', {
        'cotizaciones': cotizaciones
    })

@login_required
def nueva_cotizacion(request):
    """Vista para crear una nueva cotización"""
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.creado_por = request.user
            cotizacion.save()
            messages.success(request, f'Cotización {cotizacion.numero_cotizacion} creada exitosamente')
            return redirect('cotizaciones:ver_cotizacion', pk=cotizacion.pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = CotizacionForm()
    
    return render(request, 'cotizaciones/nueva_cotizacion.html', {
        'form': form
    })

@login_required
def ver_cotizacion(request, pk):
    """Vista para ver detalles de una cotización"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk, activo=True)
    return render(request, 'cotizaciones/ver_cotizacion.html', {
        'cotizacion': cotizacion
    })

@login_required
@require_POST
def eliminar_cotizacion(request, pk):
    """Vista para eliminar (desactivar) una cotización"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    cotizacion.activo = False
    cotizacion.save()
    messages.success(request, f'Cotización {cotizacion.numero_cotizacion} eliminada')
    return redirect('cotizaciones:lista_cotizaciones')

@login_required
def descargar_pdf(request, pk):
    """Vista para descargar la cotización en PDF"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk, activo=True)
    
    # Generar el PDF
    pdf_buffer = generar_pdf_cotizacion(cotizacion)
    
    # Crear la respuesta HTTP con el PDF
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    filename = f"cotizacion_{cotizacion.numero_cotizacion}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def imprimir_cotizacion(request, pk):
    """Vista para visualizar la cotización lista para imprimir"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk, activo=True)
    return render(request, 'cotizaciones/imprimir_cotizacion.html', {
        'cotizacion': cotizacion
    })

@login_required
def lista_departamentos(request):
    """Lista de departamentos"""
    departamentos = Departamento.objects.all()
    return render(request, 'cotizaciones/lista_departamentos.html', {
        'departamentos': departamentos
    })

@login_required
def nuevo_departamento(request):
    """Crear nuevo departamento"""
    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento creado exitosamente.')
            return redirect('cotizaciones:lista_departamentos')
        else:
            messages.error(request, 'Por favor, corrija los errores del formulario.')
    else:
        form = DepartamentoForm()
    return render(request, 'cotizaciones/nuevo_departamento.html', {'form': form})

@login_required
def editar_departamento(request, pk):
    """Editar un departamento"""
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento actualizado correctamente.')
            return redirect('cotizaciones:lista_departamentos')
    else:
        form = DepartamentoForm(instance=departamento)
    return render(request, 'cotizaciones/editar_departamento.html', {
        'form': form, 'departamento': departamento
    })

@login_required
def eliminar_departamento(request, pk):
    """Eliminar un departamento"""
    departamento = get_object_or_404(Departamento, pk=pk)
    departamento.delete()
    messages.warning(request, 'Departamento eliminado.')
    return redirect('cotizaciones:lista_departamentos')