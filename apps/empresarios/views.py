from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from investidores.models import PropostaInvestimento
from .models import Documento, Empresa, Metrica
from brutils import is_valid_cnpj, format_cnpj
import os


@login_required
def cadastrar_empresa(request):
    template_name = 'cadastro_empresa.html'
    context = {
        'areas_atuacoes': Empresa.area_choices,
        'publicos_alvos': Empresa.alvo_choices,
    }
    if request.method == 'POST':
        nome = request.POST.get('nome').strip()
        cnpj = request.POST.get('cnpj').strip()
        site = request.POST.get('site').strip()
        inicio_atividade = request.POST.get('inicio_atividade')
        descricao = request.POST.get('descricao').strip()
        data_final_captacao = request.POST.get('data_final_captacao')
        percentual_equity = request.POST.get('percentual_equity').strip()
        estagio = request.POST.get('estagio')
        area_atuacao = request.POST.get('area_atuacao')
        publico_alvo = request.POST.get('publico_alvo')
        valor_captacao = request.POST.get('valor_captacao')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        request_post = request.POST.dict()
        request_post.pop('csrfmiddlewaretoken')
        print(request_post)
        for k, v in request_post.items():
            context[k] = v

        for k, v in request_post.items():
            if len(v) == 0:
                messages.add_message(request, messages.WARNING, f"Campo '{k}' não informado !")
                return render(request, template_name, context)
        

        if not is_valid_cnpj(cnpj):
            messages.add_message(request, messages.WARNING, 'CNPJ inválido !')
            return render(request, template_name, context)

        try:
            empresa = Empresa(
                user = request.user,
                nome = nome.upper(),
                cnpj = cnpj,
                site = site,
                inicio_atividade = inicio_atividade,
                descricao = descricao,
                data_final_captacao = data_final_captacao,
                percentual_equity = percentual_equity,
                estagio = estagio,
                area = area_atuacao,
                publico_alvo = publico_alvo,
                valor = valor_captacao,
                pitch = pitch,
                logo = logo,
            )
            empresa.save()
        except Exception as e:
            messages.add_message(request, messages.WARNING, f"Não foi possível efetuar o cadastro da empresa.\nErro: {e}")
            return render(request, template_name, context)
        
        messages.add_message(request, messages.SUCCESS, 'Cadastro realizado com sucesso.')
        return redirect(reverse('cadastrar_empresa'))

    return render(request, template_name, context)


@login_required
def lista_empresas(request):
    template_name = 'lista_empresas.html'
    empresas = Empresa.objects.filter(user=request.user)
    busca = request.GET.get('empresa')
    if busca:
        empresas = empresas.filter(nome__icontains=busca)
    context = {'empresas': empresas, 'busca': busca}
    return render(request, template_name, context)


@login_required
def ver_empresa(request, id):
    template_name = 'empresa.html'
    empresa = get_object_or_404(Empresa, id=id)
    if empresa.user != request.user:
        messages.add_message(request, messages.ERROR, "Este empresa não lhe pertence !")
        return redirect(reverse('lista_empresas'))
    
    documentos = Documento.objects.filter(empresa=empresa)
    proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
    proposta_investimentos_enviada = proposta_investimentos.filter(status='PE')

    percentual_vendido = 0
    for pi in proposta_investimentos:
        if pi.status == 'PA':
            percentual_vendido += pi.percentual

    qtd_investidores = proposta_investimentos.filter(status='PA').count()
    total_captado = sum(proposta_investimentos.filter(status='PA').values_list('valor', flat=True))

    valuation_atual = (100 * float(total_captado)) / float(percentual_vendido) if percentual_vendido != 0 else 0

    context = {
        'empresa': empresa, 
        'cnpj': format_cnpj(empresa.cnpj),
        'documentos': documentos,
        'proposta_investimentos_enviada': proposta_investimentos_enviada,
        'percentual_vendido': percentual_vendido,
        'qtd_investidores': qtd_investidores,
        'total_captado': total_captado,
        'valuation_atual': valuation_atual,
    }
    if request.method == "GET":
        return render(request, template_name, context)


@login_required
def add_doc(request, id_emp):
    if get_object_or_404(Empresa, id=id_emp).user != request.user:
        messages.add_message(request, messages.ERROR, 'Você não pode adicionar documento a uma empresa não lhe pertence !')
        return redirect(reverse('lista_empresas'))
    
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')

    if len(titulo.strip()) == 0:
        messages.add_message(request, messages.ERROR, 'Título não informado !')
        return redirect(f'/empresarios/ver-empresa/{id_emp}')

    if not arquivo:
        messages.add_message(request, messages.ERROR, 'Arquivo não escolhido !')
        return redirect(f'/empresarios/ver-empresa/{id_emp}')
    
    extensao = arquivo.name.split('.')
    if extensao[1].lower() != 'pdf':
        messages.add_message(request, messages.ERROR, "Envie apenas PDF's")
        return redirect(f'/empresarios/ver-empresa/{id_emp}')
    
    try:
        documento = Documento(
            empresa_id=id_emp,
            titulo=titulo,
            arquivo=arquivo
        )
        documento.save()
        messages.add_message(request, messages.SUCCESS, 'Arquivo cadastrado com sucesso')
    except Exception as e:
        messages.add_message(request, messages.ERROR, f'Ocorreu um erro: {e}.')
    
    return redirect(f'/empresarios/ver-empresa/{id_emp}')


@login_required
def excluir_doc(request, id):
    documento = get_object_or_404(Documento, id=id)
    if documento.empresa.user != request.user:
        messages.add_message(request, messages.ERROR, 'Esse documento não faz parte de uma empresa que lhe pertence !')
        return redirect(reverse('lista_empresas'))
    
    try:
        path_arquivo = os.path.join(settings.MEDIA_ROOT, str(documento.arquivo))
        documento.delete()
        if os.path.exists(path_arquivo):
            os.remove(path_arquivo)
        messages.add_message(request, messages.SUCCESS, 'Documento excluído com sucesso')
    except Exception as e:
        messages.add_message(request, messages.ERROR, f'Ocorreu erro: {e}')

    return redirect(f'/empresarios/ver-empresa/{documento.empresa.id}')


@login_required
def add_metrica(request, id_emp):
    empresa = get_object_or_404(Empresa, id=id_emp)
    if empresa.user != request.user:
        messages.add_message(request, messages.ERROR, 'Você não pode adicionar métrica a uma empresa não lhe pertence !')
        return redirect(reverse('lista_empresas'))

    titulo = request.POST.get('metrica')
    valor = request.POST.get('valor')

    if len(titulo.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, messages.WARNING, 'Informe título e valor da métrica !')
        return redirect(f'/empresarios/ver-empresa/{id_emp}')
    
    try:
        metrica = Metrica(
            empresa_id=id_emp,
            titulo=titulo.strip(),
            valor=valor
        )
        metrica.save()
        messages.add_message(request, messages.SUCCESS, 'Métrica adicionada com sucesso.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, f'Erro: {e}')

    return redirect(f'/empresarios/ver-empresa/{id_emp}')


@login_required
def gerenciar_proposta(request, id_pi):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id_pi)

    if acao == 'aceitar':
        pi.status = 'PA'
        messages.add_message(request, messages.SUCCESS, 'Proposta aceita.')
    elif acao == 'recusar':
        pi.status = 'PR'
        messages.add_message(request, messages.INFO, 'Proposta recusada !')

    try:
        pi.save()
    except Exception as e:
        messages.add_message(request, messages.ERROR, f'Erro: {e}')

    return redirect(f'/empresarios/ver-empresa/{pi.empresa.id}')
