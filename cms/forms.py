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
        fields = ['title', 'sutian', 'text','editoria', 'creators']
        labels = {'title':'','sutian':'','creators': 'Autores','text': ''}

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['concept_to_add'].label = "Conceitos à adicionar"
        self.fields['title'].widget.attrs.update({'class' : 'title','placeholder' : 'Titulo'})
        self.fields['sutian'].widget.attrs.update({'class' : 'sutian','placeholder' : 'Sutian'})
        self.fields['creators'].widget.attrs.update({'class' : 'creators'})
        self.fields['text'].widget.attrs.update({'class' : 'text','placeholder' : 'Texto'})
        self.fields['editoria'].widget.attrs.update({'class' : 'editoria','placeholder' : 'Texto'})
        self.fields['concept_to_add'].widget.attrs.update({'class' : 'concept_to_add'})

class ArticleSearchForm(forms.Form):

    titulo = forms.CharField(label='Título', max_length=100)
    
    class Meta:
        model = Artigo
        fields = []




