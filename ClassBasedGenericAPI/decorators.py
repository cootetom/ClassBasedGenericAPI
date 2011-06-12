'''
Decorators to use on the generic class view function (get, post, put, delete)
to provide functionality specifically for an API.
'''
import base64
from datetime import timedelta, datetime

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.core.cache import cache

def throttle(limit, time_period=60*60, namespace=''):
    '''
    Throttle a view method or group of methods by limiting requests
    to the view from a single user within a time period. 
    
    Arguments:
    limit -- how many requests are allowed to this view from a single user.
    
    Keyword arguments:
    time_period -- the period of time that must elapse before the limit is reset.
                   Default is 1 hour.
    namespace -- if set then the throttle is for this namespace only and not API
                 wide. The same namespace can be used for one or many view functions.
    '''
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            request_id = request.META.get('HTTP_X_FORWARDED_FOR') or \
                         request.META.get('REMOTE_ADDR', '')
                         
            if request.user.is_authenticated():
                request_id += '_user_{0}'.format(request.user.id)
                         
            if request_id:
                key = 'api_throttle_{0}_{1}'.format(request_id, namespace)
                data = cache.get(key)
                
                if data:
                    data['count'] += 1
                    if data['expires'] > datetime.now():
                        if data['count'] > limit:
                            return HttpResponse('Request limit reached. Limit reset at {0}'.format(data['expires']), status=503)
                    else:
                        data = None
                        
                if not data:
                    data = {'expires': datetime.now() + timedelta(seconds=time_period), 
                            'count': 1
                            }
                        
                cache.set(key, data, time_period)
            
            return func(request, *args, **kwargs)
                
        return wrapper
    return view_decorator

def basic_api_login_required(func=None, realm=''):
    '''
    Check for authentication before invoking the decorated view function. 
    If the user is not already authenticated then look for a HttpBasicAuth
    string and attempt to log them in using that.
    
    Keyword arguments:
    realm -- provide the authentication realm for when asking the user for
             credentials if needed.
    '''
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated():
                return func(request, *args, **kwargs)
            else:
                # got this code from http://djangosnippets.org/snippets/243/
                if 'HTTP_AUTHORIZATION' in request.META:
                    auth = request.META['HTTP_AUTHORIZATION'].split()
                    if len(auth) == 2 and auth[0].lower() == "basic":
                        uname, passwd = base64.b64decode(auth[1]).split(':')
                        user = authenticate(username=uname, password=passwd)
                            
                        if user is not None and user.is_active:
                            login(request, user)
                            request.user = user
                            request.session.set_expiry(0)
                            return func(request, *args, **kwargs)

                # Either they did not provide an authorization header or
                # something in the authorization attempt failed. Send a 401
                # back to them to ask them to authenticate.
                response = HttpResponse()
                response.status_code = 401
                response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
                return response
        
        return wrapper
    
    if func is None:
        return view_decorator
    else:
        return view_decorator(func)
        