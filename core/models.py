from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
    
class Sistema(models.Model):
    nome = models.CharField(max_length=100)
    data_mapeamento = models.DateField(null=True, blank=True)
    base_dados = models.CharField(max_length=100, blank=True)
    icone = models.ImageField(upload_to='icones_sistema/', null=True, blank=True)
    criado_por = models.ForeignKey(User, related_name='sistemas_criados', on_delete=models.CASCADE)
    def __str__(self):
        return self.nome

class TipoTarefa(models.Model):
    nome = models.CharField(max_length=100)
    roteiro = models.TextField()
    titulo_padrao = models.CharField(max_length=200, blank=True)
    criado_por = models.ForeignKey(User, related_name='tipos_criados', on_delete=models.CASCADE)
    def __str__(self):
        return self.nome

class Implatacao(models.Model):
    STATUS_CHOICES_IMPLATACAO = [
        ('implantador','Implantador'),
        ('analista','Analista'),
        ('coordenador','Coordenador'),
        ('gerente','Gerente')
    ]
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=20, choices=STATUS_CHOICES_IMPLATACAO, default='implantador')
    criado_por = models.ForeignKey(User, related_name='implatador_criados', on_delete=models.CASCADE)
    def __str__(self):
        return self.nome
    
class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('inicial', 'Inicial'),
        ('andamento', 'Em andamento'),
        ('concluida', 'Concluída'),
    ]

    titulo = models.CharField(max_length=200)
    tipo = models.ForeignKey(TipoTarefa, on_delete=models.CASCADE)
    sistema = models.ForeignKey(Sistema, on_delete=models.CASCADE)
    criado_por = models.ForeignKey(User, related_name='tarefas_criadas', on_delete=models.CASCADE)
    atribuido_para = models.ForeignKey(User, related_name='atribuídas', on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    prazo = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inicial')
    documentacao = models.TextField(blank=True)
    link_glpi = models.TextField(blank=True)
    link_redmine = models.TextField(blank=True)
    analista = models.ForeignKey(Implatacao, on_delete=models.SET_NULL, null=True, blank=True, related_name='tarefas_analista')
    implatador = models.ForeignKey(Implatacao, on_delete=models.SET_NULL, null=True, blank=True, related_name='tarefas_implantador')


    def __str__(self):
        return self.titulo

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_gerente = models.BooleanField(default=False)
    aprovado = models.BooleanField(default=False)  # Se for True, o gerente já aceitou

    def __str__(self):
        return self.user.username
    
class Comentario(models.Model):
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.autor.username} - {self.criado_em.strftime("%d/%m/%Y %H:%M")}'

class RegistroTempo(models.Model):
    tarefa = models.ForeignKey('Tarefa', on_delete=models.CASCADE, related_name='registros_tempo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    inicio = models.DateTimeField()
    fim = models.DateTimeField(null=True, blank=True)

    def duracao(self):
        if self.fim:
            diff = self.fim - self.inicio
            horas, resto = divmod(diff.total_seconds(), 3600)
            minutos, _ = divmod(resto, 60)
            return f"{int(horas)}h {int(minutos)}min"
        return None

    def __str__(self):
        return f"{self.tarefa.titulo} - {self.inicio.strftime('%d/%m/%Y %H:%M')}"

  
@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(
            user=instance,
            aprovado=instance.is_superuser,
            is_gerente=instance.is_superuser
        )
    else:
        instance.perfil.save()

