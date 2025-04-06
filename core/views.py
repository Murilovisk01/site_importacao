from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Tarefa
from django.shortcuts import redirect
from .forms import TipoTarefaForm, SistemaForm, TarefaForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

class CustomLoginView(LoginView):
    template_name = 'core/login.html'

from django.utils.dateparse import parse_date
from .models import Sistema, TipoTarefa

@login_required
def dashboard(request):
    tarefas = Tarefa.objects.filter(atribuido_para=request.user)

    status = request.GET.get('status')
    pesquisa = request.GET.get('q')
    sistema_id = request.GET.get('sistema')
    tipo_id = request.GET.get('tipo')
    prazo_ate = request.GET.get('prazo_ate')

    if status:
        tarefas = tarefas.filter(status=status)

    if pesquisa:
        tarefas = tarefas.filter(titulo__icontains=pesquisa)

    if sistema_id:
        tarefas = tarefas.filter(sistema_id=sistema_id)

    if tipo_id:
        tarefas = tarefas.filter(tipo_id=tipo_id)

    if prazo_ate:
        data = parse_date(prazo_ate)
        if data:
            tarefas = tarefas.filter(prazo__lte=data)

    sistemas = Sistema.objects.all()
    tipos = TipoTarefa.objects.all()

    return render(request, 'core/dashboard.html', {
        'tarefas': tarefas,
        'status_selecionado': status,
        'q': pesquisa or '',
        'sistemas': sistemas,
        'tipos': tipos,
        'sistema_id': sistema_id,
        'tipo_id': tipo_id,
        'prazo_ate': prazo_ate,
    })

@login_required
def dashboard_kanban(request):
    """Dashboard visual estilo Kanban"""
    tarefas_inicial = Tarefa.objects.filter(atribuido_para=request.user, status='inicial')
    tarefas_andamento = Tarefa.objects.filter(atribuido_para=request.user, status='andamento')
    tarefas_concluida = Tarefa.objects.filter(atribuido_para=request.user, status='concluida')

    return render(request, 'core/dashboard_kanban.html', {
        'tarefas_inicial': tarefas_inicial,
        'tarefas_andamento': tarefas_andamento,
        'tarefas_concluida': tarefas_concluida,
    })

@login_required
def criar_tipo_tarefa(request):
    if request.method == 'POST':
        form = TipoTarefaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TipoTarefaForm()
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Criar Tipo de Tarefa'})

@login_required
def criar_sistema(request):
    if request.method == 'POST':
        form = SistemaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SistemaForm()
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Criar Sistema'})

@login_required
def criar_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.criado_por = request.user
            tarefa.save()
            return redirect('dashboard')
    else:
        form = TarefaForm()
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Criar Tarefa'})

@login_required
def editar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    # Apenas quem criou ou foi atribuído pode editar
    if request.user != tarefa.criado_por and request.user != tarefa.atribuido_para:
        return redirect('dashboard')

    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TarefaForm(instance=tarefa)
    return render(request, 'core/form.html', {'form': form, 'titulo': f'Editar: {tarefa.titulo}'})

@login_required
def excluir_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    # Apenas o criador pode excluir
    if request.user != tarefa.criado_por:
        return redirect('dashboard')

    if request.method == 'POST':
        tarefa.delete()
        return redirect('dashboard')

    return render(request, 'core/confirmar_exclusao.html', {'tarefa': tarefa})
