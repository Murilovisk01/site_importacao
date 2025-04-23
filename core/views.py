from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login,update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count,Q,Sum, F, ExpressionWrapper, DurationField
from django.utils import timezone
from django.utils.timezone import localtime,now
from core.decorators import aprovado_required
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from .models import Implatacao, RegistroTempo, SistemaExterno, Tarefa, Sistema, TempoSistemaExterno, TipoTarefa, Perfil
from .forms import  ComentarioForm, ImplantacaoForm, MinhaContaForm, RegistroTempoForm, SistemaExternoForm, TempoSistemaExternoForm, TipoTarefaForm, SistemaForm, TarefaForm,RegistroForm
from .forms import RegistroForm
from dal import autocomplete
from django.core.paginator import Paginator

class CustomLoginView(LoginView):
    template_name = 'core/user/login.html'
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        if hasattr(user, 'perfil') and not user.perfil.aprovado:
            messages.error(self.request, 'Seu acesso ainda não foi aprovado pela equipe.')
            return redirect('login')

        login(self.request, user)
        return redirect('dashboard') 

def tela_inicial(request):
    termo = request.GET.get('q', '')
    sistemas = Sistema.objects.all()

    if termo:
        sistemas = sistemas.filter(nome__icontains=termo)

    return render(request, 'core/tela_inicial.html', {'sistemas': sistemas})

@login_required
@aprovado_required
def dashboard_kanban(request):
    membro_id = request.GET.get('membro')
    busca = request.GET.get('q')
    atribuidas = request.GET.get('atribuidas')

    tarefas = Tarefa.objects.all()

    if atribuidas == '1':  
        tarefas = tarefas.filter(atribuido_para=request.user)
    elif membro_id:
        tarefas = tarefas.filter(atribuido_para__id=membro_id)

    if busca:
        tarefas = tarefas.filter(titulo__icontains=busca)

    tarefas_inicial = tarefas.filter(status='inicial')
    tarefas_andamento = tarefas.filter(status='andamento')
    tarefas_concluida = tarefas.filter(status='concluida')

    acumulados = {}
    registros_ativos = {}

    for tarefa in tarefas:
        total = tarefa.registros_tempo.filter(fim__isnull=False).aggregate(
            total=Sum(ExpressionWrapper(F('fim') - F('inicio'), output_field=DurationField()))
        )['total']
        acumulados[tarefa.id] = int(total.total_seconds()) if total else 0

        ativo = tarefa.registros_tempo.filter(fim__isnull=True).last()
        if ativo:
            registros_ativos[tarefa.id] = ativo.inicio.isoformat()

    status_colunas = [
        ('inicial', 'Inicial', tarefas_inicial, 'secondary'),
        ('andamento', 'Em andamento', tarefas_andamento, 'warning'),
        ('concluida', 'Concluída', tarefas_concluida, 'success'),
    ]
    
    return render(request, 'core/dashboard_kanban.html', {
        'status_colunas': status_colunas,
        'tarefas_inicial': tarefas_inicial,
        'tarefas_andamento': tarefas_andamento,
        'tarefas_concluida': tarefas_concluida,
        'filtro_membro': int(membro_id) if membro_id else None,
        'busca': busca or '',
        'acumulados': acumulados,
        'registros_ativos': registros_ativos,
        'atribuidas': atribuidas,
    })

# Tela Tipo Tarefas, criação, edição, exclusão
@login_required
@aprovado_required
def criar_tipo_tarefa(request):
    if request.method == 'POST':
        form = TipoTarefaForm(request.POST)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.criado_por = request.user
            tipo.save()
            messages.success(request, "Tipo de tarefa criado com sucesso.")
            return redirect('listar_tipotarefa')
    else:
        form = TipoTarefaForm()

    return render(request, 'core/form.html', {
        'form': form,
        'titulo': 'Criar Tipo de Tarefa'
    })

@login_required
@aprovado_required
def listar_tipotarefas(request):
    tipos = TipoTarefa.objects.all()
    return render(request, 'core/tela_tarefas/listar_tipotarefas.html', {'tipos': tipos})

@login_required
@aprovado_required
def editar_tipo_tarefa(request, tipo_id):
    tipo = get_object_or_404(TipoTarefa, id=tipo_id)

    if request.method == 'POST':
        form = TipoTarefaForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de tarefa atualizado com sucesso.')
            return redirect('listar_tipotarefa')
    else:
        form = TipoTarefaForm(instance=tipo)

    return render(request, 'core/form.html', {
        'form': form,
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
        messages.success(request, "Tipo de tarefa excluido com sucesso.")
        return redirect('listar_tipotarefa')
    
    return render(request, 'core/confirmar_exclusao.html', {'tipo':tipo})

# Tela Sistemas, criação, edição, exclusão
@login_required
@aprovado_required
def criar_sistema(request):
    if request.method == 'POST':
        form = SistemaForm(request.POST, request.FILES)
        if form.is_valid():
            sistema = form.save(commit=False)
            sistema.criado_por = request.user
            sistema.save()
            messages.success(request, 'Sistema criado com sucesso.')
            return redirect('listar_sistemas')
    else:
        form = SistemaForm()

    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Criar Sistema'})

@login_required
@aprovado_required
def listar_sistemas(request):

    sistemas = Sistema.objects.all()
    return render(request, 'core/tela_sistemas/listar_sistemas.html', {'sistemas': sistemas})

@login_required
@aprovado_required
def editar_sistema(request, sistema_id):
    sistema = get_object_or_404(Sistema, id=sistema_id)
    
    if request.method == 'POST':
        form = SistemaForm(request.POST, request.FILES, instance=sistema,)
        if form.is_valid():
            form.save()
            messages.success(request, "sistema editado com sucesso.")
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
        messages.success(request, "Sistema excluido com sucesso.")
        return redirect('listar_sistemas')
    
    return render(request,'core/confirmar_exclusao.html',{'sistema':sistema})

# Telas Tarefas, criação, edição, exclusão, mover
@login_required
@aprovado_required
def criar_tarefa(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.criado_por = request.user
            tarefa.save()
            messages.success(request, "Tarefa criado com sucesso.")
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
            messages.success(request, "Tarefa editada com sucesso.")
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
        messages.success(request, "Tarefa excluida com sucesso.")
        return redirect('dashboard')

    return render(request, 'core/confirmar_exclusao.html', {'tarefa': tarefa})

@login_required
@aprovado_required
def detalhes_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    # ⏱️ Calcular tempo total da tarefa
    registros = tarefa.registros_tempo.all()
    total_segundos = sum(
        [(r.fim - r.inicio if r.fim else timezone.now() - r.inicio).total_seconds() for r in registros],
        0
    )
    tempo_total = str(timedelta(seconds=int(total_segundos)))

    # 💬 Comentários
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        form.fields['texto'].widget.attrs.update({'tabindex': '-1'})
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarefa = tarefa
            comentario.autor = request.user
            comentario.save()
            messages.success(request, "Comentário adicionado.")
            return redirect('detalhes_tarefa', tarefa_id=tarefa.id)
    else:
        form = ComentarioForm()
        form.fields['texto'].widget.attrs.update({'tabindex': '-1'})

    comentarios = tarefa.comentarios.all().order_by('-criado_em')

    # 🧠 Obter e formatar tempos em sistemas externos
    registros_externos = tarefa.tempos_externos.select_related('usuario', 'sistema')

    def formatar_tempo(td):
        if not td:
            return "00:00"
        total_segundos = int(td.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"

    tempos_externos_formatados = [
        {
            'usuario': r.usuario.get_full_name() or r.usuario.username,
            'sistema': r.sistema.nome,
            'tempo': formatar_tempo(r.tempo_corrido),
        }
        for r in registros_externos
    ]

    return render(request, 'core/tela_tarefas/detalhes_tarefa.html', {
        'tarefa': tarefa,
        'form': form,
        'comentarios': comentarios,
        'tempo_total': tempo_total,
        'tempos_externos_formatados': tempos_externos_formatados,
    })

@login_required
@aprovado_required
def mover_tarefa(request, tarefa_id, novo_status):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    if novo_status == 'concluida':
        # Verificar se há algum tempo registrado
        has_tempo = tarefa.registros_tempo.filter(fim__isnull=False).exists()

        if not has_tempo:
            messages.warning(request, '⚠️ Esta tarefa não pode ser concluída pois não possui tempo registrado.')
            return redirect('dashboard')  # ou para detalhes da tarefa

    tarefa.status = novo_status
    tarefa.save()
    messages.success(request, f'Tarefa movida para {novo_status}.')
    return redirect('dashboard')

# Tela Usuario, Registro, edição, painel de equipe, aprovar, remover, relatorios
def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            # Verifica se o nome de usuário já está em uso
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Este nome de usuário já está em uso.')
                return render(request, 'core/user/registro.html', {'form': form})

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
    return render(request, 'core/user/registro.html', {'form': form})

@login_required
def minha_conta(request):
    user = request.user

    if request.method == 'POST':
        form = MinhaContaForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=False)

            senha1 = form.cleaned_data.get("password1")
            senha2 = form.cleaned_data.get("password2")

            if senha1 and senha2 and senha1 == senha2:
                user.set_password(senha1)
                update_session_auth_hash(request, user)

            user.save()
            messages.success(request, "Dados atualizados com sucesso.")
            return redirect('dashboard')
    else:
        form = MinhaContaForm(instance=user)

    return render(request, 'core/user/minha_conta.html', {'form': form})

@login_required
@aprovado_required
def painel_equipe(request):
    perfil = request.user.perfil

    if not perfil.is_gerente:
        return HttpResponseForbidden("Apenas gerentes podem acessar o painel da equipe.")

    membros = Perfil.objects.exclude(user=request.user)

    return render(request, 'core/tela_equipe/painel_equipe.html', {
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

# Relatorio equipe
@aprovado_required
@login_required
def relatorio_equipe(request):
    tarefas = Tarefa.objects.all()

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    tipo_id = request.GET.get('tipo')
    status = request.GET.get('status')
    usuario_id = request.GET.get('usuario')
    is_gerente = request.user.perfil.is_gerente

    # Se não for gerente, força o filtro para o próprio usuário
    if not is_gerente:
    # Técnicos só podem ver suas próprias tarefas
        usuario_id = str(request.user.id)


    hoje = now().date()
    if not data_inicio:
        data_inicio = hoje.replace(day=1).isoformat()
    if not data_fim:
        data_fim = hoje.isoformat()

    tarefas = tarefas.filter(data_criacao__date__gte=data_inicio, data_criacao__date__lte=data_fim)

    if tipo_id:
        tarefas = tarefas.filter(tipo_id=tipo_id)
    if status:
        tarefas = tarefas.filter(status=status)
    if is_gerente:
        if usuario_id:
            tarefas = tarefas.filter(atribuido_para_id=usuario_id)
    else:
        tarefas = tarefas.filter(atribuido_para_id=request.user.id)

    total = tarefas.count()
    concluidas = tarefas.filter(status='concluida').count()
    andamento = tarefas.filter(status='andamento').count()
    inicial = tarefas.filter(status='inicial').count()

    tarefas_por_tipo = tarefas.values('tipo__nome').annotate(qtd=Count('id'))

    # Agrupar por tipo e status
    dados_grafico_tipo_status = defaultdict(lambda: {'inicial': 0, 'andamento': 0, 'concluida': 0})
    for t in tarefas:
        nome_tipo = t.tipo.nome if t.tipo else 'Sem tipo'
        dados_grafico_tipo_status[nome_tipo][t.status] += 1

    # Tempo por tipo — filtrando registros_tempo pelo usuário se houver filtro
    if usuario_id:
        tempo_por_tipo = tarefas.filter(registros_tempo__usuario_id=usuario_id).values('tipo__nome').annotate(
            tempo_total=Sum(
                ExpressionWrapper(F('registros_tempo__fim') - F('registros_tempo__inicio'), output_field=DurationField())
            )
        )
    else:
        tempo_por_tipo = tarefas.values('tipo__nome').annotate(
            tempo_total=Sum(
                ExpressionWrapper(F('registros_tempo__fim') - F('registros_tempo__inicio'), output_field=DurationField())
            )
        )

    # Converter para texto legível
    def formatar_timedelta(td):
        if not td:
            return "00:00:00"
        total_segundos = int(td.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        segundos = total_segundos % 60
        return f"{horas:02}:{minutos:02}:{segundos:02}"

    tempo_formatado = {
        item['tipo__nome'] or 'Sem tipo': formatar_timedelta(item['tempo_total'])
        for item in tempo_por_tipo
    }

    tarefas_por_sistema = tarefas.values('sistema__nome').annotate(qtd=Count('id')).order_by('sistema__nome')

    # Tempo de sistemas externos por sistema + tipo de tarefa
    tempo_externo_agrupado_query = TempoSistemaExterno.objects.all()

    # Filtro por tarefa no período
    tempo_externo_agrupado_query = tempo_externo_agrupado_query.filter(tarefa__data_criacao__date__gte=data_inicio,
                                                                    tarefa__data_criacao__date__lte=data_fim)

    # Filtro por tipo/status se aplicável
    if tipo_id:
        tempo_externo_agrupado_query = tempo_externo_agrupado_query.filter(tarefa__tipo_id=tipo_id)
    if status:
        tempo_externo_agrupado_query = tempo_externo_agrupado_query.filter(tarefa__status=status)

    # Se for técnico, mostrar só tempos lançados por ele
    if not is_gerente:
        tempo_externo_agrupado_query = tempo_externo_agrupado_query.filter(usuario=request.user)
    elif usuario_id:
        # Se for gerente e estiver filtrando
        tempo_externo_agrupado_query = tempo_externo_agrupado_query.filter(usuario_id=usuario_id)

    tempo_externo_agrupado = (
        tempo_externo_agrupado_query
        .values('sistema__nome', 'tarefa__tipo__nome')
        .annotate(tempo_total=Sum('tempo_corrido'))
        .order_by('sistema__nome', 'tarefa__tipo__nome')
    )

    tempo_sistemas_tipo_formatado = [
        {
            'descricao': f"{item['sistema__nome']} - {item['tarefa__tipo__nome'] or 'Sem tipo'}",
            'tempo': formatar_timedelta(item['tempo_total'])
        }
        for item in tempo_externo_agrupado
    ]


    context = {
        'is_gerente': is_gerente,
        'tempo_sistemas_externos_tipo': tempo_sistemas_tipo_formatado,
        'tarefas_por_sistema': list(tarefas_por_sistema),
        'tempo_por_tipo': tempo_formatado,
        'dados_grafico_tipo_status': dict(dados_grafico_tipo_status),
        'total': total,
        'concluidas': concluidas,
        'andamento': andamento,
        'inicial': inicial,
        'tarefas_por_tipo': list(tarefas_por_tipo),
        'tipos': TipoTarefa.objects.all(),
        'usuarios': User.objects.all(),
        'filtros': {
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'tipo_id': tipo_id,
            'status': status,
            'usuario_id': usuario_id,
        }
    }

    return render(request, 'core/tela_equipe/relatorio_equipe.html', context)

# Tela de implantação, função de inicar, pausar e editar os registros da implantação
@login_required
@aprovado_required
def criar_implantador(request):
    if request.method == 'POST':
        form = ImplantacaoForm(request.POST, request.FILES)
        if form.is_valid():
            implantador = form.save(commit=False)
            implantador.criado_por = request.user
            implantador.save()
            messages.success(request, 'Implantador criado com sucesso.')
            return redirect('listar_implantador')
    else:
        form = ImplantacaoForm()

    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Criar Implantador'})

@login_required
@aprovado_required
def listar_implantador(request):
    implantadores = Implatacao.objects.all()
    return render(request, 'core/tela_implantacao/listar_implantador.html', {'implantadores': implantadores})

@login_required
@aprovado_required
def editar_implatador(request, implantador_id):
    implantador = get_object_or_404(Implatacao, id=implantador_id)
    
    if request.method == 'POST':
        form = ImplantacaoForm(request.POST, request.FILES, instance=implantador,)
        if form.is_valid():
            form.save()
            messages.success(request, "Implantador editado com sucesso.")
            return redirect('listar_implantador')
    else:
        form = ImplantacaoForm(instance=implantador)
    
    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Editar Implantador'})

@login_required
@aprovado_required
def excluir_implantador(request,implantador_id):
    implantador = get_object_or_404(Implatacao, id=implantador_id)

    if request.user != implantador.criado_por:
        return redirect('listar_implantador')
    
    if request.method == 'POST':
        implantador.delete()
        messages.success(request, "Implantador excluido com sucesso.")
        return redirect('listar_implantador')
    
    return render(request,'core/confirmar_exclusao.html',{'implantador':implantador})

# Tela de registro de tempo, função de inicar, pausar e editar o tempo da tarefa
@csrf_exempt
@login_required
@aprovado_required
def iniciar_tempo(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    # Finaliza qualquer registro anterior sem fim
    RegistroTempo.objects.filter(tarefa=tarefa, usuario=request.user, fim__isnull=True).update(fim=timezone.now())
    # Cria novo registro
    inicio = timezone.now()
    RegistroTempo.objects.create(tarefa=tarefa, usuario=request.user, inicio=inicio)
    acumulado = tarefa.registros_tempo.filter(usuario=request.user, fim__isnull=False).aggregate(
        total=Sum(ExpressionWrapper(F('fim') - F('inicio'), output_field=DurationField()))
    )['total']
    acumulado_segundos = int(acumulado.total_seconds()) if acumulado else 0
    return JsonResponse({
        'inicio': inicio.isoformat(),
        'acumulado': acumulado_segundos,
    })

@csrf_exempt
@login_required
@aprovado_required
def pausar_tempo(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    registro = tarefa.registros_tempo.filter(usuario=request.user, fim__isnull=True).last()
    if registro:
        registro.fim = timezone.now()
        registro.save()
    return JsonResponse({'status': 'ok'})

@login_required
@aprovado_required
def meu_relatorio_tempo(request):
    registros = RegistroTempo.objects.filter(usuario=request.user).select_related('tarefa')

    # Filtros
    tarefa_query = request.GET.get('tarefa', '')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Mês atual por padrão
    if not data_inicio or not data_fim:
        hoje = timezone.now().date()
        primeiro_dia = hoje.replace(day=1)
        data_inicio = data_inicio or primeiro_dia.isoformat()
        data_fim = data_fim or hoje.isoformat()

    registros = registros.filter(inicio__date__gte=data_inicio, inicio__date__lte=data_fim)

    if tarefa_query:
        registros = registros.filter(tarefa__titulo__icontains=tarefa_query)

    registros = registros.order_by('-inicio')

    # Paginação
    paginator = Paginator(registros, 10)  # 10 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Agrupar os itens da página atual por dia
    registros_por_dia = defaultdict(list)
    for r in page_obj.object_list:
        data_local = localtime(r.inicio).date()
        registros_por_dia[data_local].append(r)

    registros_ordenados = dict(sorted(registros_por_dia.items(), reverse=True))

    return render(request, 'core/tela_tempo/gerenciador_tempo.html', {
        'registros_por_dia': registros_ordenados,
        'page_obj': page_obj,
        'filtros': {
            'tarefa': tarefa_query,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
    })

@login_required
@aprovado_required
def registrar_tempo_manual(request):
    if request.method == 'POST':
        form = RegistroTempoForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            messages.success(request, "Tempo manual criado com sucesso.")
            registro.save()
            return redirect('meu_relatorio_tempo')  # ou onde desejar
    else:
        form = RegistroTempoForm()
    return render(request, 'core/tela_tempo/registro_tempo_form.html', {'form': form})

@login_required
@aprovado_required
def editar_registro_tempo(request, pk):
    registro = get_object_or_404(RegistroTempo, pk=pk)

    # 🔒 Verifica se o usuário logado é o dono do registro
    if registro.usuario != request.user:
        return HttpResponseForbidden("Você não tem permissão para editar este registro.")

    if request.method == 'POST':
        form = RegistroTempoForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            messages.success(request, "Tempo editado com sucesso.")
            return redirect('meu_relatorio_tempo')
    else:
        form = RegistroTempoForm(instance=registro)

    return render(request, 'core/tela_tempo/registro_tempo_form.html', {'form': form})

class TarefaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Tarefa.objects.none()

        qs = Tarefa.objects.all()

        if self.q:
            qs = qs.filter(
                Q(titulo__icontains=self.q) |
                Q(tipo__nome__icontains=self.q) |
                Q(atribuido_para__username__icontains=self.q)
            )
        return qs

# Tela sistema externo
@login_required
@aprovado_required
def criar_sistema_externo(request):
    if request.method == 'POST':
        form = SistemaExternoForm(request.POST, request.FILES)
        if form.is_valid():
            sistema_externo = form.save(commit=False)
            sistema_externo.usuario = request.user
            sistema_externo.save()
            messages.success(request, 'Sistema Externo criado com sucesso.')
            return redirect('listar_sistemas_externo')
    else:
        form = SistemaExternoForm()

    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Criar Sistema Externo'})

@login_required
@aprovado_required
def listar_sistemas_externo(request):
    sistemas = SistemaExterno.objects.all()
    return render(request, 'core/tela_sistema_externo/listar_sistema_externo.html', {'sistemas': sistemas})

@login_required
@aprovado_required
def excluir_sistema_externo(request,pk):
    sistema = get_object_or_404(SistemaExterno, pk=pk)
    
    if request.method == 'POST':
        sistema.delete()
        messages.success(request, "Sistema excluido com sucesso.")
        return redirect('listar_sistemas_externo')
    
    return render(request,'core/confirmar_exclusao.html',{'sistema':sistema})

@login_required
@aprovado_required
def editar_sistema_externo(request, pk):
    sistema = get_object_or_404(SistemaExterno, pk=pk)
    
    if request.method == 'POST':
        form = SistemaExternoForm(request.POST, request.FILES, instance=sistema,)
        if form.is_valid():
            form.save()
            messages.success(request, "sistema editado com sucesso.")
            return redirect('listar_sistemas_externo')
    else:
        form = SistemaExternoForm(instance=sistema)
    
    return render(request, 'core/form_basico.html', {'form': form, 'titulo': 'Editar Sistema Externo'})

# Tela Tempo externo
@login_required
@aprovado_required
def adicionar_tempo_externo(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)

    if request.method == 'POST':
        form = TempoSistemaExternoForm(request.POST)
        if form.is_valid():
            tempo_externo = form.save(commit=False)
            tempo_externo.usuario = request.user
            tempo_externo.tarefa = tarefa
            tempo_externo.save()
            messages.success(request, 'Tempo adicionado com sucesso.')
            return redirect('detalhes_tarefa', tarefa_id=tarefa.id)
    else:
        form = TempoSistemaExternoForm()

    return render(request, 'core/tela_sistema_externo/adicionar_tempo_externo.html', {
        'form': form,
        'tarefa': tarefa
    })

@login_required
@aprovado_required
def editar_tempo_externo(request, tempo_id):
    tempo = get_object_or_404(TempoSistemaExterno, id=tempo_id)

    if tempo.usuario != request.user:
        return HttpResponseForbidden("Você não pode editar esse tempo.")

    if request.method == 'POST':
        form = TempoSistemaExternoForm(request.POST, instance=tempo)
        if form.is_valid():
            form.save()
            messages.success(request, "Tempo externo editado com sucesso.")
            return redirect('detalhes_tarefa', tarefa_id=tempo.tarefa.id)
    else:
        form = TempoSistemaExternoForm(instance=tempo)

    return render(request, 'core/form_basico.html', {
        'form': form,
        'titulo': f'Editar Tempo Externo - {tempo.tarefa.titulo}'
    })

@login_required
@aprovado_required
def excluir_tempo_externo(request, tempo_id):
    tempo = get_object_or_404(TempoSistemaExterno, id=tempo_id)

    if tempo.usuario != request.user:
        return HttpResponseForbidden("Você não pode excluir esse tempo.")

    if request.method == 'POST':
        tempo.delete()
        messages.success(request, "Tempo externo excluído.")
        return redirect('detalhes_tarefa', tarefa_id=tempo.tarefa.id)

    return render(request, 'core/confirmar_exclusao.html', {'tempo': tempo})

@login_required
@aprovado_required
def gerenciar_tempos_externos(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    registros = tarefa.tempos_externos.select_related('usuario', 'sistema')

    return render(request, 'core/tela_sistema_externo/gerenciar_tempos.html', {
        'tarefa': tarefa,
        'registros': registros,
    })
