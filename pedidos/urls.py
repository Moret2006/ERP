from django.urls import path

from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.dashboard_pedidos, name='dashboard'),
    path('novo/', views.criar_pedido, name='criar'),
    path('<int:pk>/', views.detalhar_pedido, name='detalhar'),
    path('<int:pk>/editar/', views.editar_pedido, name='editar'),
    path('<int:pk>/status/', views.alterar_status_pedido, name='alterar_status'),
    path('<int:pk>/cancelar/', views.cancelar_pedido, name='cancelar'),
    path('<int:pk>/excluir/', views.excluir_pedido, name='excluir'),
]
