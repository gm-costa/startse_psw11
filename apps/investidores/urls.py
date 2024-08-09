from django.urls import path
from . import views


urlpatterns = [
    path('sugestoes/', views.sugestoes, name='sugestoes' ),
    path('acessar_empresa/<int:id_emp>/', views.acessar_empresa, name='acessar_empresa'),
    path('realizar_proposta/<int:id_emp>/', views.realizar_proposta, name="realizar_proposta"),

]
