from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse
from django.views.generic.list import ListView
from django.utils import timezone
from django.db.models import Max

from cms.forms import ArticleForm,ArticleSearchForm
from cms.models import Artigo,Recurso,Tripla,Namespace,Publicado

import datetime
import re
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
    @staticmethod
    def infix_to_posfix(exp,**oprtrs):

        stack = list()
        out = list()
        oprtrs_keys = oprtrs.keys()
        for o in exp:
            if o in oprtrs_keys:
                if stack:
                    op = stack.pop(0)
                    while op != '(' and oprtrs[op] >= oprtrs[o] and stack:                    
                        out.append(op)
                        op = stack.pop(0)
                stack.insert(0,o)
            elif o == '(':
                stack.insert(0,o)
            elif o == ')':
                op = stack.pop(0)
                while op != '(' and stack:
                    out.append(op)
                    op = stack.pop(0)
                out.append(op)
                out.append(o)
            else:
                out.append(o)
        while stack:
            op = stack.pop(0)
            out.append(op)

        return(out)
    @staticmethod
    def process_posfix(exp,oprtrs_keys):
        stack = list()
        for o in exp:
            if o not in oprtrs_keys:
                stack.insert(0,o)
            else:
                lo = stack.pop(0)
                ro = stack.pop(0)
                if o == '&':
                    result = lo & ro
                elif o == '|':
                    result = lo | ro
                else:
                    print("Operador desconhecido")
                    return(queryset)

                stack.insert(0,result)
                
        return(stack.pop(0))
         
    def make_set(self,field_dict,queryset,q_filter):
        oprtrs= {'&':1,'|':0}
        for field_type, field in field_dict.items():
            if field:
                quoteds = re.findall(r'"[^"]*"', field)
                if quoteds:
                    splited = list()
                    field_pos = 0          
                    for s in quoteds:
                        quo_pos = field.find(s)
                        splited.extend(field[field_pos:quo_pos].split(' '))
                        splited.extend(s[1:-1])
                        field_pos = quo_pos + len(s)
                    splited.extend(field[field_pos:].split(' '))
                else:
                    splited = field.split(' ')
               
                operators_dict = { i:x for i,x in enumerate(splited) if x == '&' or x == '|' or x == '(' or x == ')' }
                operators_dict_keys = list(operators_dict.keys())

                if operators_dict_keys:
                    query_position = operator_keys_pos = 0
                    dict_lenght = len(operators_dict_keys)
                    expression = list()
                    while operator_keys_pos < dict_lenght:
                        operator_position = operators_dict_keys[operator_keys_pos] 

                        q_args = {'{0}__{1}'.format(field_type, q_filter):''.join(splited[query_position:operator_position])}
                
                        expression.append(queryset.filter(**q_args))
                        expression.append(operators_dict[operator_position]) 

                        query_position = operator_position + 1
                        operator_keys_pos += 1

                    q_args = {'{0}__{1}'.format(field_type, q_filter):''.join(splited[query_position:operator_position])}
                    expression.append(queryset.filter(**q_args))
                    queryset = self.process_posfix(self.infix_to_posfix(expression,**oprtrs),list(oprtrs.keys()))
                else:
                    q_args = {'{0}__{1}'.format(field_type, q_filter):''.join(splited)}
                    queryset = queryset.filter(**q_args)

        print(queryset)
        return(queryset)
                
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
      
        #context['article_data'] = zip(list(published_articles),list(publish_set))
        context['artigos'] = self.get_queryset()
        #print(context['artigos'])
        return context

    def get_queryset(self):
        
        field_dict = dict()
        field_dict['title'] = self.request.GET.get('t') 
        field_dict['sutian'] = self.request.GET.get('s')
        field_dict['valor'] = self.request.GET.get('c')
        field_dict['uri'] = self.request.GET.get('u')
        field_dict['topico'] = self.request.GET.get('e')
        field_dict['name'] = self.request.GET.get('a')
        
        if field_dict.values():

            published_articles = Artigo.objects.filter(pk__in=Publicado.objects.all().values('artigo')).order_by('pk')
            publish_set = Publicado.objects.none()
            for i in published_articles:
                last_publish_date = Publicado.objects.filter(artigo=i).aggregate(Max('data'))
                publish_set = publish_set | Publicado.objects.filter(artigo=i).filter(data=last_publish_date['data__max'])

            if field_dict['title'] or field_dict['sutian']:
                q_article = self.make_set({k: field_dict[k] for k in ('title', 'sutian')},Artigo.objects.filter(pk__in=publish_set.values('artigo')),'icontains')
            else:
                q_article = Artigo.objects.filter(pk__in=publish_set.values('artigo'))

            if field_dict['recurso']:
                q_recurso = self.make_set({k: field_dict[k] for k in ('valor','uri')},Recurso.objects.all(),'icontains')
                q_article = q_article | q_article.filter(pk__in=Tripla.objects.filter(objeto__in=q_recurso).values('artigo'))

            if field_dict['topico']:
                q_editorias = self.make_set({k: field_dict[k] for k in ('topico')},Editoria.objects.all(),'icontains')
                q_article = q_article.filter(editoria__in=q_editorias)
                
            if field_dict['name']:
                q_creators = self.make_set({k: field_dict[k] for k in ('creator')},Creator.objects.all(),'icontains')
                q_article = q_article.filter(editoria__in=q_editorias)

            return(q_article)

        return Artigo.objects.all()
        
def PublishedArticle(request):

    published = Publicado.objects.filter(id=self.kwargs['pk']).values('html')
    context = {'published': published}

    return render(request, 'cms/published.html', context)

