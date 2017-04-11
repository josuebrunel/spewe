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
