from django.db import models
from django.contrib.auth.models import User
from empresarios.models import Empresa


class PropostaInvestimento(models.Model):
    status_choices = (
        ('AA', 'Aguardando assinatura'),
        ('PE', 'Proposta enviada'),
        ('PA', 'Proposta aceita'),
        ('PR', 'Proposta recusada')
    )
    valor = models.DecimalField(max_digits=9, decimal_places=2)
    percentual = models.FloatField()
    empresa = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
    investidor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=2, choices=status_choices, default='AA')
    selfie = models.FileField(upload_to="selfie", null=True, blank=True)
    rg = models.FileField(upload_to="rg", null=True, blank=True)

    @property
    def valuation(self):
        return float((100*self.valor)) / self.percentual

    def __str__(self):
        return str(self.valor)
