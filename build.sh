#!/usr/bin/env bash
# build.sh - Script de build para Render

set -o errexit  # Salir si hay errores

echo "=== Instalando dependencias ==="
pip install -r requirements.txt

echo "=== Recolectando archivos estáticos ==="
python manage.py collectstatic --no-input

echo "=== Aplicando migraciones ==="
python manage.py migrate

echo "=== Creando usuarios del sistema ==="
python manage.py crear_usuarios

echo "=== Build completado exitosamente ==="