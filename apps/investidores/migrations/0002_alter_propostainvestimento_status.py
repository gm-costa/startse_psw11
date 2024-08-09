# Generated by Django 5.0.7 on 2024-08-09 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investidores', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propostainvestimento',
            name='status',
            field=models.CharField(choices=[('AA', 'Aguardando assinatura'), ('PE', 'Proposta enviada'), ('PA', 'Proposta aceita'), ('PR', 'Proposta recusada')], default='AA', max_length=2),
        ),
    ]
