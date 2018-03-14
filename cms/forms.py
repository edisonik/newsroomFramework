from django.forms import ModelForm
from django import forms
from cms.models import Artigo,Recurso
from kms.views import kms

OPERATOR_CHOICES = (
    ('1', 'AND'),
    ('2', 'OR'),
)

def get_choices():
    # you place some logic here
    choices_list = []
    return choices_list



class ResourceChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return '{valor} {uri}'.format(valor=obj.valor, uri=obj.uri)
        

class ArticleForm(ModelForm):

    concept_to_add = ResourceChoiceField(queryset=Recurso.objects.all(),empty_label=None)

    class Meta:
        model = Artigo
        fields = ['title', 'sutian', 'creators', 'text','editoria']

class SemanticSearchForm(forms.Form):
    search_field1 = forms.ChoiceField(choices=get_choices())
    operator_field1 = forms.ChoiceField(choices=OPERATOR_CHOICES)
    search_field2 = forms.ChoiceField(choices=get_choices())
    operator_field2 = forms.ChoiceField(choices=OPERATOR_CHOICES)
    search_field3 = forms.ChoiceField(choices=get_choices())



