# Generated by Django 5.0.7 on 2024-08-16 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investidores', '0002_alter_propostainvestimento_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='propostainvestimento',
            name='data',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
