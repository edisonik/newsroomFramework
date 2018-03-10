from django.db import models
from django.urls import reverse
from django import forms
from django.contrib.postgres.fields import ArrayField
from django.forms import SelectMultiple
from django_mysql.models import ListTextField
from django.core.files import File

from ckeditor.fields import RichTextField
from newsroomFramework.settings import PROJECT_ROOT
from cms.annotator import Annotator

import os
import MySQLdb
import datetime
import ontospy 

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

    title = models.CharField(max_length=50)
    sutian = models.CharField(max_length=50)
    creators = models.ManyToManyField(Creator)
    text = RichTextField(config_name='default', verbose_name=u'Matéria', default="")
    editoria = models.ManyToManyField(Editoria)
    concepts_to_annotate = set()

    a = Annotator()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-edit', args=[self.id])

    def save(self, *args, **kwargs):
        concepts_list = kwargs.pop('concepts')
        print('Checkbox')
        print(concepts_list)
        self.update_annotations_in_db(concepts_list)
        super(Artigo, self).save(*args, **kwargs)

    def update_annotations_in_db(self,concepts_to_annotate_list):
        print("Argument List")
        print(concepts_to_annotate_list)
        actual_concepts = Recurso.objects.filter(pk__in=Tripla.objects.filter(artigo=Artigo.objects.get(pk=self.id)).values('objeto'))
        print('Actual concepts')
        print(actual_concepts)

        concepts_to_annotate_queryset = Recurso.objects.filter(pk__in=concepts_to_annotate_list)
        print('Concepts to annotate')
        print(concepts_to_annotate_queryset)
        triples_to_delete_queryset = Tripla.objects.filter(objeto__in=actual_concepts).exclude(pk__in=concepts_to_annotate_queryset)
        print('Concepts to delete')
        print(triples_to_delete_queryset)
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
      self.a.update_graph(os.path.join(PROJECT_ROOT, 'base.rdf'),self.get_absolute_url(),concepts_to_annotate_list,self.creators).serialize(format='xml',destination = os.path.join(PROJECT_ROOT, 'base.rdf'))  

class Publicado(models.Model):
    artigo = models.ForeignKey(Artigo)
    html = models.TextField(verbose_name=u'html', max_length=None)
    rdf_annotation = models.TextField(verbose_name=u'rdf_annotation', max_length=None)

class Namespace(models.Model):
    ns_ref = models.TextField(verbose_name=u'ref', max_length=None)
    rdf = models.TextField(verbose_name=u'rdf', max_length=None)

class Recurso(models.Model):
    namespace = models.ForeignKey(Namespace)
    uri = RichTextField(verbose_name=u'uri')
    valor = RichTextField(verbose_name=u'valor')

class Tripla(models.Model):
    artigo = models.ForeignKey(Artigo)
    predicado = models.ForeignKey(Recurso,related_name='predicado')
    objeto = models.ForeignKey(Recurso,related_name='objeto')






