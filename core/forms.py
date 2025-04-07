from django import forms
from .models import Comentario, TipoTarefa, Sistema, Tarefa, Equipe
from django.contrib.auth.models import User

class TipoTarefaForm(forms.ModelForm):
    class Meta:
        model = TipoTarefa
        fields = ['nome','titulo_padrao', 'roteiro']

class SistemaForm(forms.ModelForm):
    class Meta:
        model = Sistema
        fields = ['nome']

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'tipo', 'sistema', 'atribuido_para', 'prazo', 'status', 'documentacao']
        widgets = {
            'prazo': forms.DateInput(attrs={'type': 'date'}),
            'documentacao': forms.Textarea(attrs={'rows': 4}),
        }

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