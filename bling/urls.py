from django.urls import path

from . import views

app_name = 'bling'

urlpatterns = [
    path('', views.bling_status_view, name='status'),
    path('conectar/', views.bling_connect_view, name='connect'),
    path('callback/', views.bling_callback_view, name='callback'),
]
