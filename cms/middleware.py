from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class SparqlMiddleware(MiddlewareMixin):

    def process_request(self, request):

        post = request.POST.copy() # to make it mutable
        #if post['semanticAnnotationsPath'][0] == '-/-':
        actual = post.get('semanticAnnotationsPath', False)
        print(actual)
        #carrega valores do sparql e atribui a value
        value = 'nada'
        post['semanticAnnotationsPath'] = value
        request.POST = post

    #def process_response(self, request, response):

