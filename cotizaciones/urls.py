# cotizaciones/urls.py

from django.urls import path
from . import views

app_name = 'cotizaciones'

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Cotizaciones
    path('cotizaciones/', views.lista_cotizaciones, name='lista_cotizaciones'),
    path('cotizaciones/nueva/', views.nueva_cotizacion, name='nueva_cotizacion'),
    path('cotizaciones/ver/<int:pk>/', views.ver_cotizacion, name='ver_cotizacion'),
    path('cotizaciones/eliminar/<int:pk>/', views.eliminar_cotizacion, name='eliminar_cotizacion'),
    path('cotizaciones/pdf/<int:pk>/', views.descargar_pdf, name='descargar_pdf'),
    path('cotizaciones/imprimir/<int:pk>/', views.imprimir_cotizacion, name='imprimir_cotizacion'),
    path('cotizaciones/<int:pk>/editar/', views.editar_cotizacion, name='editar_cotizacion'),
    path('ver_pdf/<int:pk>/', views.ver_pdf, name='ver_pdf'),
    path('descargar_pdf/<int:pk>/', views.descargar_pdf, name='descargar_pdf'),
    # Departamentos
    path('departamentos/', views.lista_departamentos, name='lista_departamentos'),
    path('departamentos/nuevo/', views.nuevo_departamento, name='nuevo_departamento'),
    path('departamentos/editar/<int:pk>/', views.editar_departamento, name='editar_departamento'),
    path('departamentos/eliminar/<int:pk>/', views.eliminar_departamento, name='eliminar_departamento'),
]