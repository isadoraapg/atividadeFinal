from django.urls import path
from .views import lista_clientes_view, adicionar_cliente_view, index, area_cliente_view, login_view, logout_view, area_corretor_view

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('corretor/', area_corretor_view, name='area_corretor'),
    path('corretor/clientes/', lista_clientes_view, name='clientes_corretor'),
    path('corretor/clientes/adicionar/', adicionar_cliente_view, name='adicionar_cliente'),
    path('cliente/area/', area_cliente_view, name='area_cliente'),

]