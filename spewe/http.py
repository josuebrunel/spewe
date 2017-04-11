# Copyright (c) 2017 <copyright holders>
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


class Request(object):

    def __init__(self, env):
        self._environ = env
        self.method = env['REQUEST_METHOD']
        self.path = env['PATH_INFO']
        self.query_string = env['QUERY_STRING']
        self.content_type = env['CONTENT_TYPE']
        self.content_length = env['CONTENT_LENGTH']
        self.server_name = env['SERVER_NAME']
        self.server_port = env['SERVER_PORT']
        self.server_protocol = env['SERVER_PROTOCOL']
        self.remote_address = env['REMOTE_ADDR']
        self.remote_host = env['REMOTE_HOST']
        # self.body = env['wsgi.input'].read()
        # if 'wsgi.file_wrapper':
        #     self.form = cgi.FieldStorage(fp=env['wsgi.input'], environ=env)
        self._wsgi = {key: value for key, value in env.items() if key.startswith('wsgi')}
        self.headers = {key: value for key, value in env.items() if key.startswith('HTTP')}

    def __str__(self):
        return '%s - %s' % (self.method, self.get_full_path())

    __repr__ = __str__

    def get_full_path(self):
        return '%s%s' % (self.server_name, self.path)

    def build_absolute_uri(self, path):
        return '%s%s' % (self.server_name, path)


class Response(object):

    def __init__(self, data='', status_code=200, **kwargs):
        self.data = data
        self.status_code = status_code
        self.headers = kwargs.get('headers', {})
        self.cookies = kwargs.get('cookies', None)

    def add_header(self, key, value):
        self.headers[key] = value

    def set_cookie(self, name, value, path='/', expire=None, httponly=None):
        pass

    def delete_cookies(self):
        pass


__all__ = [Request, Response]
