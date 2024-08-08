from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import render
from empresarios.models import Empresa


def sugestoes(request):
    template_name = 'sugestoes.html'
    areas = Empresa.area_choices
    context = {'areas': areas}
    if request.method == "POST":
        tipo = request.POST.get('tipo')
        areas_post = request.POST.getlist('area')
        valor = request.POST.get('valor')

        context['tipo'] = tipo
        context['areas_post'] = areas_post
        context['valor'] = valor

        if len(areas_post) == 0 or len(valor) == 0:
            messages.add_message(request, messages.WARNING, 'Área e/ou valor não informados !')
            return render(request, template_name, context)

        if tipo == 'C':
            empresas = Empresa.objects.filter(inicio_atividade__lte=datetime.today().date() - timedelta(days=1825)).filter(estagio="E")
        elif tipo == 'D':
            empresas = Empresa.objects.filter(inicio_atividade__gt=datetime.today().date() - timedelta(days=1825)).exclude(estagio="E")
        
        empresas = empresas.filter(area__in=areas_post)
        
        empresas_selecionadas = []
        for empresa in empresas:
            percentual = (float(valor) * 100) / float(empresa.valuation)
            if percentual >= 1:
                empresas_selecionadas.append(empresa)

        if not empresas_selecionadas:
            messages.add_message(request, messages.WARNING, 'Nenhuma empresa atende aos critérios informados !')
            return render(request, template_name, context)

        context['empresas'] = empresas_selecionadas

        return render(request, template_name, context)

    else:
        return render(request, template_name, context)
