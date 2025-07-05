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
    
    # Processar demonstração de interesse
    if request.method == 'POST' and request.user.is_authenticated and hasattr(request.user, 'cliente'):
        cliente = request.user.cliente
        if imovel not in cliente.imoveis.all():
            cliente.imoveis.add(imovel)
            messages.success(request, f'Interesse demonstrado com sucesso no imóvel "{imovel.titulo}"! O corretor será notificado.')
        else:
            messages.info(request, 'Você já demonstrou interesse neste imóvel.')
        return redirect('detalhe_imovel', imovel_id=imovel.id)
    
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
def excluir_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)
    
    if request.user.corretor != imovel.corretor:
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    if request.method == 'POST':
        # Excluir fotos do imóvel
        for foto in imovel.fotos.all():
            if foto.imagem:
                foto.imagem.delete(save=False)
            foto.delete()
        
        # Excluir o imóvel
        imovel.delete()
        messages.success(request, 'Imóvel excluído com sucesso!')
        return redirect('dashboard_corretor')
    
    return render(request, 'corretor/excluir_imovel.html', {'imovel': imovel})

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
    
    # Redirecionar de volta para a página de onde veio
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        # Fallback para dashboard do cliente ou corretor
        if hasattr(request.user, 'cliente'):
            return redirect('dashboard_cliente')
        elif hasattr(request.user, 'corretor'):
            return redirect('dashboard_corretor')
        else:
            return redirect('home')

@login_required
def detalhes_cliente(request, cliente_id):
    if not hasattr(request.user, 'corretor'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    corretor = request.user.corretor
    
    # Verificar se o cliente pertence ao corretor
    if cliente.corretor != corretor:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_corretor')
    
    context = {
        'cliente': cliente,
        'imoveis_interesse': cliente.imoveis.all(),
        'notificacoes': cliente.user.notificacoes.all().order_by('-data_criacao')[:10],
    }
    return render(request, 'corretor/detalhes_cliente.html', context)

@login_required
def editar_cliente(request, cliente_id):
    if not hasattr(request.user, 'corretor'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    corretor = request.user.corretor
    
    # Verificar se o cliente pertence ao corretor
    if cliente.corretor != corretor:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_corretor')
    
    if request.method == 'POST':
        # Atualizar dados do usuário
        user = cliente.user
        user.first_name = request.POST.get('user.first_name', '')
        user.last_name = request.POST.get('user.last_name', '')
        user.email = request.POST.get('user.email', '')
        user.save()
        
        # Atualizar dados do cliente
        cliente.telefone = request.POST.get('telefone', '')
        cliente.receber_notificacoes = request.POST.get('receber_notificacoes') == 'on'
        cliente.save()
        
        messages.success(request, 'Cliente atualizado com sucesso!')
        return redirect('detalhes_cliente', cliente_id=cliente.id)
    
    return render(request, 'corretor/editar_cliente.html', {'cliente': cliente})

@login_required
def excluir_cliente(request, cliente_id):
    if not hasattr(request.user, 'corretor'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    corretor = request.user.corretor
    
    # Verificar se o cliente pertence ao corretor
    if cliente.corretor != corretor:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard_corretor')
    
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('dashboard_corretor')
    
    return render(request, 'corretor/excluir_cliente.html', {'cliente': cliente})

@login_required
def enviar_imovel_cliente(request, imovel_id):
    if not hasattr(request.user, 'corretor'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    imovel = get_object_or_404(Imovel, id=imovel_id)
    corretor = request.user.corretor
    
    # Verificar se o corretor é responsável pelo imóvel
    if imovel.corretor != corretor:
        messages.error(request, 'Você só pode enviar imóveis que você cadastrou.')
        return redirect('dashboard_corretor')
    
    if request.method == 'POST':
        cliente_destinatario_id = request.POST.get('cliente_id')
        mensagem = request.POST.get('mensagem', '').strip()
        
        try:
            cliente_destinatario = Cliente.objects.get(id=cliente_destinatario_id)
            
            # Verificar se o cliente pertence ao corretor
            if cliente_destinatario.corretor != corretor:
                messages.error(request, 'Você só pode enviar imóveis para seus próprios clientes.')
                return redirect('dashboard_corretor')
            
            # Criar notificação para o cliente destinatário
            titulo = f'🏠 Imóvel recomendado: {imovel.titulo}'
            mensagem_padrao = f'O corretor {corretor.user.get_full_name() or corretor.user.username} recomendou este imóvel para você.\n\n📍 Localização: {imovel.localizacao}\n💰 Preço: R$ {imovel.preco:,.2f}\n🏗️ Status: {imovel.get_status_obra_display()}'
            
            if mensagem:
                mensagem_completa = f"{mensagem_padrao}\n\n💬 Mensagem do corretor:\n{mensagem}"
            else:
                mensagem_completa = mensagem_padrao
            
            Notificacao.objects.create(
                usuario=cliente_destinatario.user,
                tipo='recomendacao',
                titulo=titulo,
                mensagem=mensagem_completa,
                imovel=imovel
            )
            
            messages.success(request, f'Imóvel enviado com sucesso para {cliente_destinatario.user.get_full_name() or cliente_destinatario.user.username}!')
            
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente não encontrado.')
        except Exception as e:
            messages.error(request, 'Erro ao enviar imóvel. Tente novamente.')
    
    return redirect('dashboard_corretor')

