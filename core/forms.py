from django import forms
from .models import TipoTarefa, Sistema, Tarefa

class TipoTarefaForm(forms.ModelForm):
    class Meta:
        model = TipoTarefa
        fields = ['nome', 'roteiro']

class SistemaForm(forms.ModelForm):
    class Meta:
        model = Sistema
        fields = ['nome']

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        exclude = ['criado_por', 'data_criacao']
        widgets = {
            'prazo': forms.DateInput(attrs={'type': 'date'}),
        }
