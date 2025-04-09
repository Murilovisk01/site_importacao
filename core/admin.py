from django.contrib import admin
from .models import ChecklistItem, ChecklistSecao, Perfil, Sistema, TipoTarefa, Tarefa

admin.site.register(Sistema)
admin.site.register(TipoTarefa)
admin.site.register(Tarefa)
admin.site.register(Perfil)
admin.site.register(ChecklistSecao)
admin.site.register(ChecklistItem)