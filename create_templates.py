# create_templates.py
# Guarda este archivo en la carpeta inmobiliaria_project y ejecútalo

import os

# Definir la ruta base
base_path = 'cotizaciones/templates/cotizaciones'

# Crear las carpetas si no existen
os.makedirs(base_path, exist_ok=True)

# Contenido de los templates
templates = {
    'login.html': '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar Sesión - Sistema de Cotizaciones</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 2rem;
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header i {
            font-size: 3rem;
            color: #667eea;
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 0.75rem;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-header">
            <i class="bi bi-building"></i>
            <h3 class="mt-3">Sistema de Cotizaciones</h3>
            <p class="text-muted">Inmobiliaria</p>
        </div>
        
        {% if messages %}
            {% for message in messages %}
            <div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            
            {% if form.non_field_errors %}
            <div class="alert alert-danger">
                {{ form.non_field_errors }}
            </div>
            {% endif %}
            
            <div class="mb-3">
                <label for="{{ form.username.id_for_label }}" class="form-label">
                    <i class="bi bi-person"></i> Usuario
                </label>
                {{ form.username }}
                {% if form.username.errors %}
                    <div class="text-danger small">{{ form.username.errors }}</div>
                {% endif %}
            </div>
            
            <div class="mb-4">
                <label for="{{ form.password.id_for_label }}" class="form-label">
                    <i class="bi bi-lock"></i> Contraseña
                </label>
                {{ form.password }}
                {% if form.password.errors %}
                    <div class="text-danger small">{{ form.password.errors }}</div>
                {% endif %}
            </div>
            
            <button type="submit" class="btn btn-login w-100">
                <i class="bi bi-box-arrow-in-right"></i> Iniciar Sesión
            </button>
        </form>
        
        <div class="text-center mt-3">
            <small class="text-muted">
                Solo personal autorizado
            </small>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'base.html': '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Sistema de Cotizaciones - Inmobiliaria{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    
    {% load static %}
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    {% if user.is_authenticated %}
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'cotizaciones:lista_cotizaciones' %}">
                <i class="bi bi-building"></i> Inmobiliaria - Cotizaciones
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'cotizaciones:lista_cotizaciones' %}">
                            <i class="bi bi-list-ul"></i> Cotizaciones
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'cotizaciones:nueva_cotizacion' %}">
                            <i class="bi bi-plus-circle"></i> Nueva Cotización
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="bi bi-person-circle"></i> {{ user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/admin/" target="_blank">
                                <i class="bi bi-gear"></i> Administración
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'cotizaciones:logout' %}">
                                <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
                            </a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}
    
    <!-- Messages -->
    {% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <!-- Content -->
    <main class="py-4">
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-light text-center py-3 mt-auto">
        <div class="container">
            <small class="text-muted">
                Sistema de Cotizaciones © {% now "Y" %} - Inmobiliaria
            </small>
        </div>
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>''',

    'lista_cotizaciones.html': '''{% extends 'cotizaciones/base.html' %}

{% block title %}Lista de Cotizaciones - Sistema{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-list-ul"></i> Cotizaciones Registradas</h2>
            <a href="{% url 'cotizaciones:nueva_cotizacion' %}" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Nueva Cotización
            </a>
        </div>
        
        {% if cotizaciones %}
        <div class="card shadow-sm">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>N° Cotización</th>
                                <th>Cliente</th>
                                <th>DNI</th>
                                <th>Departamento</th>
                                <th>Precio Final</th>
                                <th>Fecha</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cotizacion in cotizaciones %}
                            <tr>
                                <td>
                                    <span class="badge bg-info">{{ cotizacion.numero_cotizacion }}</span>
                                </td>
                                <td>{{ cotizacion.nombre_cliente }}</td>
                                <td>{{ cotizacion.dni_cliente }}</td>
                                <td>{{ cotizacion.departamento.codigo }} - {{ cotizacion.departamento.nombre }}</td>
                                <td>
                                    <strong>S/. {{ cotizacion.precio_final|floatformat:2 }}</strong>
                                    {% if cotizacion.descuento > 0 %}
                                        <br><small class="text-success">{{ cotizacion.descuento }}% desc.</small>
                                    {% endif %}
                                </td>
                                <td>
                                    {{ cotizacion.fecha_creacion|date:"d/m/Y" }}<br>
                                    <small class="text-muted">{{ cotizacion.fecha_creacion|time:"H:i" }}</small>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="{% url 'cotizaciones:ver_cotizacion' cotizacion.pk %}" 
                                           class="btn btn-outline-primary" title="Ver detalles">
                                            <i class="bi bi-eye"></i>
                                        </a>
                                        <a href="{% url 'cotizaciones:descargar_pdf' cotizacion.pk %}" 
                                           class="btn btn-outline-success" title="Descargar PDF">
                                            <i class="bi bi-file-pdf"></i>
                                        </a>
                                        <a href="{% url 'cotizaciones:imprimir_cotizacion' cotizacion.pk %}" 
                                           target="_blank" class="btn btn-outline-info" title="Imprimir">
                                            <i class="bi bi-printer"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger" 
                                                onclick="confirmarEliminar({{ cotizacion.pk }}, '{{ cotizacion.numero_cotizacion }}')"
                                                title="Eliminar">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% else %}
        <div class="alert alert-info text-center">
            <i class="bi bi-info-circle"></i> No hay cotizaciones registradas.
            <a href="{% url 'cotizaciones:nueva_cotizacion' %}" class="alert-link">
                Crear primera cotización
            </a>
        </div>
        {% endif %}
    </div>
</div>

<!-- Modal de confirmación -->
<div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirmar Eliminación</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                ¿Está seguro de eliminar la cotización <strong id="cotizacionNumero"></strong>?
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <form id="deleteForm" method="post" style="display: inline;">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
function confirmarEliminar(id, numero) {
    document.getElementById('cotizacionNumero').textContent = numero;
    document.getElementById('deleteForm').action = "{% url 'cotizaciones:eliminar_cotizacion' 0 %}".replace('0', id);
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}
</script>
{% endblock %}''',

    'nueva_cotizacion.html': '''{% extends 'cotizaciones/base.html' %}

{% block title %}Nueva Cotización - Sistema{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="bi bi-plus-circle"></i> Nueva Cotización</h4>
            </div>
            <div class="card-body">
                <form method="post" novalidate>
                    {% csrf_token %}
                    
                    <h5 class="mb-3 text-secondary">Datos del Cliente</h5>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="{{ form.nombre_cliente.id_for_label }}" class="form-label">
                                {{ form.nombre_cliente.label }} <span class="text-danger">*</span>
                            </label>
                            {{ form.nombre_cliente }}
                            {% if form.nombre_cliente.errors %}
                                <div class="text-danger small">{{ form.nombre_cliente.errors }}</div>
                            {% endif %}
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label for="{{ form.dni_cliente.id_for_label }}" class="form-label">
                                {{ form.dni_cliente.label }} <span class="text-danger">*</span>
                            </label>
                            {{ form.dni_cliente }}
                            {% if form.dni_cliente.errors %}
                                <div class="text-danger small">{{ form.dni_cliente.errors }}</div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-12 mb-3">
                            <label for="{{ form.direccion_cliente.id_for_label }}" class="form-label">
                                {{ form.direccion_cliente.label }} <span class="text-danger">*</span>
                            </label>
                            {{ form.direccion_cliente }}
                            {% if form.direccion_cliente.errors %}
                                <div class="text-danger small">{{ form.direccion_cliente.errors }}</div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="{{ form.telefono_cliente.id_for_label }}" class="form-label">
                                {{ form.telefono_cliente.label }} <span class="text-danger">*</span>
                            </label>
                            {{ form.telefono_cliente }}
                            {% if form.telefono_cliente.errors %}
                                <div class="text-danger small">{{ form.telefono_cliente.errors }}</div>
                            {% endif %}
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label for="{{ form.email_cliente.id_for_label }}" class="form-label">
                                {{ form.email_cliente.label }}
                            </label>
                            {{ form.email_cliente }}
                            {% if form.email_cliente.errors %}
                                <div class="text-danger small">{{ form.email_cliente.errors }}</div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <hr>
                    
                    <h5 class="mb-3 text-secondary">Información de la Cotización</h5>
                    
                    <div class="row">
                        <div class="col-md-8 mb-3">
                            <label for="{{ form.departamento.id_for_label }}" class="form-label">
                                {{ form.departamento.label }} <span class="text-danger">*</span>
                            </label>
                            {{ form.departamento }}
                            {% if form.departamento.errors %}
                                <div class="text-danger small">{{ form.departamento.errors }}</div>
                            {% endif %}
                        </div>
                        
                        <div class="col-md-4 mb-3">
                            <label for="{{ form.descuento.id_for_label }}" class="form-label">
                                {{ form.descuento.label }}
                            </label>
                            <div class="input-group">
                                {{ form.descuento }}
                                <span class="input-group-text">%</span>
                            </div>
                            {% if form.descuento.errors %}
                                <div class="text-danger small">{{ form.descuento.errors }}</div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.observaciones.id_for_label }}" class="form-label">
                            {{ form.observaciones.label }}
                        </label>
                        {{ form.observaciones }}
                        {% if form.observaciones.errors %}
                            <div class="text-danger small">{{ form.observaciones.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="d-flex justify-content-end gap-2">
                        <a href="{% url 'cotizaciones:lista_cotizaciones' %}" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Guardar Cotización
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'ver_cotizacion.html': '''{% extends 'cotizaciones/base.html' %}

{% block title %}Cotización {{ cotizacion.numero_cotizacion }} - Sistema{% endblock %}

{% block content %}
<div class="row">
    <div class="col-lg-10 mx-auto">
        <div class="card shadow">
            <div class="card-header bg-info text-white">
                <div class="d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">
                        <i class="bi bi-file-text"></i> Cotización {{ cotizacion.numero_cotizacion }}
                    </h4>
                    <div>
                        <a href="{% url 'cotizaciones:descargar_pdf' cotizacion.pk %}" class="btn btn-light btn-sm">
                            <i class="bi bi-download"></i> PDF
                        </a>
                        <a href="{% url 'cotizaciones:imprimir_cotizacion' cotizacion.pk %}" 
                           target="_blank" class="btn btn-light btn-sm">
                            <i class="bi bi-printer"></i> Imprimir
                        </a>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <p>Detalles de la cotización...</p>
                <a href="{% url 'cotizaciones:lista_cotizaciones' %}" class="btn btn-secondary">Volver</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'imprimir_cotizacion.html': '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Imprimir Cotización</title>
</head>
<body>
    <h1>Cotización para imprimir</h1>
    <p>Contenido de la cotización...</p>
</body>
</html>'''
}

# Crear los archivos
for filename, content in templates.items():
    filepath = os.path.join(base_path, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Creado: {filepath}")

print("\n¡Todos los templates han sido creados exitosamente!")
print("Ahora puedes ejecutar: python manage.py runserver")