from django.urls import path

from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.pedidos_list_view, name='list'),
    path('novo/', views.pedido_form_view, name='pedido_create'),
    path('<int:pk>/editar/', views.pedido_form_view, name='pedido_edit'),
    path('clientes/', views.clientes_list_view, name='clientes_list'),
    path('clientes/novo/', views.cliente_form_view, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_form_view, name='cliente_edit'),
    path('produtos/', views.produtos_list_view, name='produtos_list'),
    path('produtos/novo/', views.produto_form_view, name='produto_create'),
    path('produtos/json/', views.produtos_json_view, name='produtos_json'),
    path('produtos/<int:pk>/editar/', views.produto_form_view, name='produto_edit'),
]
