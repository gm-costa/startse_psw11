from django.contrib import admin
from .models import Empresa, Documento, Metrica


class MetricaAdmin(admin.ModelAdmin):
    model= Metrica
    list_display = ['titulo', 'valor']

admin.site.register(Empresa)
admin.site.register(Documento)
admin.site.register(Metrica, MetricaAdmin)
