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
import os

from spewe.template import Template
from spewe.http import Response


def get_func_filename(func):
    if hasattr(func, 'func_code'):
        return func.func_code.co_filename
    return func.__code__.co_filename


def get_view_template(func_view, template_name):
    dirname = os.path.dirname(get_func_filename(func_view))
    return os.path.join(dirname, 'templates', template_name)


def render_view_template(view, template_name, context):
    template_name = get_view_template(view, template_name)
    tpl = Template(template_name)
    content = tpl.render(context)
    return Response(content)