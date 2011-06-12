'''
One mixin should exist per data type that you wish the API to support. 

Each mixin needs to support the following two methods:
    - def process_request(self, request)
    - def process_response(self, request, response, data, format)
    
The 'process_request' method must check to see if the data passed via the
request object is of the type that the mixin supports. If it is then
the mixin must parse that data into request.DATA and return the request.
If not then the method should call super.

The 'process_response' method must check to see if the given 'format' is
of the type that the mixin supports. If it is then the mixin must serialize
the 'data' into a string to response.content and return the response. If not
then the method should call super.
'''

from django.utils import simplejson
from django.http import QueryDict

class JSONMixin(object):
    '''
    Mixin to provide support for JSON request and response's.
    '''
    def process_request(self, request):
        if 'application/json' in request.META['CONTENT_TYPE'].lower():
            request.DATA = QueryDict('', mutable=True)
            request.DATA.update(simplejson.loads(request.raw_post_data))
            return request
        
        return super(JSONMixin, self).process_request(request)
    
    def process_response(self, request, response, data, format):
        if format == 'json':
            response.content = simplejson.dumps(data)
            return response
        
        return super(JSONMixin, self).process_response(request, response, data, format)
    
    
class XMLMixin(object):
    '''
    Mixin to provide support for XML request and response's.
    
    NOT IMPLEMENTED!!!
    '''
    def process_request(self, request):
        if 'application/xml' in request.META['CONTENT_TYPE'].lower():
            raise NotImplementedError
        
        return super(XMLMixin, self).process_request(request)
    
    def process_response(self, request, response, data, format):
        if format == 'xml':
            raise NotImplementedError
        
        return super(XMLMixin, self).process_response(request, response, data, format)
    
    