from django import forms
from .models import Comentario, TipoTarefa, Sistema, Tarefa, Equipe
from django.contrib.auth.models import User
from django.forms.widgets import DateInput

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
    class Meta:
        model = Tarefa
        fields = ['titulo', 'tipo', 'sistema', 'atribuido_para', 'prazo', 'status', 'documentacao']
        widgets = {
            'prazo': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'documentacao': forms.Textarea(attrs={'rows': 4}),
        }

def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)

    if user:
        equipe = user.perfil.equipe
        self.fields['tipo'].queryset = TipoTarefa.objects.filter(equipe=equipe)
        self.fields['sistema'].queryset = Sistema.objects.filter(equipe=equipe)
        self.fields['atribuido_para'].queryset = User.objects.filter(perfil__equipe=equipe)

    if kwargs.get('instance'):
        self.fields['tipo'].disabled = True

    self.fields['prazo'].input_formats = ['%Y-%m-%d']


class RegistroForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)
    repetir_senha = forms.CharField(widget=forms.PasswordInput)

    # Opção: criar ou entrar em equipe
    criar_nova_equipe = forms.BooleanField(
        required=False,
        label="Criar nova equipe?"
    )

    nome_equipe = forms.CharField(required=False)
    descricao_equipe = forms.CharField(widget=forms.Textarea, required=False)
    codigo_acesso = forms.CharField(required=False, label="Código da equipe")

    class Meta:
        model = User
        fields = ['username', 'email', 'senha', 'repetir_senha']

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        repetir_senha = cleaned_data.get("repetir_senha")

        if senha != repetir_senha:
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