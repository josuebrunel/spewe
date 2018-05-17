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
import cgi

try:
    from http.cookies import SimpleCookie
except (ImportError,):
    from Cookie import SimpleCookie

import json
from wsgiref.headers import Headers


HTTP_SAFE_METHODS = ['HEAD', 'GET', 'OPTIONS']


class HttpStatus(object):

    def __init__(self):
        self._statuses = {}
        try:
            from http.server import HTTPStatus
            self._statuses = {status.value: status.phrase for status in HTTPStatus}
        except (ImportError,):
            import httplib
            self._statuses = httplib.responses
        for value, phrase in self._statuses.items():
            phrase = 'HTTP_%d_%s' % (value, phrase.upper().replace(' ', '_'))
            setattr(self, phrase, value)

    def describe(self, status_code):
        return '%d %s' % (status_code, self._statuses[status_code].upper())


status = HttpStatus()


class XFormFile(object):

    def __init__(self, filename, content, content_type=None, encoding=None):
        self.filename = filename
        self.content = content.decode()
        self.content_type = content_type
        self.encoding = encoding

    def __repr__(self):
        return '<XFormFile: %s>' % self.filename


class Request(object):

    def __init__(self, env):
        self._environ = env
        self.method = env.get('REQUEST_METHOD', None)
        self.path = env.get('PATH_INFO', None)
        self.query_string = env.get('QUERY_STRING', None)
        self.content_type = env.get('CONTENT_TYPE', None)
        self.content_length = env.get('CONTENT_LENGTH', None)
        self.server_name = env.get('SERVER_NAME', None)
        self.server_port = env.get('SERVER_PORT', None)
        self.server_protocol = env.get('SERVER_PROTOCOL', None)
        self.remote_address = env.get('REMOTE_ADDR', None)
        self.remote_host = env.get('REMOTE_HOST', None)
        self.params = cgi.parse_qs(self.query_string)
        self.form = {}
        self.files = {}
        self.body = ''
        if self.method not in HTTP_SAFE_METHODS:
            self.form, self.files = self._parse_multipart()
            self.body = self._get_body()
        self.headers = Headers(
            list({key: value for key, value in env.items() if key.startswith('HTTP')}.items()))

    def __str__(self):
        return '%s - %s' % (self.method, self.get_full_path())

    __repr__ = __str__

    def _get_body(self):
        fp = self._environ['wsgi.input']
        if not fp:
            return ''
        fp.seek(0)
        body = fp.read()
        fp.seek(0)
        return body.decode()

    def _parse_multipart(self):
        form = {}
        files = {}
        if self.content_type == 'application/json':
            return form, files
        fs = cgi.FieldStorage(fp=self._environ['wsgi.input'],
                              environ=self._environ)
        for field in fs.list:
            if field.filename:
                xfile = XFormFile(field.filename, field.value, field.type,
                                  getattr(field, 'encoding', 'utf-8'))
                files.setdefault(field.name, xfile)
            else:
                form.setdefault(field.name, field.value)
        return form, files

    @property
    def json(self):
        if self.content_type == 'application/json':
            return json.loads(self.body)

    def get_full_path(self):
        return '%s%s' % (self.server_name, self.path)

    def build_absolute_uri(self, path):
        return '%s%s' % (self.server_name, path)


class BaseResponse(object):

    content_type = None
    status_code = 200

    def __init__(self, data='', status_code=None, content_type=None, **kwargs):
        self.data = data
        self.headers = Headers([])
        self.cookies = SimpleCookie()
        if status_code:
            self.status_code = status_code
        if content_type:
            self.content_type = content_type
        if self.content_type:
            self.headers.add_header('Content-Type', self.content_type)

    def add_header(self, name, value, **kwargs):
        self.headers.add_header(name, value, **kwargs)

    def set_cookie(self, name, value, path='/', expire=None, httponly=None):
        pass

    def delete_cookies(self):
        pass


class Response(BaseResponse):

    content_type = 'text/html; charset=UTF8'


class JsonResponse(BaseResponse):

    content_type = 'application/json'

    def __init__(self, data, status_code=200, **kwargs):
        data = json.dumps(data)
        super(JsonResponse, self).__init__(data, status_code=status_code, **kwargs)


class ResponseNoContent(BaseResponse):

    status_code = 204
    content_type = None


class ResponseRedirect(Response):

    status_code = 302

    def __init__(self, url):
        super(ResponseRedirect, self).__init__()
        self.add_header('Location', url)


class ResponsePermanentRedirect(ResponseRedirect):

    status_code = 301
