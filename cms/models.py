from django.db import models
from ckeditor.fields import RichTextField
import MySQLdb

# Create your models here.

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
    semanticAnnotationsPath = models.TextField(verbose_name=u'Path para a Anotação Semântica', max_length=50)
    relatedTexts = models.TextField(verbose_name=u'URL relacionadas', max_length=50)
    editoria = models.ManyToManyField(Editoria)

    def __str__(self):
        return self.title

    def annotationSuggest(self): #gera palavras chave
        chave = self.title.split()
        texto = ""
        for i in chave:
            if len(i)>3:
                texto += i +", "
        return texto

    def save(self, *args, **kwargs):
        chave = self.title.split()
        texto = ""
        for i in chave:
            if len(i) > 3:
                texto += i + "\n "

        self.semanticAnnotationsPath=texto
        super(Artigo, self).save(*args, **kwargs)



