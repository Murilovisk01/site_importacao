from django import forms
from .models import Comentario, Implatacao, RegistroTempo, SistemaExterno, TempoSistemaExterno, TipoTarefa, Sistema, Tarefa
from django.contrib.auth.models import User
from django.forms.widgets import DateInput
from django.forms import inlineformset_factory
from django.contrib.auth.forms import PasswordChangeForm
from dal import autocomplete
from django.forms import modelformset_factory
from datetime import timedelta

class TipoTarefaForm(forms.ModelForm):
    class Meta:
        model = TipoTarefa
        fields = ['nome','titulo_padrao', 'roteiro']

class SistemaForm(forms.ModelForm):
    ICONES_CHOICES = [
        ('amazonrds.png', 'Amazon RDS'),
        ('amazonaurora.png', 'Amazon Aurora'),
        ('cassandra.png', 'Cassandra'),
        ('couchdb.png', 'CouchDB'),
        ('dbf.png', 'DBF'),
        ('dynamodb.png', 'DynamoDB'),
        ('elasticsearch.png', 'Elasticsearch'),
        ('firebase.png', 'Firebase'),
        ('firebird.png', 'Firebird'),
        ('googlecloudsql.png', 'Google Cloud SQL'),
        ('ibmdb2.png', 'IBM Db2'),
        ('informix.png', 'Informix'),
        ('mariadb.png', 'MariaDB'),
        ('mongodb.png', 'MongoDB'),
        ('mysql.png', 'MySQL'),
        ('neo4j.png', 'Neo4j'),
        ('oracle.png', 'Oracle'),
        ('postgresql.png', 'PostgreSQL'),
        ('redis.png', 'Redis'),
        ('snowflake.png', 'Snowflake'),
        ('sqlite.png', 'SQLite'),
        ('sqlserver.png', 'SQL Server'),
    ]

    icone = forms.ChoiceField(choices=ICONES_CHOICES, required=False)

    class Meta:
        model = Sistema
        fields = ['nome', 'data_mapeamento', 'data_ultima_atualizacao', 'base_dados', 'link', 'icone', 'criado_por']
        widgets = {
            'data_mapeamento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_ultima_atualizacao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in ['data_mapeamento', 'data_ultima_atualizacao']:
            if self.instance and getattr(self.instance, campo):
                self.initial[campo] = getattr(self.instance, campo).strftime('%Y-%m-%d')

class TarefaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Retira o argumento 'user'
        super().__init__(*args, **kwargs)

        self.fields['tipo'].queryset = TipoTarefa.objects.all().order_by('nome')
        self.fields['sistema'].queryset = Sistema.objects.all().order_by('nome')
        self.fields['atribuido_para'].queryset = User.objects.all().order_by('username')
        self.fields['implatador'].queryset = Implatacao.objects.filter(cargo='implantador').order_by('nome')
        self.fields['analista'].queryset = Implatacao.objects.filter(cargo='analista').order_by('nome')

        if kwargs.get('instance'):
            self.fields['tipo'].disabled = True
        self.fields['prazo'].input_formats = ['%Y-%m-%d']

    class Meta:
        model = Tarefa
        fields = [
            'titulo', 'tipo', 'sistema', 'atribuido_para', 'prazo', 'status',
            'documentacao', 'link_glpi', 'link_redmine', 'analista', 'implatador',
            'usou_sistema_externo'
        ]
        widgets = {
            'prazo': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'documentacao': forms.Textarea(attrs={'rows': 4}),
            'link_glpi': forms.TextInput(attrs={'placeholder': 'URL GLPI'}),
            'link_redmine': forms.TextInput(attrs={'placeholder': 'URL Redmine'}),
            'usou_sistema_externo': forms.Select(attrs={
                'class': 'form-select',
            }),
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

class ImplantacaoForm(forms.ModelForm):
    class Meta:
        model = Implatacao
        fields = ['nome', 'cargo']

class FiltroRegistroTempoForm(forms.Form):
    data_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    tarefa = forms.ModelChoiceField(queryset=Tarefa.objects.all(), required=False, empty_label="Todas as tarefas")

class RegistroTempoForm(forms.ModelForm):
    class Meta:
        model = RegistroTempo
        fields = ['tarefa', 'inicio', 'fim']
        widgets = {
            'tarefa': autocomplete.ModelSelect2(
                url='tarefa-autocomplete',
                attrs={'data-placeholder': 'Buscar tarefa...', 'class': 'form-control'}  # <-- aqui o ajuste
            ),
             'inicio': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'fim': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in ['inicio', 'fim']:
            if self.instance.pk and getattr(self.instance, campo):
                self.fields[campo].initial = getattr(self.instance, campo).strftime('%Y-%m-%dT%H:%M')

class SistemaExternoForm(forms.ModelForm):
    class Meta:
        model = SistemaExterno
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TempoSistemaExternoForm(forms.ModelForm):
    tempo_corrido = forms.CharField(
        label="Tempo Gasto (hh:mm)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 01:30'})
    )

    class Meta:
        model = TempoSistemaExterno
        fields = ['sistema', 'tempo_corrido']

    def clean_tempo_corrido(self):
        data = self.cleaned_data['tempo_corrido']
        try:
            horas, minutos = map(int, data.split(':'))
            return timedelta(hours=horas, minutes=minutos)
        except:
            raise forms.ValidationError("Informe o tempo no formato hh:mm (ex: 01:30)")
