from django.urls import path
from .views import CustomLoginView, aprovar_membro, criar_sistema, criar_tarefa, criar_tipo_tarefa, dashboard_kanban, detalhes_tarefa, editar_tarefa, excluir_tarefa, painel_equipe, registro_usuario, remover_membro, toggle_gerente
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', dashboard_kanban, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('criar-tipo/', criar_tipo_tarefa, name='criar_tipo'),
    path('criar-sistema/', criar_sistema, name='criar_sistema'),
    path('criar-tarefa/', criar_tarefa, name='criar_tarefa'),
    path('editar-tarefa/<int:tarefa_id>/', editar_tarefa, name='editar_tarefa'),
    path('excluir-tarefa/<int:tarefa_id>/', excluir_tarefa, name='excluir_tarefa'),
    path('tarefa/<int:tarefa_id>/', detalhes_tarefa, name='detalhes_tarefa'),
    path('registro/', registro_usuario, name='registro'),
    path('equipe/', painel_equipe, name='painel_equipe'),
    path('equipe/aprovar/<int:perfil_id>/', aprovar_membro, name='aprovar_membro'),
    path('equipe/toggle-gerente/<int:perfil_id>/', toggle_gerente, name='toggle_gerente'),
    path('equipe/remover/<int:perfil_id>/', remover_membro, name='remover_membro'),

]
