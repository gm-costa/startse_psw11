from django.http import HttpResponse
from .models import Empresa
from datetime import datetime
from brutils import is_valid_cnpj


def check_nome_empresa(request):
    nome = request.GET.get('nome').strip()
    if nome:
        if Empresa.objects.filter(nome=nome.upper()):
            return HttpResponse('Nome já cadastrado !')
        else:
            return HttpResponse('')
    else:
        return HttpResponse('Nome não informado !')
    

def check_cnpj(request):
    cnpj = request.GET.get('cnpj')
    if cnpj:
        if not is_valid_cnpj(cnpj):
            return HttpResponse('CNPJ inválido !')
        else:
            return HttpResponse('')
    else:
        return HttpResponse('CNPJ não informado !')


def check_tempo_decorrido(request):
    inicio_atividade = request.GET.get('inicio_atividade')
    dt_inicio_atividade = datetime.strptime(inicio_atividade, '%Y-%m-%d').date()
    dt_hoje = datetime.today().date()
    if dt_inicio_atividade > dt_hoje:
        return HttpResponse('Data maior que atual!')
    tempo = (dt_hoje - dt_inicio_atividade).days
    if tempo < 30:
        msg_texto = f'{str(tempo).zfill(2)} dias'
    else:
        tempo = tempo//30
        msg_texto = f'01 mês' if tempo == 1 else f'{str(tempo).zfill(2)} meses'
    return HttpResponse(f'{msg_texto}  de existência')
