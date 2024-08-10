from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from empresarios.models import Documento, Empresa
from .models import PropostaInvestimento


@login_required
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

        # TODO: Criar um tipo genérico (M - Mediano)
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


@login_required
def acessar_empresa(request, id_emp):
    template_name = 'acessar_empresa.html'
    empresa = get_object_or_404(Empresa, id=id_emp)
    proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
    percentual_vendido = sum(proposta_investimentos.filter(status='PA').values_list('percentual', flat=True))
    limiar = (80 * empresa.percentual_equity) / 100
    concretizado = False
    if percentual_vendido >= limiar:
        concretizado = True
    percentual_disponivel = empresa.percentual_equity - percentual_vendido

    documentos = Documento.objects.filter(empresa=empresa)
    context = {
        'empresa': empresa,
        'percentual_vendido': percentual_vendido,
        'concretizado': concretizado,
        'percentual_disponivel': percentual_disponivel,
        'documentos': documentos,
    }
    if request.method == 'POST':
        pass
    else:
        return render(request, template_name, context)


@login_required
def realizar_proposta(request, id_emp):
    if request.method == 'POST':
        empresa = get_object_or_404(Empresa, id=id_emp)
        valor = request.POST.get('valor').strip()
        percentual = request.POST.get('percentual').strip()

        if len(valor) == 0 or len(percentual) == 0:
            messages.add_message(request, messages.WARNING, 'Valor e/ou Percentual não informados !')
            return redirect(f'/investidores/acessar-empresa/{id_emp}')

        propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')
        total = 0
        for pa in propostas_aceitas:
            total = total + pa.percentual

        if total + int(percentual)  > empresa.percentual_equity:
            messages.add_message(request, messages.WARNING, 'O percentual solicitado ultrapassa o percentual máximo.')
            return redirect(f'/investidores/acessar-empresa/{id_emp}')

        valuation = (100 * int(valor)) / int(percentual)

        if valuation < (int(empresa.valuation) / 2):
            messages.add_message(request, messages.WARNING, f'Seu valuation proposto foi R$ {valuation} e deve ser no mínimo R$ {empresa.valuation/2}')
            return redirect(f'/investidores/acessar-empresa/{id_emp}')

        try:
            pi = PropostaInvestimento(
                valor = valor,
                percentual = percentual,
                empresa = empresa,
                investidor = request.user,
            )
            pi.save()
        except Exception as e:
            messages.add_message(request, messages.WARNING, f'Erro: {e}')
            return redirect(f'/investidores/acessar-empresa/{id_emp}')

        #messages.add_message(request, messages.SUCCESS, f'Proposta enviada com sucesso')
        return redirect(f'/investidores/assinar-contrato/{pi.id}')


@login_required
def assinar_contrato(request, id_pi):
    template_name = 'assinar_contrato.html'
    pi = get_object_or_404(PropostaInvestimento, id=id_pi)
    if pi.status != "AA":
        raise Http404()
    
    if request.method == "POST":
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')

        if not selfie or not rg:
            messages.add_message(request, messages.WARNING, 'Selfie e/ou RG não informados !')
            return redirect(f'/investidores/assinar-contrato/{id_pi}')

        try:
            pi.selfie = selfie
            pi.rg = rg
            pi.status = 'PE'
            pi.save()
        except Exception as e:
            messages.add_message(request, messages.WARNING, 'Não foi possível assinar o contrato.')
            messages.add_message(request, messages.ERROR, f'Erro: {e}')
            return redirect(f'/investidores/assinar-contrato/{id_pi}')

        messages.add_message(request, messages.SUCCESS, f'Contrato assinado com sucesso, sua proposta foi enviada à empresa.')
        return redirect(f'/investidores/acessar-empresa/{pi.empresa.id}')

    else:
        return render(request, template_name, {'pi': pi})
