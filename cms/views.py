from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.utils import timezone
from django.db.models import Max

from cms.forms import ArticleForm,ArticleSearchForm
from cms.models import Artigo,Recurso,Tripla,Namespace,Publicado

import datetime
import rdflib as rdf
        
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
    
    def get_context_data(self, **kwargs):

        return dict(
            super(ArticleUpdateView, self).get_context_data(**kwargs),
            related_articles=Artigo.objects.all()[0:10],
            related_concepts=Recurso.objects.filter(pk__in=Tripla.objects.filter(artigo=self.kwargs['pk']).values('objeto'))
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.request.POST.get("annotate"):
            self.object.annotate()
        elif(self.request.POST.get("add_concept")):
            self.object.save(concepts=(self.request.POST.getlist('concepts') + [form.cleaned_data['concept_to_add'].pk]))
        elif(self.request.POST.get("publish")):
            self.object.publish(html=render_to_string(template_name=self.template_name,context=self.get_context_data()))
        else:
            self.object.save(concepts=(self.request.POST.getlist('concepts')))

        return HttpResponseRedirect(self.object.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleUpdateView, self).dispatch(request, *args, **kwargs)


class ArticleDeleteView(DeleteView):
    model = Artigo

    def get_success_url(self):
        return reverse('post-index')  # Or whatever you need

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleDeleteView, self).dispatch(request, *args, **kwargs)

class ArticleSearchView(ListView):
    
    template_name = 'cms/artigo_publish_search.html'
    #form_class = ArticleSearchForm
    #model = Artigo

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
      
        #context['article_data'] = zip(list(published_articles),list(publish_set))
        context['artigos'] = self.get_queryset()
        print(context['artigos'])
        return context

    def get_queryset(self):
        
        #form = self.form_class(self.request.GET)
        query = self.request.GET.get('q')

        if query:
            print(query)
            published_articles = Artigo.objects.filter(pk__in=Publicado.objects.all().values('artigo')).order_by('pk')
            publish_set = Publicado.objects.none()
            print(publish_set)
            for i in published_articles:
                last_publish_date = Publicado.objects.filter(artigo=i).aggregate(Max('data'))
                publish_set.union(Publicado.objects.filter(artigo=i).filter(data=last_publish_date['data__max']))
            print(publish_set)
            return Artigo.objects.filter(pk__in=publish_set.values('artigo')).filter(title__icontains=query)
            return Artigo.objects.filter(title__icontains=query)
        
        return Artigo.objects.all()
        
def PublishedArticle(request):

    published = Publicado.objects.filter(id=self.kwargs['pk']).values('html')
    context = {'published': published}

    return render(request, 'cms/published.html', context)

