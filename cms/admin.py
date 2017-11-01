from django.contrib import admin
from .models import Creator, Editoria, Artigo

#def keySuggest(modeladmin, request, queryset):


class ArtigoAdmin(admin.ModelAdmin):
    list_filter = ('semanticAnnotationsPath', )
    #actions = [keySuggest]


# Register your models here.

admin.site.register(Artigo, ArtigoAdmin)
admin.site.register(Creator)
admin.site.register(Editoria)