from django.urls import path
from . import views


urlpatterns = [
    path('sugestoes/', views.sugestoes, name='sugestoes' ),
]
