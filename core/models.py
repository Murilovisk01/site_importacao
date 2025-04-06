from django.db import models
from django.contrib.auth.models import User

class Sistema(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class TipoTarefa(models.Model):
    nome = models.CharField(max_length=100)
    roteiro = models.TextField()

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
    link_1 = models.URLField(blank=True, null=True)
    link_2 = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inicial')

    def __str__(self):
        return self.titulo
