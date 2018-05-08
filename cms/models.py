from django.db import models
from django.urls import reverse
from django import forms
from django.contrib.postgres.fields import ArrayField
from django.forms import SelectMultiple
from django_mysql.models import ListTextField
from django.core.files import File
from django.db.models import Max,Count
from django.utils.html import strip_tags

from ckeditor.fields import RichTextField
from newsroomFramework.settings import PROJECT_ROOT
from cms.annotator import Annotator

from datetime import datetime 

import os
import MySQLdb
import ontospy 
import bleach

class Creator(models.Model):
    name = models.CharField(max_length=50)
    email = models.URLField()

    def __str__(self):
        return self.name

class Editoria(models.Model):
    topico = models.CharField(max_length=30) #vide iptc media topics

    def __str__(self):
        return self.topico

class Artigo(models.Model):

    title = models.CharField(max_length=150)
    sutian = models.CharField(max_length=150,blank=True)
    text = RichTextField(config_name='default', verbose_name=u'Matéria', default="")
    editoria = models.ManyToManyField(Editoria)
    creators = models.ManyToManyField(Creator)
    concepts_to_annotate = set()

    a = Annotator()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-edit', args=[self.id])

    def get_last_publish(self):
        last_publish_date = Publicado.objects.filter(artigo=self.id).aggregate(Max('data'))
        return(Publicado.objects.filter(artigo=self.id).filter(data=last_publish_date['data__max']).get())
    
    def get_last_publish_url(self):
        return(self.get_last_publish().get_absolute_url())

    def save(self, *args, **kwargs):
        try:
            concepts_list = kwargs.pop('concepts')
            self.update_annotations_in_db(concepts_list)
        except KeyError:
            pass
            
        super(Artigo, self).save(*args, **kwargs)

    def update_annotations_in_db(self,concepts_to_annotate_list):

        article_obj = Artigo.objects.get(pk=self.id)
        actual_concepts = Recurso.objects.filter(pk__in=Tripla.objects.filter(artigo=article_obj).values('objeto'))

        concepts_to_annotate_queryset = Recurso.objects.filter(pk__in=concepts_to_annotate_list)
        triples_to_delete_queryset = Tripla.objects.filter(objeto__in=actual_concepts).filter(artigo=article_obj).exclude(pk__in=concepts_to_annotate_queryset)
    
        #Não se deleta todas de uma vez devido ao bug do erro 1093 do mysql
        for i in triples_to_delete_queryset:
            i.delete()

        for i in concepts_to_annotate_queryset.exclude(pk__in=actual_concepts).values_list('uri',flat=True):
            d = Tripla.objects.create(artigo=self,predicado=Recurso.objects.get(uri='<Property *http://purl.org/ao/hasTopic*>'),objeto=Recurso.objects.get(uri=i))
            d.save()

    def annotate(self, *args, **kwargs):
        
        super(Artigo, self).save(*args, **kwargs)
        f = open('../newsroomFramework/newsroomFramework/namespace.owl', 'w')
        ns = File(f)
        ns.write(Namespace.objects.get(pk=1).rdf)
        ns.close()
        onto = ontospy.Ontospy(os.path.join(PROJECT_ROOT, 'namespace.owl'))
        ns.close()

        web_concepts = self.a.get_reifications(onto)
        concepts_dict = self.a.uri_to_text(self.a.zika_ontology_uri_to_text,web_concepts)
        reifications_to_annotate = [concepts_dict[' '.join(i)] for i in self.a.get_article_concepts(concepts_dict.keys(),self.text)]
        self.concepts_to_annotate.clear()
        self.a.add_related_concepts(reifications_to_annotate,self.concepts_to_annotate)
        self.update_annotations_in_db(Recurso.objects.filter(uri__in=list(self.concepts_to_annotate)).values_list('pk',flat=True))
    
    def publish(self, *args, **kwargs):
        #pega html da página e faz um saneamento retiirando caracteres indesejados
        html = kwargs.pop('html').replace('\n','').replace('\r','')

        try:
            last_publish = Publicado.objects.get(artigo=Artigo.objects.get(pk=self.id)).order_by('-data')[:1]
            f = open('../newsroomFramework/newsroomFramework/base.rdf', 'w')
            ns = File(f)
            ns.write(last_publish.rdf_annotation)
            ns.close()
        except Exception as e:
            print(e)
        concepts_to_annotate_list = [x.split('*')[1] for x in Recurso.objects.filter(pk__in=Tripla.objects.filter(artigo=Artigo.objects.get(pk=self.id)).values('objeto')).values_list('uri',flat=True)]
        self.a.update_graph(os.path.join(PROJECT_ROOT, str(self.id) + '.rdf'),self.get_absolute_url(),concepts_to_annotate_list,self.creators.all().values_list('name',flat=True)).serialize(format='xml',destination = os.path.join(PROJECT_ROOT, str(self.id) + '.rdf'))
        
        p = Publicado.objects.create(artigo = self,html = html ,rdf_annotation = open(os.path.join(PROJECT_ROOT, str(self.id) + '.rdf'),'r').read())
        p.save() 

class Publicado(models.Model):
    artigo = models.ForeignKey(Artigo,on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
    html = models.TextField(verbose_name=u'html', max_length=None)
    rdf_annotation = models.TextField(verbose_name=u'rdf_annotation', max_length=None)

    def get_absolute_url(self):
        return reverse('article-publish', args=[self.id])

class Namespace(models.Model):
    ns_ref = models.TextField(verbose_name=u'ref', max_length=None)
    rdf = models.TextField(verbose_name=u'rdf', max_length=None)

class Recurso(models.Model):
    namespace = models.ForeignKey(Namespace,null=True, on_delete=models.SET_NULL)
    uri = RichTextField(verbose_name=u'uri')
    valor = RichTextField(verbose_name=u'valor')

class Tripla(models.Model):
    artigo = models.ForeignKey(Artigo,on_delete=models.CASCADE)
    predicado = models.ForeignKey(Recurso,on_delete=models.CASCADE,related_name='predicado')
    objeto = models.ForeignKey(Recurso,on_delete=models.CASCADE,related_name='objeto')

