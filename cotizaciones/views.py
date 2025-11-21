# cotizaciones/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Cotizacion, Departamento
from .forms import LoginForm, CotizacionForm, DepartamentoForm
from .utils import generar_pdf_cotizacion
from datetime import datetime
import os
from io import BytesIO

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

    departamento = None
    precio_mostrado = None

    dept_id = request.GET.get('departamento') or request.POST.get('departamento')

    if dept_id:
        try:
            departamento = Departamento.objects.get(id=dept_id)
            precio_mostrado = departamento.precio + 50000
        except Departamento.DoesNotExist:
            departamento = None

    if request.method == 'POST':
        form = CotizacionForm(request.POST)

        if departamento:
            form.data = form.data.copy()
            form.data["departamento"] = departamento.id

        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.usuario = request.user
            cotizacion.creado_por = request.user
            cotizacion.cuota_inicial = request.POST.get("cuota_inicial")
            cotizacion.save()

            pdf_url = reverse('cotizaciones:ver_pdf', args=[cotizacion.pk])
            lista_url = reverse('cotizaciones:lista_cotizaciones')

            return render(request, 'cotizaciones/nueva_cotizacion.html', {
                'form': CotizacionForm(),
                'pdf_url': pdf_url,
                'lista_url': lista_url,
                'creada': True
            })

        return render(request, 'cotizaciones/nueva_cotizacion.html', {
            'form': form,
            'departamento': departamento,
            'precio_mostrado': precio_mostrado,
        })

    else:
        form = CotizacionForm()

        if departamento:
            form.initial['departamento'] = departamento

    return render(request, 'cotizaciones/nueva_cotizacion.html', {
        'form': form,
        'departamento': departamento,
        'precio_mostrado': precio_mostrado
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
    """Lista de departamentos (con precios personalizados por usuario)"""
    departamentos = Departamento.objects.all().order_by('pisos', 'codigo')
    pisos_range = range(1, 19)

    # Agregar precios personalizados por usuario
    departamentos_info = []
    for depto in departamentos:
        precio_mostrado = depto.precio

        departamentos_info.append({
            'obj': depto,
            'precio_mostrado': precio_mostrado
        })

    # Organizar departamentos por piso (usando la info con precio personalizado)
    departamentos_por_piso = {}
    for piso in pisos_range:
        depts_en_piso = [d for d in departamentos_info if str(d['obj'].pisos) == str(piso)]
        departamentos_por_piso[piso] = depts_en_piso

    return render(request, 'cotizaciones/lista_departamentos.html', {
        'departamentos_por_piso': departamentos_por_piso,
        'pisos_range': pisos_range,
        'es_admin': request.user.is_superuser or request.user.is_staff,
    })


@login_required
def nuevo_departamento(request):
    # Solo admin puede crear departamentos
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'No tienes permisos para crear departamentos.')
        return redirect('cotizaciones:lista_departamentos')
    
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento creado exitosamente.')
            return redirect('cotizaciones:lista_departamentos')
    else:
        form = DepartamentoForm()
        # Pre-llenar el piso si viene en la URL
        piso = request.GET.get('piso')
        if piso:
            form.initial['pisos'] = piso
    
    return render(request, 'cotizaciones/nuevo_departamento.html', {
        'form': form,
        'titulo': 'Nuevo Departamento'
    })

@login_required
def editar_departamento(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)
    es_admin = request.user.is_superuser or request.user.is_staff

    if departamento.estado == 'Vendido' and not es_admin:
        messages.error(request, "No puedes editar un departamento que ya está vendido.")
        return redirect('cotizaciones:lista_departamentos')

    if es_admin:

        precio_mostrado = departamento.precio

        if request.method == 'POST':
            form = DepartamentoForm(request.POST, request.FILES, instance=departamento)
            if form.is_valid():
                form.save()
                messages.success(request, 'Departamento actualizado correctamente.')
                return redirect('cotizaciones:lista_departamentos')
        else:
            form = DepartamentoForm(instance=departamento)

        return render(request, 'cotizaciones/editar_departamento.html', {
            'form': form,
            'departamento': departamento,
            'es_admin': True,
            'precio_mostrado': precio_mostrado,
        })




@login_required
def eliminar_departamento(request, pk):
    """Confirmar y eliminar un departamento con advertencia"""
    departamento = get_object_or_404(Departamento, pk=pk)
    cotizaciones_relacionadas = departamento.cotizaciones.all()

    if request.method == 'POST':
        nombre_departamento = departamento.nombre
        departamento.delete()
        messages.warning(
            request,
            f'Departamento "{nombre_departamento}" y sus cotizaciones asociadas fueron eliminados correctamente.'
        )
        return redirect('cotizaciones:lista_departamentos')

    return render(request, 'cotizaciones/confirmar_eliminar_departamento.html', {
        'departamento': departamento,
        'cotizaciones_relacionadas': cotizaciones_relacionadas
    })

@login_required
def editar_cotizacion(request, pk):
    """Vista para editar una cotización existente"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk, activo=True)
    
    if request.method == 'POST':
        form = CotizacionForm(request.POST, instance=cotizacion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cotización {cotizacion.numero_cotizacion} actualizada exitosamente')
            return redirect('cotizaciones:lista_cotizaciones')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = CotizacionForm(instance=cotizacion)
    
    return render(request, 'cotizaciones/editar_cotizacion.html', {
        'form': form,
        'cotizacion': cotizacion
    })


def ver_pdf(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)

    pdf_buffer = generar_pdf_cotizacion(cotizacion)

    if isinstance(pdf_buffer, bytes):
        pdf_buffer = BytesIO(pdf_buffer)

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="cotizacion_{cotizacion.numero_cotizacion}.pdf"'
    return response


