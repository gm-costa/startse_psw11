from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Empresa
from brutils import is_valid_cnpj


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
                nome = nome,
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
    empresas = Empresa.objects.all()
    busca = request.GET.get('empresa')
    if busca:
        empresas = empresas.filter(nome__icontains=busca)
    context = {'empresas': empresas, 'busca': busca}
    return render(request, template_name, context)
