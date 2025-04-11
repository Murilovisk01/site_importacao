from django.urls import path
from .views import CustomLoginView, aprovar_membro, criar_sistema, criar_tarefa, criar_tipo_tarefa, dashboard_kanban, detalhes_tarefa, editar_sistema, editar_tarefa, editar_tipo_tarefa, excluir_sistema, excluir_tarefa, excluir_tipo_tarefa, listar_sistemas, listar_tipotarefas, minha_conta, mover_tarefa, painel_equipe, registro_usuario, relatorio_equipe, remover_membro, tela_inicial, toggle_gerente
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', tela_inicial, name='tela_inicial'),
    path('dashboard/', dashboard_kanban, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

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

    path('criar-tarefa/', criar_tarefa, name='criar_tarefa'),
    path('editar-tarefa/<int:tarefa_id>/', editar_tarefa, name='editar_tarefa'),
    path('excluir-tarefa/<int:tarefa_id>/', excluir_tarefa, name='excluir_tarefa'),
    path('tarefa/<int:tarefa_id>/', detalhes_tarefa, name='detalhes_tarefa'),
    path('mover-tarefa/<int:tarefa_id>/<str:novo_status>/', mover_tarefa, name='mover_tarefa'),

    path('registro/', registro_usuario, name='registro'),
    path('equipe/', painel_equipe, name='painel_equipe'),
    path('equipe/aprovar/<int:perfil_id>/', aprovar_membro, name='aprovar_membro'),
    path('equipe/toggle-gerente/<int:perfil_id>/', toggle_gerente, name='toggle_gerente'),
    path('equipe/remover/<int:perfil_id>/', remover_membro, name='remover_membro'),

    path('relatorio/', relatorio_equipe, name='relatorio_equipe'),
    path('minha-conta/', minha_conta, name='minha_conta'),
    
]
