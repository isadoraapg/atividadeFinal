from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Corretor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField("Telefone", max_length=20)
    creci = models.CharField("Número CRECI", max_length=30)
    data_cadastro = models.DateTimeField("Data de Cadastro", default=timezone.now)
    ativo = models.BooleanField("Ativo", default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Imovel(models.Model):
    STATUS_OPCOES = [
        ('planta', 'Na planta'),
        ('fundacao', 'Fundação'),
        ('estrutura', 'Estrutura'),
        ('acabamento', 'Acabamento'),
        ('finalizado', 'Finalizado'),
    ]

    TIPO_IMOVEL = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('comercial', 'Comercial'),
        ('terreno', 'Terreno'),
    ]

    titulo = models.CharField("Título", max_length=100)
    descricao = models.TextField("Descrição")
    localizacao = models.CharField("Localização", max_length=200)
    preco = models.DecimalField("Preço", max_digits=12, decimal_places=2)
    status_obra = models.CharField("Status da Obra", max_length=20, choices=STATUS_OPCOES)
    tipo_imovel = models.CharField("Tipo de Imóvel", max_length=20, choices=TIPO_IMOVEL)
    area_total = models.DecimalField("Área Total (m²)", max_digits=10, decimal_places=2, null=True, blank=True)
    quartos = models.IntegerField("Número de Quartos", default=0)
    banheiros = models.IntegerField("Número de Banheiros", default=0)
    vagas_garagem = models.IntegerField("Vagas de Garagem", default=0)
    progresso_obra = models.IntegerField("Progresso da Obra (%)", 
                                       validators=[MinValueValidator(0), MaxValueValidator(100)],
                                       default=0)
    data_cadastro = models.DateTimeField("Data de Cadastro", default=timezone.now)
    data_previsao_entrega = models.DateField("Previsão de Entrega", null=True, blank=True)
    disponivel = models.BooleanField("Disponível para investimento", default=True)
    corretor = models.ForeignKey(Corretor, on_delete=models.CASCADE, related_name="imoveis")
    anunciado_por_cliente = models.BooleanField("Anunciado por Cliente", default=False)
    cliente_anunciante = models.ForeignKey('Cliente', on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name="imoveis_anunciados")

    def __str__(self):
        return f"{self.titulo} - {self.localizacao}"

class FotoImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name="fotos")
    imagem = models.ImageField("Imagem", upload_to="imoveis_fotos/")
    legenda = models.CharField("Legenda", max_length=100, blank=True)
    principal = models.BooleanField("Foto Principal", default=False)

    def __str__(self):
        return f"Foto de {self.imovel.titulo}"

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField("Telefone", max_length=20, blank=True)
    corretor = models.ForeignKey(Corretor, on_delete=models.CASCADE, related_name="clientes")
    imoveis = models.ManyToManyField(Imovel, related_name='clientes')
    data_cadastro = models.DateTimeField("Data de Cadastro", default=timezone.now)
    preferencias = models.JSONField("Preferências de Busca", default=dict, blank=True)
    receber_notificacoes = models.BooleanField("Receber Notificações", default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Notificacao(models.Model):
    TIPO_NOTIFICACAO = [
        ('obra', 'Atualização de Obra'),
        ('novo_imovel', 'Novo Imóvel'),
        ('status', 'Mudança de Status'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes")
    tipo = models.CharField("Tipo de Notificação", max_length=20, choices=TIPO_NOTIFICACAO)
    titulo = models.CharField("Título", max_length=100)
    mensagem = models.TextField("Mensagem")
    data_criacao = models.DateTimeField("Data de Criação", default=timezone.now)
    lida = models.BooleanField("Lida", default=False)
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

class CronogramaObra(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name="cronograma")
    fase = models.CharField("Fase", max_length=100)
    descricao = models.TextField("Descrição")
    data_inicio = models.DateField("Data de Início")
    data_fim = models.DateField("Data de Término")
    concluido = models.BooleanField("Concluído", default=False)

    def __str__(self):
        return f"{self.fase} - {self.imovel.titulo}"

class AnuncioImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name="anuncios")
    titulo = models.CharField("Título", max_length=100)
    descricao = models.TextField("Descrição")
    data_criacao = models.DateTimeField("Data de Criação", default=timezone.now)
    ativo = models.BooleanField("Ativo", default=True)

    def __str__(self):
        return f"{self.titulo} - {self.imovel.titulo}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def notificacoes_nao_lidas(self):
        return self.user.notificacoes.filter(lida=False).count()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# ... existing code ...