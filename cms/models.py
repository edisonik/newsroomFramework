from django.db import models
from ckeditor.fields import RichTextField
import MySQLdb
import datetime
import rdflib
from rdflib import Graph,XSD,Literal,plugin,URIRef
from rdflib.namespace import Namespace,RDFS,RDF,FOAF
from rdflib.extras.describer import Describer
from rdflib.serializer import Serializer
import ontospy
import nltk
from nltk.tag import pos_tag
import urllib.request
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from bisect import bisect_left
import urllib
from urllib.parse import urlparse
import shutil
import os
import sys
import tempfile
from newsroomFramework.settings import PROJECT_ROOT
from django.urls import reverse
from django import forms

from django.contrib.postgres.fields import ArrayField
from django.forms import SelectMultiple
from django_mysql.models import ListTextField


class ArraySelectMultiple(SelectMultiple):

    def value_omitted_from_data(self, data, files, name):
        return False


class ChoiceArrayField(ArrayField):

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.TypedMultipleChoiceField,
            'choices': self.base_field.choices,
            'coerce': self.base_field.to_python,
            'widget': ArraySelectMultiple
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)
'''
    def db_type(self, connection):
        return None

   def from_db_value(self, value, expression, connection, context):
        #Aqui carrega do banco(arquivo base.rdf)
        if value is None:
            return value
        return parse_hand(value)

    def to_python(self, value):
        if isinstance(value, Hand):
            return value

        if value is None:
            return value

        return parse_hand(value)
'''

class Widget(models.Model):
    widget_group_ids = ListTextField(base_field=models.IntegerField(),size=100,)

class Annotator():

    @staticmethod
    def get_text_sentences(text):
        sentences = nltk.sent_tokenize(' '.join([i for i in text.split()]))
        return [nltk.word_tokenize(sent) for sent in sentences]

    @staticmethod
    def get_article_concepts(concept_text_list,text):#retorna lista de conceitos encontrados no texto
      
        sentences = Annotator.get_text_sentences(text)
        concepts_found = list()
        search_remaining_concepts = [nltk.word_tokenize(i) for i in concept_text_list]

        while len(search_remaining_concepts) > 0:
            biggest_concept_lenght = len(max(search_remaining_concepts,key = len))
            biggest_concept_items = [x for x in search_remaining_concepts if len(x) == biggest_concept_lenght]
            search_remaining_concepts = [x for x in search_remaining_concepts if x not in biggest_concept_items]
                
            for sentence in sentences:
                if len(sentence) >= biggest_concept_lenght:
                    for k in range(0,len(sentence) - biggest_concept_lenght):
                        biggest_concept_items_cp = biggest_concept_items
                        for concept in biggest_concept_items_cp:
                            if concept not in concepts_found:
                            #Compara o conceito com os itens  de -(k + biggest_concept_lenght) até -k
                                if [i.upper() for i in concept] == [i.upper() for i in sentence[-(k + biggest_concept_lenght):-k]]:
                                    concepts_found.insert(len(concepts_found),concept)
                                    biggest_concept_items.remove(concept)

        return concepts_found
    @staticmethod
    def get_reifications(onto):#retorna a lista de uris de todas as reificações de uma ontologia carregada no ontospy

        reifications = []
        for i in onto.classes:
            if not i.children():
                reifications.insert(len(reifications),i)
        return reifications
    @staticmethod
    def add_related_concepts(parents,elem_set):#Adiciona a um conjunto de uris(nós) todos os outros nós pais relacionádos aos mesmos
 
        for i in parents:
            elem_set.update([i])
            Annotator.add_related_concepts(i.parents(),elem_set)
    @staticmethod
    def update_graph(basefile,doc_ref,annotations_concepts_uris,author):#Insere novas anotações no grafo presente em basefile ou cria um novo
     
        AO = Namespace("http://smiy.sourceforge.net/ao/rdf/associationontology.owl")
        PAV = Namespace("http://cdn.rawgit.com/pav-ontology/pav/2.0/pav.owl")
        #ANN = Namespace("https://www.w3.org/2000/10/annotation-ns#annotates")
        AOF = Namespace("http://annotation-ontology.googlecode.com/svn/trunk/annotation-foaf.owl")

        graph = Graph()
        if os.path.isfile(basefile):
            graph.parse(basefile, format="xml")
        else:
            print("Arquivo de anotações não encontrado ou ilegível.Outro será criado")
            graph.bind('aof',AOF)
            graph.bind('ao',AO)
            graph.bind('pav',PAV)

            graph.commit()

        for i in annotations_concepts_uris:
            d = Describer(graph)        
            d.rel(RDF.type,AO.Annotation)
            d.rel(AOF.annotatesDocument,doc_ref)
            d.rel(AO.hasTopic,i.uri)
            d.rel(PAV.createdOn,Literal(datetime.datetime.now(),datatype=XSD.date))
            d.rel(PAV.createdB,Literal(author))
            graph.commit()

                                    
        return graph
    @staticmethod
    def uri_to_text(uri_to_text_func,concepts):
       
        concept_dict = dict()
        for i in concepts:
            concept_dict[uri_to_text_func(i)] = i
        return concept_dict
    @staticmethod
    def zika_ontology_uri_to_text(uri):
        return str(uri).partition('#')[-1].partition('*')[0].replace('_',' ')

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
    #semanticAnnotationsPath = ChoiceArrayField(base_field=models.CharField(max_length=100),blank=True,null=True)
    #semanticAnnotationsPath = models.TextField(verbose_name=u'Path para a Anotação Semântica', max_length=50000)
    #semanticAnnotationsPath = Widget()
    semanticAnnotationsPath = ListTextField(base_field=models.CharField(max_length=300),size=100,)
    #semanticAnnotationsPath = models.ManyToManyField(models.CharField(max_length=400))
    #semanticAnnotationsPath = ListTextField(base_field=models.CharField(max_length=200),size=100)
    relatedTexts = models.TextField(verbose_name=u'URL relacionadas', max_length=50,blank=True,null=True)
    editoria = models.ManyToManyField(Editoria)
    concepts_to_annotate = set()

    a = Annotator()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-edit', args=[self.id])

    def save(self, *args, **kwargs):
        #Faz-se o seguinte por não se saber como construir um uri válido para o rdflib a partir das strings contidas em semanticAnnotationsPath
        concepts_to_annotate_list = list(self.concepts_to_annotate)
        if concepts_to_annotate_list:
            for i in concepts_to_annotate_list:
                if str(i) not in self.semanticAnnotationsPath:
                    concepts_to_annotate_list.remove(i)
        print(concepts_to_annotate_list)
        self.a.update_graph(os.path.join(PROJECT_ROOT, 'base.rdf'),self.get_absolute_url(),concepts_to_annotate_list,self.creators).serialize(format='xml',destination = os.path.join(PROJECT_ROOT, 'base.rdf'))
        semanticAnnotationsPath = [] 
        print('salvou')
        super(Artigo, self).save(*args, **kwargs)

    def annotate(self):
        onto = ontospy.Ontospy(os.path.join(PROJECT_ROOT, 'root-ontology.owl'))
        web_concepts = self.a.get_reifications(onto)
        concepts_dict = self.a.uri_to_text(self.a.zika_ontology_uri_to_text,web_concepts)
        reifications_to_annotate = [concepts_dict[' '.join(i)] for i in self.a.get_article_concepts(concepts_dict.keys(),self.text)]
        self.concepts_to_annotate.clear()
        self.a.add_related_concepts(reifications_to_annotate,self.concepts_to_annotate)
        self.semanticAnnotationsPath = [str(i) for i in list(self.concepts_to_annotate)]
        super(Artigo, self).save(update_fields=['semanticAnnotationsPath'])




