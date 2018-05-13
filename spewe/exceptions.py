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
    pass


class TemplateSyntaxError(TemplateError):

    error_message = 'invalid syntax:'

    def __init__(self, description):
        message = ' '.join([self.error_message, description])
        super(TemplateSyntaxError, self).__init__(message)


class TemplateContextError(TemplateError):

    error_message = '<{}> does not exist in context'

    def __init__(self, variable):
        message = self.error_message.format(variable)
        super(TemplateContextError, self).__init__(message)
