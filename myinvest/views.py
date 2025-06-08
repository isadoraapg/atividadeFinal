from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import Imovel, Cliente, Notificacao, Corretor, FotoImovel, UserProfile
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from myinvest.forms import ImovelForm, ClienteForm, AnuncioImovelForm
import json

def index(request):
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Garante que o perfil do usuário existe
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
            
            # Verifica o tipo de usuário e redireciona
            if hasattr(user, 'corretor'):
                return redirect('dashboard_corretor')
            elif hasattr(user, 'cliente'):
                return redirect('dashboard_cliente')
            else:
                messages.error(request, 'Usuário não possui perfil de corretor ou cliente.')
                logout(request)
                return redirect('login')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return redirect('login')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Você foi desconectado com sucesso.')
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

@login_required
def dashboard_cliente(request):
    cliente = request.user.cliente
    imoveis_interesse = cliente.imoveis.all()
    notificacoes = Notificacao.objects.filter(usuario=request.user, lida=False)
    
    context = {
        'imoveis_interesse': imoveis_interesse,
        'notificacoes': notificacoes,
    }
    return render(request, 'cliente/dashboard.html', context)

@login_required
def dashboard_corretor(request):
    if not hasattr(request.user, 'corretor'):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    corretor = request.user.corretor
    imoveis = Imovel.objects.filter(corretor=corretor)
    clientes = Cliente.objects.filter(corretor=corretor)
    
    # Filtrar imóveis em obra
    imoveis_em_obra = imoveis.filter(status_obra__in=['fundacao', 'estrutura', 'acabamento'])
    
    context = {
        'imoveis': imoveis,
        'clientes': clientes,
        'imoveis_em_obra': imoveis_em_obra,
    }
    return render(request, 'corretor/dashboard.html', context)

def listar_imoveis(request):
    imoveis = Imovel.objects.filter(disponivel=True)
    
    # Filtros
    localizacao = request.GET.get('localizacao')
    tipo = request.GET.get('tipo')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    quartos = request.GET.get('quartos')
    
    if localizacao:
        imoveis = imoveis.filter(localizacao__icontains=localizacao)
    if tipo:
        imoveis = imoveis.filter(tipo_imovel=tipo)
    if preco_min:
        imoveis = imoveis.filter(preco__gte=preco_min)
    if preco_max:
        imoveis = imoveis.filter(preco__lte=preco_max)
    if quartos:
        imoveis = imoveis.filter(quartos__gte=quartos)
    
    paginator = Paginator(imoveis, 9)
    page = request.GET.get('page')
    imoveis = paginator.get_page(page)
    
    context = {
        'imoveis': imoveis,
        'tipos_imovel': Imovel.TIPO_IMOVEL,
    }
    return render(request, 'imoveis/lista.html', context)

def detalhe_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)
    fotos = imovel.fotos.all()
    cronograma = imovel.cronograma.all().order_by('data_inicio')
    
    context = {
        'imovel': imovel,
        'fotos': fotos,
        'cronograma': cronograma,
    }
    return render(request, 'imoveis/detalhe.html', context)

@login_required
def cadastrar_imovel(request):
    if not hasattr(request.user, 'corretor'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)
        if form.is_valid():
            imovel = form.save(commit=False)
            imovel.corretor = request.user.corretor
            imovel.save()
            
            # Processar múltiplas fotos
            fotos = request.FILES.getlist('fotos')
            for foto in fotos:
                FotoImovel.objects.create(
                    imovel=imovel,
                    imagem=foto
                )
            
            messages.success(request, 'Imóvel cadastrado com sucesso!')
            return redirect('detalhe_imovel', imovel_id=imovel.id)
    else:
        form = ImovelForm()
    
    return render(request, 'corretor/cadastrar_imovel.html', {'form': form})

@login_required
def editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)
    
    if request.user.corretor != imovel.corretor:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imóvel atualizado com sucesso!')
            return redirect('detalhe_imovel', imovel_id=imovel.id)
    else:
        form = ImovelForm(instance=imovel)
    
    return render(request, 'corretor/editar_imovel.html', {'form': form, 'imovel': imovel})

@login_required
def cadastrar_cliente(request):
    if not hasattr(request.user, 'corretor'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.corretor = request.user.corretor
            cliente.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('dashboard_corretor')
    else:
        form = ClienteForm()
    
    return render(request, 'corretor/cadastrar_cliente.html', {'form': form})

@login_required
def atualizar_status_obra(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)
    
    if request.user.corretor != imovel.corretor:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        novo_progresso = request.POST.get('progresso')
        
        if novo_status in dict(Imovel.STATUS_OPCOES):
            imovel.status_obra = novo_status
            imovel.progresso_obra = novo_progresso
            imovel.save()
            
            # Notificar clientes interessados
            for cliente in imovel.clientes.all():
                if cliente.receber_notificacoes:
                    Notificacao.objects.create(
                        usuario=cliente.user,
                        tipo='obra',
                        titulo=f'Atualização na obra: {imovel.titulo}',
                        mensagem=f'A obra do imóvel {imovel.titulo} está em {novo_status}',
                        imovel=imovel
                    )
            
            messages.success(request, 'Status da obra atualizado com sucesso!')
    
    return redirect('detalhe_imovel', imovel_id=imovel.id)

@login_required
def salvar_preferencias(request):
    if request.method == 'POST':
        preferencias = json.loads(request.body)
        cliente = request.user.cliente
        cliente.preferencias = preferencias
        cliente.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def anunciar_imovel(request):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AnuncioImovelForm(request.POST)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.cliente = request.user.cliente
            anuncio.save()
            messages.success(request, 'Anúncio criado com sucesso!')
            return redirect('dashboard_cliente')
    else:
        form = AnuncioImovelForm()
    
    return render(request, 'cliente/anunciar_imovel.html', {'form': form})

@login_required
def notificacoes(request):
    notificacoes = Notificacao.objects.filter(usuario=request.user).order_by('-data_criacao')
    return render(request, 'notificacoes.html', {'notificacoes': notificacoes})

@login_required
def marcar_notificacao_lida(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    notificacao.lida = True
    notificacao.save()
    return redirect('notificacoes')

