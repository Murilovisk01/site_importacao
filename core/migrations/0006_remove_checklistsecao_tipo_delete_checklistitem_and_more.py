# Generated by Django 5.2 on 2025-04-11 02:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_sistema_criado_por_tipotarefa_criado_por_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklistsecao',
            name='tipo',
        ),
        migrations.DeleteModel(
            name='ChecklistItem',
        ),
        migrations.DeleteModel(
            name='ChecklistSecao',
        ),
    ]
