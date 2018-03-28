from django.forms import ModelForm
from django import forms
from cms.models import Artigo,Recurso
from kms.views import kms

class ResourceChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return '{valor} {uri}'.format(valor=obj.valor, uri=obj.uri)
        

class ArticleForm(ModelForm):

    concept_to_add = ResourceChoiceField(queryset=Recurso.objects.all(),empty_label=None)

    class Meta:
        model = Artigo
        fields = ['title', 'sutian', 'creators', 'text','editoria']

class ArticleSearchForm(forms.Form):

    titulo = forms.CharField(label='Título', max_length=100)
    
    class Meta:
        model = Artigo
        fields = []




