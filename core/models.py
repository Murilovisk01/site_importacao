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

class ChecklistSecao(models.Model):
    tipo = models.ForeignKey('TipoTarefa', on_delete=models.CASCADE, related_name='secoes')
    titulo = models.CharField(max_length=255)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.titulo

class ChecklistItem(models.Model):
    secao = models.ForeignKey('ChecklistSecao', on_delete=models.CASCADE, related_name='itens')
    descricao = models.TextField()
    obrigatorio = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.descricao

    
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

