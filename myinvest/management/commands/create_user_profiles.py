from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myinvest.models import UserProfile

class Command(BaseCommand):
    help = 'Cria perfis de usuário para todos os usuários existentes'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write(f'Perfil criado para o usuário {user.username}') 