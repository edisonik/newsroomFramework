from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views import generic
from cms.forms import ArticleForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

import datetime
import rdflib as rdf

from cms.models import Artigo

# Create your views here.
def jornal(request):
    edicao_dados = []
    #edicao_dados.append( datetime.datetime.now())
    artigo = Artigo.objects.all()
    edicao_dados.append( artigo[0].title )
    edicao_dados.append(artigo[0].sutian)
    edicao_dados.append(artigo[0].text)
    context = {'edicao_dados': edicao_dados}

    return render(request, 'cms/pagina1.html', context )
    #return render(request, 'cms/index.html', {'edicao_dados': edicao_dados} )

def rdf(request):

    return render(request, 'rdf.html')

def form(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        '''if request.POST.get("Salvar"):
            #if form.is_valid():
                #Aqui deve salvar o formulário
                #return HttpResponseRedirect('/contact/thanks/')'''
    else:
        form = ArticleForm()
    return render(request, 'cms/article_form.html', {'form': form})
    


class ArticleCreateView(CreateView):
    model = Artigo
    form_class = ArticleForm
    template_name = 'cms/article_form.html'
    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.request.POST.get("annotate"):
            self.object.annotate() 
        else:
            self.object.save()
        return HttpResponseRedirect(self.object.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleCreateView, self).dispatch(request, *args, **kwargs)


class ArticleUpdateView(UpdateView):
    model = Artigo
    form_class = ArticleForm
    template_name = 'cms/article_form.html'
    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.request.POST.get("annotate"):
            self.object.annotate()
        else:
            self.object.save()
        return HttpResponseRedirect(self.object.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleUpdateView, self).dispatch(request, *args, **kwargs)


class ArticleDeleteView(DeleteView):
    model = Artigo

    def get_success_url(self):
        return reverse('post-index')  # Or whatever you need

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleDeleteView, self).dispatch(request, *args, **kwargs)

