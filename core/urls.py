from django.urls import path
from .views import CustomLoginView, TarefaAutocomplete, aprovar_membro, criar_implantador, criar_script, criar_sistema, criar_tarefa, criar_tipo_script, criar_tipo_tarefa, dashboard_kanban, detalhes_script, detalhes_tarefa, editar_implatador, editar_registro_tempo, editar_script, editar_sistema, editar_tarefa, editar_tipo_tarefa, excluir_implantador, excluir_script, excluir_sistema, excluir_tarefa, excluir_tipo_tarefa, iniciar_tempo, listar_implantador, listar_scripts, listar_sistemas, listar_tipotarefas, meu_relatorio_tempo, minha_conta, mover_tarefa, painel_equipe, pausar_tempo, registrar_tempo_manual, registro_usuario, relatorio_equipe, remover_membro, tela_inicial, toggle_gerente
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', tela_inicial, name='tela_inicial'),
    path('dashboard/', dashboard_kanban, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('minha-conta/', minha_conta, name='minha_conta'),

    # Paginas tipo tarefa
    path('criar-tipo/', criar_tipo_tarefa, name='criar_tipo'),
    path('tipotarefas/', listar_tipotarefas, name='listar_tipotarefa'),
    path('editar-tipo/<int:tipo_id>/', editar_tipo_tarefa, name='editar_tipotarefa'),
    path('excluir-tipo-tarefa/<int:tipo_id>/', excluir_tipo_tarefa, name='excluir_tipo_tarefa'),

    # Paginas sistema
    path('criar-sistema/', criar_sistema, name='criar_sistema'),
    path('sistemas/', listar_sistemas, name='listar_sistemas'),
    path('editar-sistema/<int:sistema_id>/', editar_sistema, name='editar_sistema'),
    path('excluir_sistema/<int:sistema_id>/', excluir_sistema, name= 'excluir_sistema'),

    # Paginas de tarefas
    path('criar-tarefa/', criar_tarefa, name='criar_tarefa'),
    path('editar-tarefa/<int:tarefa_id>/', editar_tarefa, name='editar_tarefa'),
    path('excluir-tarefa/<int:tarefa_id>/', excluir_tarefa, name='excluir_tarefa'),
    path('tarefa/<int:tarefa_id>/', detalhes_tarefa, name='detalhes_tarefa'),
    path('mover-tarefa/<int:tarefa_id>/<str:novo_status>/', mover_tarefa, name='mover_tarefa'),

    # Paginas registro e equipe
    path('registro/', registro_usuario, name='registro'),
    path('equipe/', painel_equipe, name='painel_equipe'),
    path('equipe/aprovar/<int:perfil_id>/', aprovar_membro, name='aprovar_membro'),
    path('equipe/toggle-gerente/<int:perfil_id>/', toggle_gerente, name='toggle_gerente'),
    path('equipe/remover/<int:perfil_id>/', remover_membro, name='remover_membro'),

    path('relatorio/', relatorio_equipe, name='relatorio_equipe'),
    
    # Paginas implatadores
    path('criar-implantador/', criar_implantador, name='criar_implantador'),
    path('implantadores/', listar_implantador, name='listar_implantador'),
    path('implantador-editar/<int:implantador_id>/', editar_implatador, name='editar_implatador'),
    path('excluir-implantador/<int:implantador_id>/',excluir_implantador,name='excluir_implantador'),

    # Paginas Contador de tempo
    path('tarefa/<int:tarefa_id>/iniciar/', iniciar_tempo, name='iniciar_tempo'),
    path('tarefa/<int:tarefa_id>/pausar/', pausar_tempo, name='pausar_tempo'),
    path('tempo/manual/', registrar_tempo_manual, name='tempo_manual'),
    path('tempo/<int:pk>/editar/', editar_registro_tempo, name='editar_registro_tempo'),

    path('meu-relatorio-tempo/', meu_relatorio_tempo, name='meu_relatorio_tempo'),
    path('tarefa-autocomplete/', TarefaAutocomplete.as_view(), name='tarefa-autocomplete'),

    path('scripts/', listar_scripts, name='listar_scripts'),
    path('scripts/novo/', criar_script, name='criar_script'),
    path('scripts/<int:pk>/editar/', editar_script, name='editar_script'),
    path('scripts/tipo/novo/', criar_tipo_script, name='criar_tipo_script'),
    path('scripts/<int:pk>/', detalhes_script, name='detalhes_script'),
    path('scripts/<int:pk>/excluir/', excluir_script, name='excluir_script'),



]
