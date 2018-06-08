from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse
from django.views.generic.list import ListView
from django.utils import timezone
from django.db.models import Count,Q,F,Case,When

from cms.forms import ArticleForm,ArticleSearchForm
from cms.models import Artigo,Recurso,Tripla,Namespace,Publicado,Editoria,Creator
from cms.annotator import Annotator
from newsroomFramework.settings import PROJECT_ROOT

import datetime
import re
import rdflib as rdf
import ontospy
import os
        
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
            form.save_m2m()
        return HttpResponseRedirect(self.object.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleCreateView, self).dispatch(request, *args, **kwargs)

class ArticleUpdateView(UpdateView):
    model = Artigo
    form_class = ArticleForm
    template_name = 'cms/article_form.html'

    def get_related_articles(self):
              
        article_concepts = Recurso.objects.filter(pk__in=Tripla.objects.filter(artigo=Artigo.objects.get(pk=self.kwargs['pk'])).values('objeto'))
        #********************************************************************************************************************
        #Primeira opção
        '''
        published_related = Artigo.objects.filter(pk__in=Tripla.objects.filter(objeto__in=article_concepts)\
                            .values('artigo')).filter(pk__in=Publicado.objects.all().values('artigo')).exclude(pk=self.kwargs['pk'])\
                            .annotate(qt_related=Count('tripla__pk',filter=Q(tripla__objeto__in=article_concepts))).order_by('-qt_related')
        return(published_related)'''

        #********************************************************************************************************************
        #segunda opção
        a = Annotator()
        onto = ontospy.Ontospy(os.path.join(PROJECT_ROOT, 'namespace.owl'))
        # Não se pode usar uma função python em uma agregação (como no codigo comentado a seguir) e não consegui criar minha própria 
        # função de agragação para uma função que não tenha correspondência no sql do banco e portanto resolvo o problema com dois loops
        # como segue(nada eficiente)
        '''published_related = Artigo.objects.filter(pk__in=Tripla.objects.filter(objeto__in=article_concepts)\
                            .values('artigo')).filter(pk__in=Publicado.objects.all().values('artigo')).exclude(pk=self.kwargs['pk'])\
                            .annotate(qt_bro=self.get_brothers_aggregation(F('pk'),self.kwargs['pk'])).order_by('qt_bro')'''

        annotated_published = Artigo.objects.filter(pk__in=Tripla.objects.all().values('artigo')).filter(pk__in=Publicado.objects.all().values('artigo')).exclude(pk=self.kwargs['pk'])

        ordered_related_list = list()
        set_a = article_concepts.values_list('uri',flat=True)
        
        for i in annotated_published:
            set_b = Recurso.objects.filter(pk__in=Tripla.objects.filter(artigo=i).values('objeto')).values_list('uri',flat=True)
        
            ordered_related_list.append((i,a.get_number_of_brothers(set_a,set_b,onto)))

        ordered_related_list = sorted(ordered_related_list, key=lambda x: x[1], reverse=True)
        
        pk_list = [x[0].id for x in ordered_related_list]

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)]) # Fucking elegant!
        published_related = Artigo.objects.filter(pk__in=pk_list).order_by(preserved)

        return(published_related)

    def get_context_data(self, **kwargs):

        return dict(
            super(ArticleUpdateView, self).get_context_data(**kwargs),
            related_articles=self.get_related_articles()[:5],
            related_concepts=Recurso.objects.filter(pk__in=Tripla.objects.filter(artigo=self.kwargs['pk']).values('objeto')),
            editor=Artigo.objects.get(pk=self.kwargs['pk']).editoria.all(),
            autors=Artigo.objects.get(pk=self.kwargs['pk']).creators.all()
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.request.POST.get("annotate"):
            self.object.annotate()
        elif(self.request.POST.get("add_concept")):
            self.object.save(concepts=(self.request.POST.getlist('concepts') + [form.cleaned_data['concept_to_add'].pk]))
        elif(self.request.POST.get("publish")):
            self.object.publish(html=render_to_string(template_name='cms/published.html',context=self.get_context_data()))
        else:
            self.object.save(concepts=(self.request.POST.getlist('concepts')))
            form.save_m2m()

        return HttpResponseRedirect(self.object.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleUpdateView, self).dispatch(request, *args, **kwargs)

class ArticleDeleteView(DeleteView):
    model = Artigo

    def get_success_url(self):
        return reverse('post-index')  # Or whatever you need

    def dispatch(self, request, *args, **kwargs):
        return super(ArticleDeleteView, self).dispatch(request, *args, **kwargs)

class ArticleListView(ListView):
	template_name = 'cms/artigo_list.html'
	model = Artigo
	
	def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            return context

class ArticleSearchView(ListView):

    template_name = 'cms/artigo_publish_search.html'
    
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

    @staticmethod
    def split_expression(expression,operators):
        word = ''
        splited = list()
        for i in expression:
            if i in operators:
                if word != '':
                    splited.append(word)
                    word = ''
                splited.append(i)
            elif i == ' ':
                if word != '':
                    splited.append(word)
                word = ''
            else:
                word += i
        if word != '':
            splited.append(word)

        return(splited)
                
        
    def make_set(self,field_dict,queryset,q_filter,acumulator):
        oprtrs= {'&':1,'|':0}
        acc = Artigo.objects.none()
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
                    splited = self.split_expression(field,['|','&','(',')'])
                operators_dict = { i:x for i,x in enumerate(splited) if x == '&' or x == '|' or x == '(' or x == ')' }
                operators_dict_keys = list(operators_dict.keys())

                if operators_dict_keys:
                    query_position = operator_keys_pos = 0
                    dict_lenght = len(operators_dict_keys)
                    expression = list()

                    while operator_keys_pos < dict_lenght:
                        operator_position = operators_dict_keys[operator_keys_pos] 
                        if ''.join(splited[query_position:operator_position]) != '' :
                            q_args = {'{0}__{1}'.format(field_type, q_filter):''.join(splited[query_position:operator_position])}
                            expression.append(queryset.filter(**q_args))
                        expression.append(operators_dict[operator_position]) 

                        query_position = operator_position + 1
                        operator_keys_pos += 1
                    #print(expression)
                    if ''.join(splited[query_position:]) != '' :
                        q_args = {'{0}__{1}'.format(field_type, q_filter):''.join(splited[query_position:])}
                        expression.append(queryset.filter(**q_args))
                    #print(expression)
                    #print(self.process_posfix(self.infix_to_posfix(expression,**oprtrs),list(oprtrs.keys())))
                    acumulator = acumulator | self.process_posfix(self.infix_to_posfix(expression,**oprtrs),list(oprtrs.keys()))
                else:
                    q_args = {'{0}__{1}'.format(field_type, q_filter):''.join(splited)}
                    acumulator = queryset.filter(**q_args) | acumulator
        return(acumulator)
                
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['artigos'] = self.get_queryset()

        return context

    def get_queryset(self):
        
        field_dict = dict()
        field_dict['title'] = self.request.GET.get('t') 
        field_dict['sutian'] = self.request.GET.get('s')
        field_dict['valor'] = self.request.GET.get('c')
        field_dict['uri'] = self.request.GET.get('u')
        field_dict['topico'] = self.request.GET.get('e')
        field_dict['name'] = self.request.GET.get('a')

        published_articles = Artigo.objects.filter(pk__in=Publicado.objects.all().values('artigo')).order_by('pk')

        if [f for f in field_dict.values() if f != '' and f != None]:

            q_article = Artigo.objects.none()

            if field_dict['title'] or field_dict['sutian']:
                q_article = self.make_set({k:field_dict[k] for k in('title','sutian')},published_articles,'icontains',Artigo.objects.none())

            if field_dict['valor']:
                q_recurso = self.make_set({k:field_dict[k] for k in('valor','uri')},Recurso.objects.all(),'icontains',Recurso.objects.none())
                q_article = q_article | published_articles.filter(pk__in=Tripla.objects.filter(objeto__in=q_recurso).values('artigo'))

            if field_dict['topico']:
                q_editorias = self.make_set({'topico': field_dict['topico']},Editoria.objects.all(),'icontains',Editoria.objects.none())
                q_article = q_article | published_articles.filter(editoria__in=q_editorias)
                
            if field_dict['name']:
                q_creators = self.make_set({'name': field_dict['name']},Creator.objects.all(),'icontains',Creator.objects.none())
                q_article = q_article | published_articles.filter(creators__in=q_creators)

            return(q_article)

        return published_articles
        
def PublishedArticle(request,**kwargs):

    published = Publicado.objects.filter(pk=kwargs['pk']).values('html')
    context = {'published': published}

    return render(request, 'cms/only_render.html', context)

def PublishedRdf(request,**kwargs):

    published = Publicado.objects.filter(pk=kwargs['pk']).values('rdf_annotation')
    response = HttpResponse(published[0]['rdf_annotation'], content_type="application/rdf+xml")
    response['Content-Disposition'] = 'inline ; filename=' + 'article.rdf'
    return response

def Menu(request,**kwargs):

    if request.POST.get("artigos_lists"):
        return HttpResponseRedirect(reverse('article-list'))
    elif request.POST.get("publish_search"):
        return HttpResponseRedirect(reverse('article-search'))
    elif request.POST.get("new_article"):
        return HttpResponseRedirect(reverse('article-add'))
    
    return render(request, 'cms/menu.html')


