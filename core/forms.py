from django import forms
from .models import Comentario, TipoTarefa, Sistema, Tarefa
from django.contrib.auth.models import User
from django.forms.widgets import DateInput
from django.forms import inlineformset_factory

class TipoTarefaForm(forms.ModelForm):
    class Meta:
        model = TipoTarefa
        fields = ['nome','titulo_padrao', 'roteiro']


class SistemaForm(forms.ModelForm):
    class Meta:
        model = Sistema
        fields = ['nome', 'data_mapeamento', 'base_dados', 'icone']
        widgets = {
            'data_mapeamento': forms.DateInput(attrs={'type': 'date'}),
        }

class TarefaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Retira o argumento 'user'
        super().__init__(*args, **kwargs)

        self.fields['tipo'].queryset = TipoTarefa.objects.all()
        self.fields['sistema'].queryset = Sistema.objects.all()
        self.fields['atribuido_para'].queryset = User.objects.all()

        if kwargs.get('instance'):
            self.fields['tipo'].disabled = True
        self.fields['prazo'].input_formats = ['%Y-%m-%d']

    class Meta:
        model = Tarefa
        fields = ['titulo', 'tipo', 'sistema', 'atribuido_para', 'prazo', 'status', 'documentacao']
        widgets = {
            'prazo': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'documentacao': forms.Textarea(attrs={'rows': 4}),
        }

class RegistroForm(forms.Form):
    username = forms.CharField(label="Nome de usuário")
    email = forms.EmailField(label="Email")
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    confirmar_senha = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar = cleaned_data.get("confirmar_senha")

        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data
    
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'required': False,  # ← ESSENCIAL!
            }),
        }

    def clean_texto(self):
        texto = self.cleaned_data.get('texto', '').strip()
        if not texto:
            raise forms.ValidationError("O comentário não pode estar vazio.")
        return texto