from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myinvest.models import Corretor

class Command(BaseCommand):
    help = 'Adiciona um perfil de corretor a um usuário existente'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome de usuário do usuário que será corretor')
        parser.add_argument('telefone', type=str, help='Telefone do corretor')
        parser.add_argument('creci', type=str, help='Número CRECI do corretor')

    def handle(self, *args, **options):
        username = options['username']
        telefone = options['telefone']
        creci = options['creci']

        try:
            user = User.objects.get(username=username)
            
            # Verifica se o usuário já é um corretor
            if hasattr(user, 'corretor'):
                self.stdout.write(self.style.ERROR(f'Usuário {username} já é um corretor.'))
                return

            # Cria o perfil de corretor
            corretor = Corretor.objects.create(
                user=user,
                telefone=telefone,
                creci=creci
            )

            self.stdout.write(self.style.SUCCESS(f'Perfil de corretor criado com sucesso para {username}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuário {username} não encontrado.')) 