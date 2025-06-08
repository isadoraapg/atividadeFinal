from django import forms
from .models import Imovel, Cliente, User, FotoImovel, AnuncioImovel

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ImovelForm(forms.ModelForm):
    fotos = MultipleFileField(
        required=False,
        help_text='Selecione uma ou mais fotos'
    )
    
    class Meta:
        model = Imovel
        fields = [
            'titulo', 'descricao', 'localizacao', 'preco',
            'tipo_imovel', 'status_obra', 'area_total',
            'quartos', 'banheiros', 'vagas_garagem',
            'progresso_obra', 'data_previsao_entrega',
            'disponivel'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'data_previsao_entrega': forms.DateInput(attrs={'type': 'date'}),
            'progresso_obra': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'tipo_imovel': forms.Select(attrs={'class': 'form-select'}),
            'status_obra': forms.Select(attrs={'class': 'form-select'})
        }

class ClienteForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = Cliente
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'telefone', 'receber_notificacoes'
        ]
        widgets = {
            'receber_notificacoes': forms.CheckboxInput()
        }
    
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        cliente = super().save(commit=False)
        cliente.user = user
        if commit:
            cliente.save()
        return cliente

class AnuncioImovelForm(forms.ModelForm):
    class Meta:
        model = AnuncioImovel
        fields = ['titulo', 'descricao', 'imovel']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'imovel': forms.Select(attrs={'class': 'form-select'})
        }

class PreferenciasForm(forms.Form):
    localizacao = forms.CharField(max_length=200, required=False)
    tipo_imovel = forms.ChoiceField(choices=Imovel.TIPO_IMOVEL, required=False)
    preco_min = forms.DecimalField(max_digits=12, decimal_places=2, required=False)
    preco_max = forms.DecimalField(max_digits=12, decimal_places=2, required=False)
    quartos_min = forms.IntegerField(min_value=0, required=False)
    area_min = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    receber_notificacoes = forms.BooleanField(required=False) 