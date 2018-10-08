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
import os
import re
import time
import traceback
from wsgiref import simple_server

from spewe import exceptions
from spewe.http import status
from spewe.http import (Request, Response, ResponseNoContent)
from spewe.utils import render_template


class Settings(dict):

    def __init__(self, **kwargs):
        kwargs.setdefault('DEBUG', False)
        kwargs.setdefault('BASE_DIR', '')
        kwargs.setdefault('TEMPLATE_DIR', os.path.join(kwargs['BASE_DIR'], kwargs.get('TEMPLATE_DIR', 'templates')))
        kwargs.setdefault('STATIC_DIR', os.path.join(kwargs['BASE_DIR'], kwargs.get('STATIC_DIR', 'static')))
        self.__dict__.update(kwargs)
        super(Settings, self).__init__(self, **self.__dict__)


class Spewe(object):

    def __init__(self, settings=None):
        self.environ = None
        self.start_response = None
        self.routes = []
        if not settings:
            settings = {}
        BASE_DIR = os.path.dirname(traceback.extract_stack()[-2][0])
        settings.setdefault('BASE_DIR', BASE_DIR)
        self.settings = Settings(**settings)

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
            response = route(request, *args, **kwargs)
            if response is None:
                return ResponseNoContent()
        except (exceptions.SpeweException,) as exception:
            return Response(data=exception.args[0],
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response

    def route(self, url, methods=['GET'], name=None, template=None):
        methods = [method.lower() for method in methods]

        def add_route(func):
            route = Route(url, methods, func, name, template)
            route.app = self
            self.routes.append(route)
        return add_route


class Route(object):

    def __init__(self, url, methods, view, name=None, template=None):
        self.url = url
        self.methods = methods
        self.view = view
        self.name = name if name else view.__name__
        self.match = None
        self._template = template

    @property
    def template(self):
        return os.path.join(self.app.settings.TEMPLATE_DIR, self._template) if self._template else None

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

    def __call__(self, request, *args, **kwargs):
        if self.match:
            kwargs.update(self.match)
        if self.template:
            kwargs.setdefault('context', {'request': request})
        response = self.view(request, *args, **kwargs)
        if isinstance(response, str):
            return Response(response)
        if isinstance(response, (dict,)) and self.template:
            try:
                response_context = response
                response_context.setdefault('request', request)
                response_context.setdefault('app', self.app)
                response = Response(render_template(self.template, response))
            except (exceptions.TemplateNotFound,) as exc:
                response = Response(
                    data=exc.args[0], status_code=exc.status_code)
                return response
        return response
