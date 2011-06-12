from inspect import isfunction

from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from mixins import JSONMixin, XMLMixin

class APIView(JSONMixin, XMLMixin, View):
    '''
    A generic view class which holds all the functionality needed to create a
    simple REST API.
    
    Supported formats are provided by mixin's. New mixin classes that support
    new formats should by added to this class inheritance list.
    
    View functions in a class that inherits this one will receive data in
    request.DATA no matter what method was used for the request.
    '''
    
    def process_request(self, request):
        '''Return the request object with a 'DATA' attribute holding the request data.'''
        if request.method == 'GET':
            request.DATA = request.GET.copy()
        else:
            request.DATA = request.POST.copy()
            
        return super(APIView, self).process_request(request)
    
    def process_response(self, request, response, data, format):
        '''Return the response object with the correct content format.'''
        if isinstance(data, HttpResponse):
            # nothing else to do, the view function has chosen to return a
            # HttpResponse itself.
            return data
        else:
            return super(APIView, self).process_response(request, response, data, format)
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, format=None, *args, **kwargs):
        '''
        Process the request by calling each mixin's 'process_request' method.
        Invoke the correct view with the addition of request.DATA.
        Process the response by calling each minin's 'process_response' method.
        Return the response.
        '''
        # process request
        try:
            request = self.process_request(request)
        except NotImplementedError:
            return self.http_response_not_implemented(request)
        except AttributeError:
            pass
           
        # invoke view 
        response = super(APIView, self).dispatch(request, *args, **kwargs)
        while isfunction(response):
            response = response(request, *args, **kwargs)
         
        # process response
        try:
            response = self.process_response(request, HttpResponse(), response, format)
        except NotImplementedError:
            return self.http_response_not_implemented(request)
        except AttributeError:
            pass
        
        return response
    
    # ************************************************************************
    # The following class methods can be used to return all sorts of different
    # responses from a view method. They are simply handy ways of returning 
    # different response codes from your API.
    
    def http_response_status(self, request, content='', status=200):
        return HttpResponse(content, status=status)
        
    def http_response_ok(self, request, content=''):
        return self.http_response_status(request, content=content, status=200)
    
    def http_response_created(self, request, content=''):
        return self.http_response_status(request, content=content, status=201)
    
    def http_response_deleted(self, request, content=''):
        return self.http_response_status(request, content=content, status=204)
    
    def http_response_bad_request(self, request, content=''):
        return self.http_response_status(request, content=content, status=400)
    
    def http_response_forbidden(self, request, content=''):
        return self.http_response_status(request, content=content, status=401)
    
    def http_response_not_found(self, request, content=''):
        return self.http_response_status(request, content=content, status=404) 
    
    def http_response_duplicate_entry(self, request, content=''):
        return self.http_response_status(request, content=content, status=409)
    
    def http_response_not_here(self, request, content=''):
        return self.http_response_status(request, content=content, status=410)
    
    def http_response_not_implemented(self, request, content=''):
        return self.http_response_status(request, content=content, status=501)
    
    def http_response_throttled(self, request, content=''):
        return self.http_response_status(request, content=content, status=503)
    
    # ************************************************************************
    
    