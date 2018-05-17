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
from datetime import datetime
from bisect import bisect_left
import urllib
from urllib.parse import urlparse
import shutil
import os
import sys
import tempfile

class Annotator():

    @staticmethod
    def get_text_sentences(text):
        sentences = nltk.sent_tokenize(' '.join([i for i in text.split()]))
        return [nltk.word_tokenize(sent) for sent in sentences]

    @staticmethod
    def get_article_concepts(concept_text_list,text):#retorna lista de conceitos encontrados no texto
      
        sentences = Annotator.get_text_sentences(text)
        print("Sentences")
        print(sentences)
        concepts_found = list()
        search_remaining_concepts = [nltk.word_tokenize(i) for i in concept_text_list]
        print("Concepts")
        print(search_remaining_concepts)

        while len(search_remaining_concepts) > 0:
            biggest_concept_lenght = len(max(search_remaining_concepts,key = len))
            biggest_concept_items = [x for x in search_remaining_concepts if len(x) == biggest_concept_lenght]
            print("Maiores conceitos")
            print(biggest_concept_items)
            search_remaining_concepts = [x for x in search_remaining_concepts if x not in biggest_concept_items]
                
            for sentence in sentences:
                if len(sentence) >= biggest_concept_lenght:
                    for k in range(0,len(sentence) - biggest_concept_lenght):
                        biggest_concept_items_cp = biggest_concept_items
                        for concept in biggest_concept_items_cp:
                            if concept not in concepts_found:
                            #Compara o conceito com os itens  de -(k + biggest_concept_lenght) até -k
                                if [i.upper() for i in concept] == [i.upper() for i in sentence[-(k + biggest_concept_lenght):-k]]:
                                    print("Conceito encontrado")
                                    print(concept)
                                    print("Sentença")
                                    print(sentence)
                                    concepts_found.insert(len(concepts_found),concept)
                                    biggest_concept_items.remove(concept)

        return concepts_found
    @staticmethod
    def get_reifications(onto):#retorna a lista de uris de todas as reificações de uma ontologia carregada no ontospy
        #adicionar aqui outros tipos de uri além de classes
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
    def get_number_of_brothers(set_a,set_b,onto):
        #adicionar aqui outros tipos de uri além de classes
        onto_nodes_list_set_a = [i for i in onto.classes if str(i) in set_a]
        onto_nodes_list_set_b = [i for i in onto.classes if str(i) in set_b]
        b_parents_set = set([ j for i in onto_nodes_list_set_b for j in i.parents()])

        brother_count = 0
        for c in onto_nodes_list_set_a:
            p = set(c.parents())
            if p.issubset(b_parents_set):
                brother_count += 1
        return(brother_count)
    #retorna o numero de conceitos irmãos não filhos da raiz
        
             
    @staticmethod
    def update_graph(basefile,doc_ref,annotations_concepts_uris,author):#Insere novas anotações no grafo presente em basefile ou cria um novo
     
        AO = Namespace("http://purl.org/ao/core/")
        PAV = Namespace("http://cdn.rawgit.com/pav-ontology/pav/2.0/pav.owl")
        #ANN = Namespace("https://www.w3.org/2000/10/annotation-ns#annotates")
        AOF = Namespace("http://purl.org/ao/foaf/")

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
            d.rel(AO.hasTopic,i)
            d.rel(PAV.createdOn,Literal(datetime.now(),datatype=XSD.date))
            for i in author:
                d.rel(PAV.createdB,Literal(i))
                
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
