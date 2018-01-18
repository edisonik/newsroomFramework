from django.forms import ModelForm
from cms.models import Artigo
from kms.views import kms

OPERATOR_CHOICES = (
    ('1', 'AND'),
    ('2', 'OR'),
)

def get_my_choices():
    # you place some logic here
    return choices_list


class ArticleForm(ModelForm):
    class Meta:
        model = Artigo
        fields = ['title', 'sutian', 'creators', 'text','semanticAnnotationsPath','relatedTexts','editoria']

class SemanticSearchForm(forms.Form):
    search_field1 = forms.ChoiceField(choices=get_choices())
    operator_field1 = forms.ChoiceField(choices=OPERATOR_CHOICES)
    search_field2 = forms.ChoiceField(choices=get_choices())
    operator_field2 = forms.ChoiceField(choices=OPERATOR_CHOICES)
    search_field3 = forms.ChoiceField(choices=get_choices())



