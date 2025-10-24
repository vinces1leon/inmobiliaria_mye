# cotizaciones/management/commands/crear_usuarios.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decouple import config

class Command(BaseCommand):
    help = 'Crea usuarios del sistema (admin y vendedores)'

    def handle(self, *args, **kwargs):
        # Lista de usuarios a crear
        usuarios = [
            {
                'username': config('ADMIN_USERNAME', default='admin'),
                'email': config('ADMIN_EMAIL', default='admin@grupomye.com'),
                'password': config('ADMIN_PASSWORD', default='Admin123!'),
                'is_superuser': True,
                'is_staff': True,
                'first_name': 'Administrador',
                'last_name': 'Sistema'
            },
            {
                'username': 'vendedor1',
                'email': 'vendedor1@grupomye.com',
                'password': 'Vend123!',
                'is_superuser': False,
                'is_staff': False,  # Sin acceso al admin
                'first_name': 'Vendedor',
                'last_name': 'Uno'
            },
            {
                'username': 'vendedor2',
                'email': 'vendedor2@grupomye.com',
                'password': 'Vend123!',
                'is_superuser': False,
                'is_staff': False,  # Sin acceso al admin
                'first_name': 'Vendedor',
                'last_name': 'Dos'
            },
            # Agrega más vendedores aquí si necesitas
        ]

        for user_data in usuarios:
            username = user_data['username']
            
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Usuario "{username}" ya existe - omitiendo')
                )
                continue
            
            # Crear el usuario
            if user_data.get('is_superuser'):
                user = User.objects.create_superuser(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password']
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password']
                )
                user.is_staff = user_data.get('is_staff', False)
            
            # Asignar nombre y apellido
            user.first_name = user_data.get('first_name', '')
            user.last_name = user_data.get('last_name', '')
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Usuario "{username}" creado exitosamente')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Usuarios del sistema ===')
        )
        for user in User.objects.all():
            tipo = 'ADMIN' if user.is_superuser else 'VENDEDOR'
            self.stdout.write(f'{tipo}: {user.username} - {user.email}')