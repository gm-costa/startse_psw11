from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


class Empresa(models.Model):
    estagio_choices = (
        ('I', 'Tenho apenas uma idea'),
        ('MVP', 'Possuo um MVP'),
        ('MVPP', 'Possuo um MVP com clientes pagantes'),
        ('E', 'Empresa pronta para escalar'),
    )
    area_choices = (
        ('ED', 'Ed-tech'),
        ('FT', 'Fintech'),
        ('AT', 'Agrotech'),
        
    )
    alvo_choices = (
        ('B2B', 'Business to Business (B2B)'),
        ('B2C', 'Business to Consumer (B2C)'),
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, unique=True)
    site = models.URLField()
    inicio_atividade = models.DateField()
    descricao = models.TextField() 
    data_final_captacao = models.DateField()
    percentual_equity = models.PositiveSmallIntegerField() # Percentual esperado
    estagio = models.CharField(max_length=4, choices=estagio_choices, default='I')
    area = models.CharField(max_length=3, choices=area_choices)
    publico_alvo = models.CharField(max_length=3, choices=alvo_choices, default='B2B')
    valor = models.DecimalField(max_digits=9, decimal_places=2) # Valor total a ser vendido
    pitch = models.FileField(upload_to='pitchs')
    logo = models.FileField(upload_to='logo')

    @property
    def percent_equity(self):
        html = f'<div class="progress" role="progressbar" aria-valuenow="{self.percentual_equity}" aria-valuemin="0" aria-valuemax="100">'
        html += f'<div class="progress-bar" style="background-color:#60F29A;color:#000;width: {self.percentual_equity}%">{self.percentual_equity}%</div></div>'
        return mark_safe(html)

    def __str__(self):
        return f'{self.user.username} | {self.nome}'
