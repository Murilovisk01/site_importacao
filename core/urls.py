from django.urls import path
from .views import CustomLoginView, TarefaAutocomplete, adicionar_tempo_externo, aprovar_membro, criar_implantador, criar_sistema, criar_sistema_externo, criar_tarefa, criar_tipo_tarefa, dashboard_kanban, detalhes_tarefa, editar_implatador, editar_registro_tempo, editar_sistema, editar_sistema_externo, editar_tarefa, editar_tempo_externo, editar_tipo_tarefa, excluir_implantador, excluir_registro_tempo, excluir_sistema, excluir_sistema_externo, excluir_tarefa, excluir_tempo_externo, excluir_tipo_tarefa, gerenciar_tempos_externos, iniciar_tempo, listar_implantador, listar_sistemas, listar_sistemas_externo, listar_tipotarefas, meu_relatorio_tempo, minha_conta, mover_tarefa, painel_equipe, pausar_tempo, registrar_tempo_manual, registro_usuario, relatorio_equipe, remover_membro, tela_inicial, toggle_gerente
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
    path('excluir-tempo/<int:pk>/', excluir_registro_tempo, name='excluir_registro_tempo'),

    path('meu-relatorio-tempo/', meu_relatorio_tempo, name='meu_relatorio_tempo'),
    path('tarefa-autocomplete/', TarefaAutocomplete.as_view(), name='tarefa-autocomplete'),

    path('sistema_externo/novo/', criar_sistema_externo, name='criar_sistema_externo'),
    path('sistema_externo/', listar_sistemas_externo, name='listar_sistemas_externo'),
    path('sistema_externo/<int:pk>/excluir/', excluir_sistema_externo, name='excluir_sistema_externo'),
    path('sistema_externo/<int:pk>/editar/', editar_sistema_externo, name='editar_sistema_externo'),

    path('tarefa/<int:tarefa_id>/tempo-externo/', adicionar_tempo_externo, name='adicionar_tempo_externo'),
    path('tempo_externo/<int:tempo_id>/editar/', editar_tempo_externo, name='editar_tempo_externo'),
    path('tempo_externo/<int:tempo_id>/excluir/', excluir_tempo_externo, name='excluir_tempo_externo'),
    path('tarefa/<int:tarefa_id>/tempos_externos/', gerenciar_tempos_externos, name='gerenciar_tempos_externos'),




]
