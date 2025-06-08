from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Corretor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField("Telefone", max_length=20)
    creci = models.CharField("Número CRECI", max_length=30)


    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Imovel(models.Model):
    STATUS_OPCOES = [
        ('planta', 'Na planta'),
        ('construcao', 'Em construção'),
        ('finalizado', 'Finalizado'),
    ]

    titulo = models.CharField("Título", max_length=100)
    descricao = models.TextField("Descrição")
    localizacao = models.CharField("Localização", max_length=200)
    preco = models.DecimalField("Preço", max_digits=12, decimal_places=2)
    status_obra = models.CharField("Status da Obra", max_length=20, choices=STATUS_OPCOES)
    data_cadastro = models.DateTimeField("Data de Cadastro", default=timezone.now)
    disponivel = models.BooleanField("Disponível para investimento", default=True)
    
    corretor = models.ForeignKey(Corretor, on_delete=models.CASCADE, related_name="imoveis")

    def __str__(self):
        return f"{self.titulo} - {self.localizacao}"
    
class FotoImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name="fotos")
    imagem = models.ImageField("Imagem", upload_to="imoveis_fotos/")

    def __str__(self):
        return f"Foto de {self.imovel.titulo}"

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField("Telefone", max_length=20, blank=True)
    corretor = models.ForeignKey(Corretor, on_delete=models.CASCADE, related_name="clientes")
    imoveis = models.ManyToManyField(Imovel, related_name='clientes')

    def __str__(self):
        return self.user.get_full_name() or self.user.username