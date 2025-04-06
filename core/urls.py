from django.urls import path
from .views import CustomLoginView, criar_sistema, criar_tarefa, criar_tipo_tarefa, dashboard, dashboard_kanban, editar_tarefa, excluir_tarefa

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('criar-tipo/', criar_tipo_tarefa, name='criar_tipo'),
    path('criar-sistema/', criar_sistema, name='criar_sistema'),
    path('criar-tarefa/', criar_tarefa, name='criar_tarefa'),
    path('editar-tarefa/<int:tarefa_id>/', editar_tarefa, name='editar_tarefa'),
    path('excluir-tarefa/<int:tarefa_id>/', excluir_tarefa, name='excluir_tarefa'),
    path('kanban/', dashboard_kanban, name='kanban'),

]
