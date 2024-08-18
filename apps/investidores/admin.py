from django.contrib import admin
from .models import PropostaInvestimento


class PropostaInvestimentoAdmin(admin.ModelAdmin):
    Model = PropostaInvestimento
    list_display = ['data', 'valor', 'percentual', 'empresa', 'investidor', 'status']

admin.site.register(PropostaInvestimento, PropostaInvestimentoAdmin)
