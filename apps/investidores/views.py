from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Sum
from django.db.models.functions import TruncDay
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from empresarios.models import Documento, Empresa, Metrica
from .models import PropostaInvestimento
from brutils import format_cnpj


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

        if tipo == 'C':
            empresas = Empresa.objects.filter(inicio_atividade__lte=datetime.today().date() - timedelta(days=1825)).filter(estagio="E") # Mais de 5 anos
        elif tipo == 'D':
            empresas = Empresa.objects.filter(inicio_atividade__gt=datetime.today().date() - timedelta(days=730)).exclude(estagio="E") # Até 2 anos
        elif tipo == 'M':
            empresas = Empresa.objects.filter(inicio_atividade__gt=datetime.today().date() - timedelta(days=1825)).filter(inicio_atividade__lt=datetime.today().date() - timedelta(days=730)).exclude(estagio="E") # De 2 a 5 anos
        
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

    metricas = Metrica.objects.filter(empresa=empresa)
    documentos = Documento.objects.filter(empresa=empresa)

    context = {
        'empresa': empresa,
        'cnpj_formatado': format_cnpj(empresa.cnpj),
        'percentual_vendido': int(percentual_vendido),
        'concretizado': concretizado,
        'percentual_disponivel': percentual_disponivel,
        'metricas': metricas,
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
                data = datetime.today().date(),
                valor = valor,
                percentual = percentual,
                empresa = empresa,
                investidor = request.user,
            )
            pi.save()
        except Exception as e:
            messages.add_message(request, messages.WARNING, f'Erro: {e}')
            return redirect(f'/investidores/acessar-empresa/{id_emp}')

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


@login_required
def lista_propostas(request):
    template_name = 'lista_propostas.html'
    propostas = PropostaInvestimento.objects.filter(empresa__user=request.user).exclude(status='AA')
    busca = request.GET.get('empresa')
    if busca:
        propostas = propostas.filter(empresa__nome__icontains=busca)
    context = {
        'propostas' : propostas,
        'concretizado': True,
        'busca': busca,
    }

    return render(request, template_name, context)


@login_required
def dashboard(request, id_emp):
    template_name = 'dashboard.html'
    empresa = Empresa.objects.get(id=id_emp)
    qtd_dias = request.GET.get('qtd-dias')
    ultimo_dia = request.GET.get('ultimo-dia')

    qtd_dias = 7 if not qtd_dias else int(qtd_dias)

    if ultimo_dia:
        ultimo_dia = datetime.strptime(ultimo_dia, '%Y-%m-%d')
    else:
        ultimo_dia = timezone.now().date()

    sete_dias_atras = ultimo_dia - timedelta(days=qtd_dias - 1)

    '''Forma simples

    propostas_diarias = {}

    for i in range(7):
        dia = sete_dias_atras + timedelta(days=i)

        propostas = PropostaInvestimento.objects.filter(
            empresa=empresa,
            status='PA',
            data=dia
        )

        total_dia = 0
        for proposta in propostas:
            total_dia += proposta.valor
        
        propostas_diarias[dia.strftime('%d/%m/%Y')] = float(total_dia)
    '''

    # Forma mais otimizada e avançada
    propostas_diarias = PropostaInvestimento.objects.filter(
        empresa=empresa,
        status='PA',
        data__range=[sete_dias_atras, ultimo_dia]
    ).values('data').annotate(total=Sum('valor')).order_by('data')

    lista_datas = [datetime.strftime(p['data'], '%d/%m/%Y') for p in propostas_diarias]
    lista_totais = [float(p['total']) for p in propostas_diarias]

    context = {
        'qtd_dias': qtd_dias,
        'ultimo_dia': ultimo_dia,
        # 'labels': list(propostas_diarias.keys()),
        # 'valores': list(propostas_diarias.values()),
        'labels': lista_datas,
        'valores': lista_totais,
    }

    return render(request, template_name, context)
