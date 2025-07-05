from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myinvest.models import Cliente, Corretor

class Command(BaseCommand):
    help = 'Adiciona um perfil de cliente a um usuário existente'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome de usuário do usuário que será cliente')
        parser.add_argument('telefone', type=str, help='Telefone do cliente')
        parser.add_argument('corretor_username', type=str, help='Nome de usuário do corretor responsável')

    def handle(self, *args, **options):
        username = options['username']
        telefone = options['telefone']
        corretor_username = options['corretor_username']

        try:
            user = User.objects.get(username=username)
            
            # Verifica se o usuário já é um cliente
            if hasattr(user, 'cliente'):
                self.stdout.write(self.style.ERROR(f'Usuário {username} já é um cliente.'))
                return

            # Busca o corretor
            try:
                corretor_user = User.objects.get(username=corretor_username)
                corretor = Corretor.objects.get(user=corretor_user)
            except (User.DoesNotExist, Corretor.DoesNotExist):
                self.stdout.write(self.style.ERROR(f'Corretor {corretor_username} não encontrado.'))
                return

            # Cria o perfil de cliente
            cliente = Cliente.objects.create(
                user=user,
                telefone=telefone,
                corretor=corretor
            )

            self.stdout.write(self.style.SUCCESS(f'Perfil de cliente criado com sucesso para {username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuário {username} não encontrado.')) 