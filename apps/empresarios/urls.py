from django.urls import path
from . import views, htmx_views


urlpatterns = [
    path('cadastrar-empresa/', views.cadastrar_empresa, name='cadastrar_empresa' ),
    path('lista-empresas/', views.lista_empresas, name='lista_empresas' ),
    path('ver-empresa/<int:id>/', views.ver_empresa, name='ver_empresa'),
    path('add-doc/<int:id_emp>/', views.add_doc, name='add_doc'),
    path('excluir-doc/<int:id>/', views.excluir_doc, name='excluir_doc'),
    path('add-metrica/<int:id_emp>/', views.add_metrica, name='add_metrica'),
    path('gerenciar_proposta/<int:id_pi>/', views.gerenciar_proposta, name='gerenciar_proposta'),
]

htmx_urlpatterns = [
    path('check-nome-empresa/', htmx_views.check_nome_empresa, name='check_nome_empresa'),
    path('check-cnpj/', htmx_views.check_cnpj, name='check_cnpj'),
    path('check-tempo-decorrido/', htmx_views.check_tempo_decorrido, name='check_tempo_decorrido'),
]

urlpatterns += htmx_urlpatterns
