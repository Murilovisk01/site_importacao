from django import forms
from .models import Comentario, Implatacao, TipoTarefa, Sistema, Tarefa
from django.contrib.auth.models import User
from django.forms.widgets import DateInput
from django.forms import inlineformset_factory
from django.contrib.auth.forms import PasswordChangeForm

class TipoTarefaForm(forms.ModelForm):
    class Meta:
        model = TipoTarefa
        fields = ['nome','titulo_padrao', 'roteiro']

class SistemaForm(forms.ModelForm):
    class Meta:
        model = Sistema
        fields = ['nome', 'data_mapeamento', 'base_dados', 'icone']
        widgets = {
            'data_mapeamento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define o valor inicial formatado corretamente para edição
        if self.instance and self.instance.pk and self.instance.data_mapeamento:
            self.initial['data_mapeamento'] = self.instance.data_mapeamento.strftime('%Y-%m-%d')

class TarefaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Retira o argumento 'user'
        super().__init__(*args, **kwargs)

        self.fields['tipo'].queryset = TipoTarefa.objects.all()
        self.fields['sistema'].queryset = Sistema.objects.all()
        self.fields['atribuido_para'].queryset = User.objects.all()
        self.fields['implatador'].queryset = Implatacao.objects.filter(cargo='implantador')
        self.fields['analista'].queryset = Implatacao.objects.filter(cargo='analista')

        if kwargs.get('instance'):
            self.fields['tipo'].disabled = True
        self.fields['prazo'].input_formats = ['%Y-%m-%d']

    class Meta:
        model = Tarefa
        fields = [
            'titulo', 'tipo', 'sistema', 'atribuido_para', 'prazo', 'status',
            'documentacao', 'link_glpi', 'link_redmine', 'analista', 'implatador'
        ]
        widgets = {
            'prazo': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'documentacao': forms.Textarea(attrs={'rows': 4}),
            'link_glpi': forms.TextInput(attrs={'placeholder': 'URL GLPI'}),
            'link_redmine': forms.TextInput(attrs={'placeholder': 'URL Redmine'}),
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
    
class MinhaContaForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

