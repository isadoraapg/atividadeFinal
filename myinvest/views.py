from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from .models import Imovel, Cliente
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def index(request):
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        senha = request.POST['password']
        user = authenticate(request, username=username, password=senha)
        
        if user is not None:
            login(request, user)
            
            # Verifica se é corretor
            if hasattr(user, 'corretor'):
                return redirect('area_corretor')  # Redireciona para área do corretor
            
            # Verifica se é cliente
            elif hasattr(user, 'cliente'):
                return redirect('area_cliente')  # Redireciona para área do cliente
            
            else:
                messages.error(request, 'Usuário sem perfil definido.')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def area_cliente_view(request):
    return render(request, 'cliente/area_cliente.html')

@login_required
def area_corretor_view(request):
    if not hasattr(request.user, 'corretor'):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    return render(request, 'corretor/area_corretor.html')

def lista_clientes_view(request):
    # Mostra todos os imóveis e seus respectivos clientes (sem depender do corretor logado)
    dados = []
    imoveis = Imovel.objects.all()

    for imovel in imoveis:
        clientes = Cliente.objects.filter(imoveis=imovel)
        dados.append((imovel, clientes))

    return render(request, 'corretor/clientes.html', {'dados': dados, 'now': timezone.now()})

# def lista_clientes_view(request):
#     corretor = request.user.corretor  # assumindo que Corretor está relacionado ao User
#     imoveis = Imovel.objects.filter(corretor=corretor)

#     dados = []
#     for imovel in imoveis:
#         clientes = Cliente.objects.filter(imoveis=imovel)
#         dados.append((imovel, clientes))

#     return render(request, 'corretor/clientes.html', {'dados': dados, 'now': timezone.now()})

def adicionar_cliente_view(request):
    return render(request, 'corretor/adicionar_cliente.html')

