from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render,redirect,get_object_or_404
from django.utils.dateparse import parse_date
from django.http import HttpResponseForbidden
from .models import Tarefa, Sistema, TipoTarefa, Equipe, Perfil
from .forms import ComentarioForm, TipoTarefaForm, SistemaForm, TarefaForm,RegistroForm
from .forms import RegistroForm
from django.contrib.auth.models import User

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        if hasattr(user, 'perfil') and not user.perfil.aprovado:
            messages.error(self.request, 'Seu acesso ainda não foi aprovado pela equipe.')
            return redirect('login')

        login(self.request, user)
        return redirect(self.get_success_url())

@login_required
def dashboard_kanban(request):
    perfil = request.user.perfil

    if not perfil.aprovado or not perfil.equipe:
        messages.error(request, "Você ainda não está em uma equipe aprovada.")
        return redirect('logout')

    equipe = perfil.equipe
    membro_id = request.GET.get('membro')
    busca = request.GET.get('q')

    tarefas = Tarefa.objects.filter(criado_por__perfil__equipe=equipe)

    if membro_id:
        tarefas = tarefas.filter(atribuido_para__id=membro_id)

    if busca:
        tarefas = tarefas.filter(titulo__icontains=busca)

    tarefas_inicial = tarefas.filter(status='inicial')
    tarefas_andamento = tarefas.filter(status='andamento')
    tarefas_concluida = tarefas.filter(status='concluida')

    membros = User.objects.filter(perfil__equipe=equipe, perfil__aprovado=True)

    return render(request, 'core/dashboard_kanban.html', {
        'tarefas_inicial': tarefas_inicial,
        'tarefas_andamento': tarefas_andamento,
        'tarefas_concluida': tarefas_concluida,
        'membros': membros,
        'filtro_membro': int(membro_id) if membro_id else None,
        'busca': busca or '',
    })

@login_required
def criar_tipo_tarefa(request):
    if request.method == 'POST':
        form = TipoTarefaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de tarefa criado com sucesso.')
            return redirect('dashboard')
    else:
        form = TipoTarefaForm()

    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Criar Tipo de Tarefa'})

@login_required
def criar_sistema(request):
    if request.method == 'POST':
        form = SistemaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sistema criado com sucesso.')
            return redirect('dashboard')
    else:
        form = SistemaForm()

    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Criar Sistema'})

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

@login_required
def detalhes_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    if not request.user.perfil.equipe == tarefa.criado_por.perfil.equipe:
        return HttpResponseForbidden("Você não pode ver essa tarefa.")

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        form.fields['texto'].widget.attrs.update({'tabindex': '-1'})  # ← aqui
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarefa = tarefa
            comentario.autor = request.user
            comentario.save()
            messages.success(request, "Comentário adicionado.")
            return redirect('detalhes_tarefa', tarefa_id=tarefa.id)
    else:
        form = ComentarioForm()
        form.fields['texto'].widget.attrs.update({'tabindex': '-1'})  # ← aqui também

    comentarios = tarefa.comentarios.all().order_by('-criado_em')

    return render(request, 'core/detalhes_tarefa.html', {
        'tarefa': tarefa,
        'form': form,
        'comentarios': comentarios,
    })


def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            senha = form.cleaned_data['senha']
            user.set_password(senha)
            user.save()

            perfil = user.perfil  # é criado automaticamente via sinal

            if form.cleaned_data['criar_nova_equipe']:
                # Criando nova equipe
                nome_equipe = form.cleaned_data['nome_equipe']
                descricao = form.cleaned_data['descricao_equipe']
                codigo = form.cleaned_data['codigo_acesso']

                if Equipe.objects.filter(codigo_acesso=codigo).exists():
                    form.add_error('codigo_acesso', 'Este código de acesso já está em uso.')
                    return render(request, 'core/registro.html', {'form': form})

                equipe = Equipe.objects.create(
                    nome=nome_equipe,
                    descricao=descricao,
                    codigo_acesso=codigo,
                    criado_por=user
                )
                perfil.equipe = equipe
                perfil.is_gerente = True
                perfil.aprovado = True
                perfil.save()
            else:
                # Entrando em equipe existente
                codigo = form.cleaned_data['codigo_acesso']
                try:
                    equipe = Equipe.objects.get(codigo_acesso=codigo)
                    perfil.equipe = equipe
                    perfil.aprovado = False
                    perfil.save()
                    messages.info(request, "Cadastro realizado! Aguarde a aprovação da equipe.")
                    return redirect('login')  # redireciona sem fazer login
                except Equipe.DoesNotExist:
                    form.add_error('codigo_acesso', 'Código de equipe inválido.')
                    return render(request, 'core/registro.html', {'form': form})
                
            login(request, user)  # faz login automático após registro
            return redirect('dashboard')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})

@login_required
def painel_equipe(request):
    perfil = request.user.perfil

    if not perfil.equipe or not perfil.is_gerente:
        return HttpResponseForbidden("Apenas gerentes podem acessar o painel da equipe.")

    equipe = perfil.equipe
    membros = Perfil.objects.filter(equipe=equipe).exclude(user=request.user)

    return render(request, 'core/painel_equipe.html', {
        'equipe': equipe,
        'membros': membros
    })

@login_required
def aprovar_membro(request, perfil_id):
    gerente = request.user.perfil

    if not gerente.is_gerente or not gerente.equipe:
        return HttpResponseForbidden("Apenas gerentes podem aprovar membros.")

    perfil = get_object_or_404(Perfil, id=perfil_id)

    if perfil.equipe != gerente.equipe:
        return HttpResponseForbidden("Você só pode aprovar membros da sua equipe.")

    perfil.aprovado = True
    perfil.save()

    messages.success(request, f'{perfil.user.username} foi aprovado com sucesso.')
    return redirect('painel_equipe')

@login_required
def toggle_gerente(request, perfil_id):
    gerente = request.user.perfil

    if not gerente.is_gerente or not gerente.equipe:
        return HttpResponseForbidden("Apenas gerentes podem alterar cargos.")

    perfil = get_object_or_404(Perfil, id=perfil_id)

    if perfil.equipe != gerente.equipe:
        return HttpResponseForbidden("Este usuário não faz parte da sua equipe.")

    # impede o gerente de se remover sozinho
    if perfil.user == request.user:
        messages.error(request, "Você não pode alterar seu próprio cargo.")
        return redirect('painel_equipe')

    perfil.is_gerente = not perfil.is_gerente
    perfil.save()

    if perfil.is_gerente:
        messages.success(request, f"{perfil.user.username} agora é gerente.")
    else:
        messages.success(request, f"{perfil.user.username} foi rebaixado para membro.")
    
    return redirect('painel_equipe')

@login_required
def remover_membro(request, perfil_id):
    gerente = request.user.perfil

    if not gerente.is_gerente or not gerente.equipe:
        return HttpResponseForbidden("Apenas gerentes podem remover membros.")

    perfil = get_object_or_404(Perfil, id=perfil_id)

    if perfil.equipe != gerente.equipe:
        return HttpResponseForbidden("Este usuário não faz parte da sua equipe.")

    if perfil.user == request.user:
        messages.error(request, "Você não pode se remover da equipe.")
        return redirect('painel_equipe')

    nome_usuario = perfil.user.username
    perfil.equipe = None
    perfil.aprovado = False
    perfil.is_gerente = False
    perfil.save()

    messages.success(request, f"{nome_usuario} foi removido da equipe.")
    return redirect('painel_equipe')

