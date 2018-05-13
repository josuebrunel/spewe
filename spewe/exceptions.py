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
from spewe.http import status


class SpeweException(Exception):
    pass


class Http404(SpeweException):
    status_code = status.HTTP_404_NOT_FOUND
    status_message = 'Page not found'


class PermissionDenied(SpeweException):
    status_code = status.HTTP_403_FORBIDDEN
    status_message = 'Acsess forbidden'


class MethodNotAllowed(SpeweException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    status_message = 'Method not allowed'


class TemplateError(SpeweException):

    error_message = ''

    def __init__(self, message):
        message = self.error_message.format(message)
        super(TemplateError, self).__init__(message)


class TemplateNotFound(TemplateError):
    error_message = 'template {} not found'
    status_code = 404


class TemplateSyntaxError(TemplateError):

    error_message = 'invalid syntax in statement: {}'


class TemplateContextError(TemplateError):

    error_message = '<{}> does not exist in context'


class TemplateAttributeError(TemplateError):

    error_message = '{}'
