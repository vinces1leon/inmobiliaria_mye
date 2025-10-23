# cotizaciones/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Cotizacion, Departamento

class LoginForm(AuthenticationForm):
    """Formulario personalizado para el login"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

class CotizacionForm(forms.ModelForm):
    """Formulario para crear/editar cotizaciones"""
    
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.filter(disponible=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Departamento preferido',
        empty_label='-- Seleccione un departamento --'
    )
    
    class Meta:
        model = Cotizacion
        fields = [
            'nombre_cliente', 
            'dni_cliente', 
            'direccion_cliente', 
            'telefono_cliente',
            'email_cliente',
            'departamento',
            'observaciones',
            'descuento'
        ]
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del cliente'
            }),
            'dni_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DNI',
                'maxlength': '8',
                'pattern': '[0-9]{8}'
            }),
            'direccion_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'telefono_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'email_cliente': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (opcional)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': '0.00'
            })
        }
        labels = {
            'nombre_cliente': 'Nombre del Cliente',
            'dni_cliente': 'DNI',
            'direccion_cliente': 'Dirección',
            'telefono_cliente': 'Teléfono',
            'email_cliente': 'Email',
            'observaciones': 'Observaciones',
            'descuento': 'Descuento (%)'
        }
    
    def clean_dni_cliente(self):
        dni = self.cleaned_data.get('dni_cliente')
        if not dni.isdigit() or len(dni) != 8:
            raise forms.ValidationError('El DNI debe contener exactamente 8 dígitos.')
        return dni

class DepartamentoForm(forms.ModelForm):
    """Formulario para crear y editar departamentos"""
    class Meta:
        model = Departamento
        fields = [
            'codigo', 'nombre', 'descripcion', 'precio', 'area_m2',
            'habitaciones', 'banos', 'piso', 'disponible'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'area_m2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control'}),
            'banos': forms.NumberInput(attrs={'class': 'form-control'}),
            'pisos': forms.TextInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
