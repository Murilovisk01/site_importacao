# Generated by Django 5.2 on 2025-04-07 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_tipotarefa_titulo_padrao'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefa',
            name='documentacao',
            field=models.TextField(blank=True),
        ),
    ]
