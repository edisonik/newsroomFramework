from django.forms import ModelForm
from cms.models import Artigo
from kms.views import kms

class ArticleForm(ModelForm):
    class Meta:
        model = Artigo
        fields = ['title', 'sutian', 'creators', 'text','semanticAnnotationsPath','relatedTexts','editoria']



