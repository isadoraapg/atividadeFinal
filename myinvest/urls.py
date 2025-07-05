from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('notificacoes/<int:notificacao_id>/marcar-lida/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
    
    # Rotas do Cliente
    path('cliente/dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
    path('cliente/preferencias/', views.salvar_preferencias, name='salvar_preferencias'),
    path('cliente/anunciar/', views.anunciar_imovel, name='anunciar_imovel'),
    
    # Rotas do Corretor
    path('corretor/dashboard/', views.dashboard_corretor, name='dashboard_corretor'),
    path('corretor/imoveis/cadastrar/', views.cadastrar_imovel, name='cadastrar_imovel'),
    path('corretor/imoveis/<int:imovel_id>/editar/', views.editar_imovel, name='editar_imovel'),
    path('corretor/imoveis/<int:imovel_id>/excluir/', views.excluir_imovel, name='excluir_imovel'),
    path('corretor/clientes/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('corretor/clientes/<int:cliente_id>/', views.detalhes_cliente, name='detalhes_cliente'),
    path('corretor/clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('corretor/clientes/<int:cliente_id>/excluir/', views.excluir_cliente, name='excluir_cliente'),
    
    # Rotas de Imóveis
    path('imoveis/', views.listar_imoveis, name='listar_imoveis'),
    path('imoveis/<int:imovel_id>/', views.detalhe_imovel, name='detalhe_imovel'),
    path('imoveis/<int:imovel_id>/status/', views.atualizar_status_obra, name='atualizar_status_obra'),
    path('imoveis/<int:imovel_id>/enviar-cliente/', views.enviar_imovel_cliente, name='enviar_imovel_cliente'),
]