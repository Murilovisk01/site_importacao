from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseForbidden
from .models import ChecklistItem, ChecklistSecao, Tarefa, Sistema, TipoTarefa, Perfil
from .forms import ChecklistItemFormSet, ChecklistSecaoForm, ChecklistSecaoFormSet, ComentarioForm, TipoTarefaForm, SistemaForm, TarefaForm,RegistroForm
from .forms import RegistroForm
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime
from core.decorators import aprovado_required
from django.forms import inlineformset_factory

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        if hasattr(user, 'perfil') and not user.perfil.aprovado:
            messages.error(self.request, 'Seu acesso ainda não foi aprovado pela equipe.')
            return redirect('login')

        login(self.request, user)
        return redirect('dashboard') 

def tela_inicial(request):
    sistemas = Sistema.objects.all()
    return render(request, 'core/tela_inicial.html', {'sistemas': sistemas})

@login_required
@aprovado_required
def dashboard_kanban(request):
    perfil = request.user.perfil

    if not perfil.aprovado:
        messages.error(request, "Você ainda não está em uma equipe aprovada.")
        return redirect('logout')

    
    membro_id = request.GET.get('membro')
    busca = request.GET.get('q')

    tarefas = Tarefa.objects.all()

    if membro_id:
        tarefas = tarefas.filter(atribuido_para__id=membro_id)

    if busca:
        tarefas = tarefas.filter(titulo__icontains=busca)

    tarefas_inicial = tarefas.filter(status='inicial')
    tarefas_andamento = tarefas.filter(status='andamento')
    tarefas_concluida = tarefas.filter(status='concluida')


    return render(request, 'core/dashboard_kanban.html', {
        'tarefas_inicial': tarefas_inicial,
        'tarefas_andamento': tarefas_andamento,
        'tarefas_concluida': tarefas_concluida,
        'filtro_membro': int(membro_id) if membro_id else None,
        'busca': busca or '',
    })

ChecklistSecaoFormSet = inlineformset_factory(
    TipoTarefa, ChecklistSecao, form=ChecklistSecaoForm,
    extra=1, can_delete=True
)

@login_required
@aprovado_required
def criar_tipo_tarefa(request):
    if request.method == 'POST':
        form = TipoTarefaForm(request.POST)
        formset_secoes = ChecklistSecaoFormSet(request.POST, prefix='secoes')

        # Criar os item_formsets com instância vazia (temporária)
        item_formsets = [
            ChecklistItemFormSet(request.POST, prefix=f'itens-{i}')
            for i in range(len(formset_secoes.forms))
        ]

        if form.is_valid() and formset_secoes.is_valid() and all([ifs.is_valid() for ifs in item_formsets]):
            tipo = form.save(commit=False)
            tipo.criado_por = request.user
            tipo.save()

            secoes = formset_secoes.save(commit=False)

            for i, secao_form in enumerate(formset_secoes.forms):
                secao = secao_form.save(commit=False)
                secao.tipo = tipo
                secao.save()

                item_formset = item_formsets[i]
                items = item_formset.save(commit=False)
                for item in items:
                    item.secao = secao
                    item.save()

            messages.success(request, "Tipo de tarefa com checklist criado com sucesso.")
            return redirect('listar_tipotarefa')
        else:
            messages.error(request, "Erro ao criar tipo de tarefa. Verifique os campos.")

    else:
        form = TipoTarefaForm()
        formset_secoes = ChecklistSecaoFormSet(prefix='secoes')
        item_formsets = [ChecklistItemFormSet(prefix=f'itens-{i}') for i in range(len(formset_secoes.forms))]

    return render(request, 'core/form_tipo_checklist.html', {
        'form': form,
        'formset_secoes': formset_secoes,
        'item_formsets': item_formsets,
        'titulo': 'Criar Tipo de Tarefa com Checklist'
    })

@login_required
@aprovado_required
def listar_tipotarefas(request):
    tipos = TipoTarefa.objects.all()
    return render(request, 'core/listar_tipotarefas.html', {'tipos': tipos})

@login_required
@aprovado_required
def editar_tipo_tarefa(request, tipo_id):
    tipo = get_object_or_404(TipoTarefa, id=tipo_id)

    ChecklistSecaoFormSet = inlineformset_factory(
        TipoTarefa, ChecklistSecao, form=ChecklistSecaoForm, extra=0, can_delete=True
    )

    ChecklistItemFormSet = inlineformset_factory(
        ChecklistSecao, ChecklistItem, fields=('descricao', 'obrigatorio'), extra=0, can_delete=True
    )

    if request.method == 'POST':
        form = TipoTarefaForm(request.POST, instance=tipo)
        formset_secoes = ChecklistSecaoFormSet(request.POST, instance=tipo)

        item_formsets = []
        all_valid = form.is_valid() and formset_secoes.is_valid()

        for i, secao_form in enumerate(formset_secoes.forms):
            prefix = f'item_formset_{i}'
            secao_instance = secao_form.instance
            item_formset = ChecklistItemFormSet(
                request.POST,
                instance=secao_instance,
                prefix=prefix
            )
            item_formsets.append(item_formset)
            all_valid = all_valid and item_formset.is_valid()

        if all_valid:
            tipo = form.save()
            secoes = formset_secoes.save(commit=False)

            for i, secao in enumerate(secoes):
                secao.tipo = tipo
                secao.save()

                item_formsets[i].instance = secao
                item_formsets[i].save()

            # Também remover seções marcadas para delete
            for secao_form in formset_secoes.deleted_forms:
                secao_form.instance.delete()

            messages.success(request, "Tipo de tarefa atualizado com sucesso.")
            return redirect('listar_tipotarefa')
    else:
        form = TipoTarefaForm(instance=tipo)
        formset_secoes = ChecklistSecaoFormSet(instance=tipo)
        item_formsets = []

        for i, secao in enumerate(formset_secoes.forms):
            prefix = f'item_formset_{i}'
            secao_instance = secao.instance
            item_formset = ChecklistItemFormSet(instance=secao_instance, prefix=prefix)
            item_formsets.append(item_formset)

    return render(request, 'core/form_tipo_checklist.html', {
        'form': form,
        'formset_secoes': formset_secoes,
        'item_formsets': item_formsets,
        'titulo': 'Editar Tipo de Tarefa'
    })

@login_required
@aprovado_required
def excluir_tipo_tarefa(request, tipo_id):
    tipo = get_object_or_404(TipoTarefa, id=tipo_id)

    if request.user != tipo.criado_por:
        return redirect('listar_tipotarefa')
    
    if request.method == 'POST':
        tipo.delete()
        return redirect('listar_tipotarefa')
    
    return render(request, 'core/confirmar_exclusao.html', {'tipo':tipo})

@login_required
@aprovado_required
def criar_sistema(request):
    if request.method == 'POST':
        form = SistemaForm(request.POST, request.FILES)
        if form.is_valid():
            sistema = form.save(commit=False)
            sistema.save()
            messages.success(request, 'Sistema criado com sucesso.')
            return redirect('dashboard')
    else:
        form = SistemaForm()

    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Criar Sistema'})

@login_required
@aprovado_required
def listar_sistemas(request):

    sistemas = Sistema.objects.all()
    return render(request, 'core/listar_sistemas.html', {'sistemas': sistemas})

@login_required
@aprovado_required
def editar_sistema(request, sistema_id):
    sistema = get_object_or_404(Sistema, id=sistema_id)
    
    if request.method == 'POST':
        form = SistemaForm(request.POST, request.FILES, instance=sistema,)
        if form.is_valid():
            form.save()
            return redirect('listar_sistemas')
    else:
        form = SistemaForm(instance=sistema)
    
    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Editar Sistema'})

@login_required
@aprovado_required
def excluir_sistema(request,sistema_id):
    sistema = get_object_or_404(Sistema, id=sistema_id)

    if request.user != sistema.criado_por:
        return redirect('listar_sistemas')
    
    if request.method == 'POST':
        sistema.delete()
        return redirect('listar_sistemas')
    
    return render(request,'core/confirmar_exclusao.html',{'sistema':sistema})

@login_required
@aprovado_required
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
@aprovado_required
def editar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    # Apenas quem criou ou foi atribuído pode editar
    if request.user != tarefa.criado_por and request.user != tarefa.atribuido_para:
        return redirect('dashboard')

    if request.method == 'POST':
        form = TarefaForm(request.POST or None, instance=tarefa, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TarefaForm(instance=tarefa)
        
    return render(request, 'core/form.html', {
    'form': form,
    'titulo': f'Editar: {tarefa.titulo}',
    'modo_edicao': True
})

@login_required
@aprovado_required
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
@aprovado_required
def detalhes_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

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
            username = form.cleaned_data['username']

            # Verifica se o nome de usuário já está em uso
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Este nome de usuário já está em uso.')
                return render(request, 'core/registro.html', {'form': form})

            try:
                user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['senha']
                )
                user.save()
                perfil = user.perfil  # Criado automaticamente via signal
                perfil.aprovado = False
                perfil.save()

                messages.info(request, 'Cadastro realizado! Aguarde a aprovação do administrador.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f'Erro ao registrar: {str(e)}')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})

@login_required
@aprovado_required
def painel_equipe(request):
    perfil = request.user.perfil

    if not perfil.is_gerente:
        return HttpResponseForbidden("Apenas gerentes podem acessar o painel da equipe.")

    membros = Perfil.objects.exclude(user=request.user)

    return render(request, 'core/painel_equipe.html', {
        'membros': membros
    })

@login_required
@aprovado_required
def aprovar_membro(request, perfil_id):
    gerente = request.user.perfil

    if not gerente.is_gerente:
        return HttpResponseForbidden("Apenas gerentes podem aprovar membros.")

    perfil = get_object_or_404(Perfil, id=perfil_id)

    perfil.aprovado = True
    perfil.save()

    messages.success(request, f'{perfil.user.username} foi aprovado com sucesso.')
    return redirect('painel_equipe')

@login_required
@aprovado_required
def toggle_gerente(request, perfil_id):
    gerente = request.user.perfil

    if not gerente.is_gerente:
        return HttpResponseForbidden("Apenas gerentes podem alterar cargos.")

    perfil = get_object_or_404(Perfil, id=perfil_id)

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
@aprovado_required
def remover_membro(request, perfil_id):
    gerente = request.user.perfil

    if not gerente.is_gerente:
        return HttpResponseForbidden("Apenas gerentes podem remover membros.")

    perfil = get_object_or_404(Perfil, id=perfil_id)

    if perfil.user == request.user:
        messages.error(request, "Você não pode se remover.")
        return redirect('painel_equipe')

    nome_usuario = perfil.user.username

    perfil.aprovado = False
    perfil.is_gerente = False
    perfil.save()

    messages.success(request, f"{nome_usuario} foi desativado.")
    return redirect('painel_equipe')

@login_required
@aprovado_required
def relatorio_equipe(request):
    tarefas = Tarefa.objects.all()

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    tipo_id = request.GET.get('tipo')
    status = request.GET.get('status')

    if data_inicio:
        tarefas = tarefas.filter(criado_em__date__gte=data_inicio)
    if data_fim:
        tarefas = tarefas.filter(criado_em__date__lte=data_fim)
    if tipo_id:
        tarefas = tarefas.filter(tipo_id=tipo_id)
    if status:
        tarefas = tarefas.filter(status=status)

    total = tarefas.count()
    concluidas = tarefas.filter(status='concluida').count()
    andamento = tarefas.filter(status='andamento').count()
    inicial = tarefas.filter(status='inicial').count()

    tarefas_por_tipo = tarefas.values('tipo__nome').annotate(qtd=Count('id'))

    context = {
        'total': total,
        'concluidas': concluidas,
        'andamento': andamento,
        'inicial': inicial,
        'tarefas_por_tipo': list(tarefas_por_tipo),
        'tipos': TipoTarefa.objects.all(),
        'filtros': {
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'tipo_id': tipo_id,
            'status': status,
        }
    }
    return render(request, 'core/relatorio_equipe.html', context)
