from django.urls import path
from . import views


urlpatterns = [
    path('sugestoes/', views.sugestoes, name='sugestoes' ),
    path('acessar-empresa/<int:id_emp>/', views.acessar_empresa, name='acessar_empresa'),
    path('realizar-proposta/<int:id_emp>/', views.realizar_proposta, name="realizar_proposta"),
    path('assinar-contrato/<int:id_pi>/', views.assinar_contrato, name='assinar_contrato')
]
