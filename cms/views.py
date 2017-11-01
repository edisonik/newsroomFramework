from django.shortcuts import get_object_or_404, render
from django.views import generic
import datetime
import rdflib as rdf

from cms.models import Artigo

# Create your views here.
def jornal(request):
    edicao_dados = []
    #edicao_dados.append( datetime.datetime.now() )
    artigo = Artigo.objects.all()
    edicao_dados.append( artigo[0].title )
    edicao_dados.append(artigo[0].sutian)
    edicao_dados.append(artigo[0].text)
    context = {'edicao_dados': edicao_dados}

    return render(request, 'cms/pagina1.html', context )
    #return render(request, 'cms/index.html', {'edicao_dados': edicao_dados} )

def rdf(request):

    return render(request, 'rdf.html')