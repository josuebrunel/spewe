# Copyright (c) 2017 Josue Kouka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import datetime
from functools import wraps
import re
import time
from wsgiref import simple_server

from spewe.exceptions import SpeweException
from spewe.http import Request, Response, status
from spewe.utils import render_view_template


class Spewe(object):

    def __init__(self):
        self.environ = None
        self.start_response = None
        self.routes = []
        self.templates = []

    def __call__(self, env, start_response):
        self.environ = env
        self.start_response = start_response
        request = Request(env)
        response = self.handle(Request(env))
        http_status_code = status.describe(response.status_code)
        response.add_header('Server', request.server_name)
        response.add_header('Date', self.gmtdate)
        self.start_response(http_status_code,
                            response.headers.items())
        return [response.data.encode('utf-8')]

    @property
    def gmtdate(self):
        gmt = time.mktime(time.gmtime())
        gmt = datetime.datetime.fromtimestamp(gmt)
        return gmt.strftime('%a, %d %b %Y %H:%M:%S GMT')

    def run(self, server_name='localhost', port=8099,
            server_class=simple_server.WSGIServer, handler_class=simple_server.WSGIRequestHandler):
        """Create a wsgi server
        """
        httpd = simple_server.make_server(server_name, port, self,
                                          server_class=server_class, handler_class=handler_class)
        print('Started http://localhost:%d/' % port)
        httpd.serve_forever()

    def handle(self, request, *args, **kwargs):
        for route in self.routes:
            if route.url_match(request):
                break
        else:
            return Response(data='Page not found', status_code=status.HTTP_404_NOT_FOUND)

        if not route.is_method_allowed(request.method):
            return Response(data='Method not allowed', status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            response = route.call_view(request, *args, **kwargs)
        except (SpeweException,) as exception:
            return Response(data=exception.status_message, status_code=exception.status_code,
                            headers=exception.headers)
        return response

    def route(self, url, methods=['GET'], name=None):
        methods = [method.lower() for method in methods]

        def add_route(func):
            self.routes.append(Route(url, methods, func, name))
        return add_route

    def template(self, name):
        def decorator(func):
            self.templates.append(name)

            @wraps(func)
            def wrapper(*args, **kwargs):
                context = {'request': args[0]}
                kwargs['context'] = context
                response = func(*args, **kwargs)
                if isinstance(response, (dict,)):
                    response = render_view_template(func, name, context)
                return response

            return wrapper

        return decorator


class Route(object):

    def __init__(self, url, methods, view, name=None):
        self.url = url
        self.methods = methods
        self.view = view
        self.name = name if name else view.__name__
        self.match = None

    def url_match(self, request):
        match = re.match(self.url, request.path)
        if not match:
            return False
        # capture url params
        if getattr(match, 'groupdict'):
            self.match = match.groupdict()
        return match

    def is_method_allowed(self, method):
        return method.lower() in self.methods

    def call_view(self, request, *args, **kwargs):
        if self.match:
            kwargs.update(self.match)
        response = self.view(request, *args, **kwargs)
        if isinstance(response, str):
            response = Response(response)
        return response
