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
import sys

STATUS_DIC = {
    100: 'HTTP_100_CONTINUE',
    101: 'HTTP_101_SWITCHING_PROTOCOLS',
    200: 'HTTP_200_OK',
    201: 'HTTP_201_CREATED',
    202: 'HTTP_202_ACCEPTED',
    203: 'HTTP_203_NON_AUTHORITATIVE_INFORMATION',
    204: 'HTTP_204_NO_CONTENT',
    205: 'HTTP_205_RESET_CONTENT',
    206: 'HTTP_206_PARTIAL_CONTENT',
    300: 'HTTP_300_MULTIPLE_CHOICES',
    301: 'HTTP_301_MOVED_PERMANENTLY',
    302: 'HTTP_302_FOUND',
    303: 'HTTP_303_SEE_OTHER',
    304: 'HTTP_304_NOT_MODIFIED',
    305: 'HTTP_305_USE_PROXY',
    306: 'HTTP_306_RESERVED',
    307: 'HTTP_307_TEMPORARY_REDIRECT',
    400: 'HTTP_400_BAD_REQUEST',
    401: 'HTTP_401_UNAUTHORIZED',
    402: 'HTTP_402_PAYMENT_REQUIRED',
    403: 'HTTP_403_FORBIDDEN',
    404: 'HTTP_404_NOT_FOUND',
    405: 'HTTP_405_METHOD_NOT_ALLOWED',
    406: 'HTTP_406_NOT_ACCEPTABLE',
    407: 'HTTP_407_PROXY_AUTHENTICATION_REQUIRED',
    408: 'HTTP_408_REQUEST_TIMEOUT',
    409: 'HTTP_409_CONFLICT',
    410: 'HTTP_410_GONE',
    411: 'HTTP_411_LENGTH_REQUIRED',
    412: 'HTTP_412_PRECONDITION_FAILED',
    413: 'HTTP_413_REQUEST_ENTITY_TOO_LARGE',
    414: 'HTTP_414_REQUEST_URI_TOO_LONG',
    415: 'HTTP_415_UNSUPPORTED_MEDIA_TYPE',
    416: 'HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE',
    417: 'HTTP_417_EXPECTATION_FAILED',
    418: 'HTTP_418_I_AM_A_TEAPOT',
    428: 'HTTP_428_PRECONDITION_REQUIRED',
    429: 'HTTP_429_TOO_MANY_REQUESTS',
    431: 'HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE',
    500: 'HTTP_500_INTERNAL_SERVER_ERROR',
    501: 'HTTP_501_NOT_IMPLEMENTED',
    502: 'HTTP_502_BAD_GATEWAY',
    503: 'HTTP_503_SERVICE_UNAVAILABLE',
    504: 'HTTP_504_GATEWAY_TIMEOUT',
    505: 'HTTP_505_HTTP_VERSION_NOT_SUPPORTED',
    511: 'HTTP_511_NETWORK_AUTHENTICATION_REQUIRED'
}


def describe(status_code):
    status = STATUS_DIC[int(status_code)].replace('HTTP', '')
    status = '%s' % status.replace('_', ' ').strip()
    return status


for status_code, text in STATUS_DIC.items():
    setattr(sys.modules[__name__], text, status_code)
