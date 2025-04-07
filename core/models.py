from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets

class Sistema(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class TipoTarefa(models.Model):
    nome = models.CharField(max_length=100)
    roteiro = models.TextField()
    titulo_padrao = models.CharField(max_length=200, blank=True)

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
    criado_por = models.ForeignKey(User, related_name='criadas', on_delete=models.CASCADE)
    atribuido_para = models.ForeignKey(User, related_name='atribuídas', on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    prazo = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inicial')
    documentacao = models.TextField(blank=True)

    def __str__(self):
        return self.titulo

class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    codigo_acesso = models.CharField(max_length=20, unique=True, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equipes_criadas')

    def save(self, *args, **kwargs):
        if not self.codigo_acesso:
            self.codigo_acesso = secrets.token_hex(4)  # Ex: 'a3f92c1d'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, on_delete=models.SET_NULL, null=True, blank=True)
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
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    instance.perfil.save()
