# Generated by Django 5.2 on 2025-04-09 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_tipotarefa_checklist_checklistsecao_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='checklistitem',
            options={'ordering': ['ordem']},
        ),
        migrations.AlterModelOptions(
            name='checklistsecao',
            options={'ordering': ['ordem']},
        ),
        migrations.AddField(
            model_name='checklistitem',
            name='ordem',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='checklistsecao',
            name='ordem',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
