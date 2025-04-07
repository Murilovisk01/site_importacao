from django.contrib import admin
from .models import Equipe, Perfil, Sistema, TipoTarefa, Tarefa

admin.site.register(Sistema)
admin.site.register(TipoTarefa)
admin.site.register(Tarefa)
admin.site.register(Equipe)
admin.site.register(Perfil)