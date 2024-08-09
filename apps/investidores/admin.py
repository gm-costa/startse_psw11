from django.contrib import admin
from .models import PropostaInvestimento


class PropostaInvestimentoAdmin(admin.ModelAdmin):
    Model = PropostaInvestimento
    list_display = ['valor', 'percentual', 'empresa', 'status']

admin.site.register(PropostaInvestimento, PropostaInvestimentoAdmin)
